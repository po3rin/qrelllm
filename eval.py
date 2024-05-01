import pandas as pd
from elasticsearch import Elasticsearch
from tqdm import tqdm

from qrelllm.eval import ndcg_compare_report


def load_test_collection(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df = df.reset_index()
    df.rename(columns={"index": "doc_id"}, inplace=True)
    df["doc_id"] = df["doc_id"].astype(str)
    return df[["doc_id", "query", "title", "rel", "reason"]]


def ping(client: Elasticsearch) -> None:
    if not client.ping():
        raise Exception("Elasticsearch is not running.")


def index(client: Elasticsearch, df: pd.DataFrame) -> None:
    df = df.sample(frac =1)
    docs = df.to_dict(orient="records")
    for d in tqdm(docs):
        try:
            client.index(
                index="docs",
                body=d,
                id=d["doc_id"],
                pipeline="japanese-text-embeddings",
            )
        except Exception as e:
            print(e)
            print(d)
            raise e


def run_with_ngram(
    client: Elasticsearch, index_name: str, df: pd.DataFrame
) -> pd.DataFrame:
    queries = df["query"].drop_duplicates().tolist()

    results = []
    for q in tqdm(queries):
        result = client.search(
            index=index_name,
            body={
                "_source": {
                    "includes": ["doc_id", "query", "title", "rel", "reason"]
                },
                "query": {
                    "bool": {
                        "should": {"match": {"title.ngram": q}},
                        "filter": {"match": {"query": q}},
                    }
                },
            },
        )
        results.extend(
            [r["_source"] | {"rel": r["_rel"]} for r in result["hits"]["hits"]]
        )

    return pd.DataFrame(results)

def run_with_kuromoji(
    client: Elasticsearch, index_name: str, df: pd.DataFrame
) -> pd.DataFrame:
    queries = df["query"].drop_duplicates().tolist()

    results = []
    for q in tqdm(queries):
        result = client.search(
            index=index_name,
            body={
                "_source": {
                    "includes": ["doc_id", "query", "title", "rel", "reason"]
                },
                "query": {
                    "bool": {
                        "should": {"match": {"title": q}},
                        "filter": {"match": {"query": q}},
                    }
                },
            },
        )
        results.extend(
            [r["_source"] | {"rel": r["_rel"]} for r in result["hits"]["hits"]]
        )

    return pd.DataFrame(results)


def run_with_semantic(
    client: Elasticsearch, index_name: str, df: pd.DataFrame
) -> pd.DataFrame:
    queries = df["query"].drop_duplicates().tolist()

    results = []
    for q in tqdm(queries):
        result = client.search(
            index=index_name,
            body={
                "_source": {
                    "includes": ["doc_id", "query", "title", "rel", "reason"]
                },
                "query": {
                    "bool": {
                        "should": {"match": {"title": q}},
                        "filter": {"match": {"query": q}},
                    }
                },
                "knn": {
                    "field": "text_embedding.predicted_value",
                    "k": 10,
                    "num_candidates": 50,
                    "query_vector_builder": {
                        "text_embedding": {
                            "model_id": "cl-tohoku__bert-base-japanese-v2",
                            "model_text": q,
                        }
                    },
                    "filter": {"bool": {"filter": {"match": {"query": q}}}},
                },
            },
        )
        results.extend(
            [r["_source"] | {"rel": r["_rel"]} for r in result["hits"]["hits"]]
        )

    return pd.DataFrame(results)


def main():
    index_name = "docs"
    client = Elasticsearch(hosts=["http://localhost:9200"])

    ping(client)

    df = load_test_collection("data/dataset_vertex.csv")

    index(client, df)

    run1_df = run_with_ngram(client, index_name, df)
    run2_df = run_with_kuromoji(client, index_name, df)

    ndcg_compare_report(df, run1_df, run2_df)


if __name__ == "__main__":
    main()
