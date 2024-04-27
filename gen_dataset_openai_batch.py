import gokart

from qrelllm.llm.openai import GenerateTestCollectionWithOpenAI
from qrelllm.queries import LoadQueries
from qrelllm.upload.openai import UploadOpenAI


def main():
    queries = LoadQueries(csv_file_path="data/queries.csv")
    upload = UploadOpenAI(queries=queries)
    gokart.build(GenerateTestCollectionWithOpenAI(input_file_id=upload))


if __name__ == "__main__":
    main()
