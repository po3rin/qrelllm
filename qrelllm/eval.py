import gokart
import pandas as pd
from ranx import Qrels, Run, compare
from sklearn.metrics import cohen_kappa_score


def ndcg_compare_report(qrels_df: pd.DataFrame, *args: pd.DataFrame):
    qrels = Qrels.from_df(
        df=qrels_df,
        q_id_col="query",
        doc_id_col="doc_id",
        score_col="rel",
    )

    runs = [
        Run.from_df(
            df=df,
            q_id_col="query",
            doc_id_col="doc_id",
            score_col="rel",
        )
        for df in list(args)
    ]

    report = compare(
        qrels=qrels,
        runs=runs,
        metrics=["ndcg@10"],
        max_p=0.05,
        make_comparable=True
    )
    return report


class CohenKappa(gokart.TaskOnKart):
    testcollection_a = gokart.TaskInstanceParameter()
    testcollection_b = gokart.TaskInstanceParameter()

    def run(self):
        a_df = self.load_data_frame(
            "testcollection_a", required_columns={"query", "title", "rel"}
        )
        b_df = self.load_data_frame(
            "testcollection_b", required_columns={"query", "title", "rel"}
        )

        # queryとtitleが二つのデータフレームで重複しているものに絞る
        a_df = a_df[
            a_df["query"].isin(b_df["query"]) & a_df["title"].isin(b_df["title"])
        ]
        b_df = b_df[
            b_df["query"].isin(a_df["query"]) & b_df["title"].isin(a_df["title"])
        ]

        df = pd.merge(a_df, b_df, on=["query", "title"], how="inner")
        rels_a = df["rel_x"].astype(int).tolist()
        rels_b = df["rel_y"].astype(int).tolist()

        if len(rels_a) != len(rels_b):
            raise ValueError(f"unmatched length. a: {len(rels_a)}, b: {len(rels_b)}")

        if len(rels_a) == 0:
            raise ValueError("length: 0")

        result = cohen_kappa_score(rels_a, rels_b, weights="quadratic")
        self.dump({"result": result})
