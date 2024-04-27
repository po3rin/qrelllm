import json
import os

import gokart
import luigi
import pandas as pd
import vertexai
from vertexai.language_models import TextGenerationModel

project = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
location = os.getenv("GOOGLE_CLOUD_LOCATION")


class SearchQueries(gokart.TaskOnKart):
    """
    医療系のクエリを生成するタスク
    """

    size: int = luigi.IntParameter(default=10)
    chunk: int = luigi.IntParameter(default=10)

    def run(self):
        vertexai.init(project=project, location=location)
        parameters = {
            "temperature": 0.5,
            "max_output_tokens": 1000,
            "top_p": 0.8,
            "top_k": 40,
        }

        model = TextGenerationModel.from_pretrained("text-bison@002")

        results = []
        for i in range(int(self.size / self.chunk) + 1):
            response = model.predict(
                f"""
                医療系の検索クエリを{self.chunk}個作成してください。
                結果は、以下のようなJSON形式で提出してください。

                [{{"query": "クエリの内容1"}},{{"query": "クエリの内容2"}}]
                """,
                **parameters,
            )

            json_str = (
                response.text.removeprefix(" ")
                .removeprefix("```json")
                .removeprefix("```JSON")
                .removesuffix("```")
                .replace("\n", "")
                .replace(" ", "")
            )
            try:
                result = json.loads(json_str)
            except Exception as e:
                print(json_str)
                raise e
            results.extend(result)

        df = pd.DataFrame(results)
        self.dump(df)


class LoadQueries(gokart.TaskOnKart):
    """
    fileからクエリをロードする
    """

    csv_file_path: str = luigi.Parameter()

    def run(self):
        with open(self.csv_file_path, "r") as f:
            queries = [line for line in f.readlines()]
            self.dump(queries)
