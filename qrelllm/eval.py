import pandas as pd
from ranx import Qrels, Run, compare


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
