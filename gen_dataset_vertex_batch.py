import os

import gokart

from qrelllm.llm.vertex import GenerateTestCollectionWithVertexAI
from qrelllm.queries import LoadQueries
from qrelllm.upload.gcs import UploadBatchForGCS

project = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
location = os.getenv("GOOGLE_CLOUD_LOCATION")


def main():
    bucket_name = "llm-testcollection"

    queries = LoadQueries(csv_file_path="data/queries.csv")
    upload_task = UploadBatchForGCS(
        queries=queries,
        bucket_name=bucket_name,
        destination_blob_name="prompt/prompts.jsonl",
    )
    generate_search_dataset_task = GenerateTestCollectionWithVertexAI(
        project=project,
        location=location,
        destination_uri_prefix=f"gs://{bucket_name}/result",
        upload_task=upload_task,
    )
    gokart.build(generate_search_dataset_task)


if __name__ == "__main__":
    main()
