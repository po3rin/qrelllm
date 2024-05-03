import gokart
import luigi
import json
import random
import vertexai
from tqdm import tqdm
import pandas as pd
from vertexai.language_models import TextGenerationModel

from qrelllm.llm.prompt import gen_doc_rel_prompt
from qrelllm.format import clean_json


class GenerateTestCollectionWithVertexAIBatch(gokart.TaskOnKart):
    """
    テストコレクションの作成
    """

    project: str = luigi.Parameter()
    location: str = luigi.Parameter()
    destination_uri_prefix: str = luigi.Parameter()
    upload_task: dict = gokart.TaskInstanceParameter()

    def run(self):
        upload = self.load("upload_task")
        vertexai.init(project=self.project, location=self.location)
        parameters = {
            "temperature": 1,
            "max_output_tokens": 10000,
            "top_p": 0.95,
            "top_k": 40,
        }
        model = TextGenerationModel.from_pretrained("text-bison")

        batch_prediction_job = model.batch_predict(
            dataset=upload["dist"],
            destination_uri_prefix=self.destination_uri_prefix,
            model_parameters=parameters,
        )

        batch_prediction_job.wait_for_resource_creation()
        self.dump("done")


class TestCollection(gokart.TaskOnKart):
    """
    与えられたクエリに関連する記事タイトルと関連のない記事タイトルを生成するタスク
    """

    project: str = luigi.Parameter()
    location: str = luigi.Parameter()
    size: int = luigi.IntParameter(default=10)
    queries = gokart.TaskInstanceParameter()

    def run(self):
        vertexai.init(project=self.project, location=self.location)
        parameters = {
            "temperature": 1.0,
            "max_output_tokens": 1000,
            "top_p": 0.95,
            "top_k": 40,
        }

        model = TextGenerationModel.from_pretrained("text-bison@002")

        queries = self.load("queries")
        queries = random.sample(queries, self.size)

        results = []
        errors = []
        for q in tqdm(queries):
            response = model.predict(
                gen_doc_rel_prompt(q),
                **parameters,
            )

            json_str = clean_json(response.text)
            try:
                result = json.loads(json_str)
            except Exception as e:
                errors.append(json_str)
                continue
            results.extend(result)

        df = pd.DataFrame(results)
        print(f"{len(errors)} errors")
        self.dump(df)
