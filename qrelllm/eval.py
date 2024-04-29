import pandas as pd
import gokart
from ranx import Qrels, Run, compare
from sklearn.metrics import cohen_kappa_score


def ndcg_compare_report(
    qrels_df: pd.DataFrame, *args: pd.DataFrame
):
    qrels = Qrels.from_df(
        df=qrels_df,
        q_id_col="query",
        doc_id_col="doc_id",
        score_col="score",
    )

    runs = [Run.from_df(
        df=df,
        q_id_col="query",
        doc_id_col="doc_id",
        score_col="score",
    ) for df in list(args)]

    report = compare(qrels=qrels, runs=runs, metrics=["ndcg@10"], max_p=0.05)

    print(report)


class CohenKappa(gokart.TaskOnKart):
    testcollection_a = gokart.TaskInstanceParameter()
    testcollection_b = gokart.TaskInstanceParameter()

    def run(self):
        a_df = self.load_data_frame('testcollection_a', required_columns={'query', 'title', 'score'})
        b_df = self.load_data_frame('testcollection_b', required_columns={'query', 'title', 'score'})

        a_df.sort_values(['query', 'title'], inplace=True)
        b_df.sort_values(['query', 'title'], inplace=True)

        # queryとtitleが二つのデータフレームで重複しているものに絞る
        a_df = a_df[a_df['query'].isin(b_df['query'])]
        a_df = a_df[a_df['title'].isin(b_df['title'])]
        b_df = b_df[b_df['query'].isin(a_df['query'])]
        b_df = b_df[b_df['title'].isin(a_df['title'])]

        rels_a = a_df['score'].to_list()
        rels_b = a_df['score'].to_list()

        if len(rels_a) != len(rels_b):
            raise ValueError('unmatched length')
        
        if len(rels_a) == 0:
            raise ValueError('length: 0')

        result = cohen_kappa_score(rels_a, rels_b)
        self.dump(result)
