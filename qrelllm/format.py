import pandas as pd


def clean_json(s: str) -> str:
    return (
        s.removeprefix(" ")
        .removeprefix("```json")
        .removeprefix("```JSON")
        .removesuffix("```")
        .replace("\n", "")
        .replace(" ", "")
    )


def format_test_collection(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index()
    df.rename(columns={"index": "doc_id"}, inplace=True)
    df["doc_id"] = df["doc_id"].astype(str)
    return df[["doc_id", "query", "title", "rel", "reason"]]
