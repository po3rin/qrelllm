import gokart

from qrelllm.queries import SearchQueries


def main():
    df = gokart.build(SearchQueries(size=200))
    df.to_csv("data/generated_queries.csv", index=False)


if __name__ == "__main__":
    main()
