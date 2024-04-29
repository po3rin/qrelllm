import gokart
import luigi
from openai import OpenAI


class GenerateTestCollectionWithOpenAIBatch(gokart.TaskOnKart):
    """
    与えられたクエリに関連する記事タイトルと関連のない記事タイトルを生成するタスク
    """

    upload_task: int = gokart.TaskInstanceParameter()

    def run(self):
        client = OpenAI()
        upload_task = self.load("upload_task")
        input_file_id = upload_task["input_file_id"]
        results = []
        batch = client.batches.create(
            completion_window="24h",
            endpoint="/v1/chat/completions",
            input_file_id=input_file_id,
        )

        with client.batches.with_streaming_response.retrieve(
            batch.id,
        ) as response:
            batch = response.parse()
            self.dump(batch)
