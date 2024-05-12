import json
import gokart
import luigi
import pandas as pd
from tqdm import tqdm
from openai import OpenAI

from qrelllm.format import clean_json
from qrelllm.llm.prompt import gen_rel_prompt


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


class RelDecision(gokart.TaskOnKart):
    """
    与えられたクエリと記事タイトルに適合度を付与
    """

    testcollection = gokart.TaskInstanceParameter()
    _version: int = luigi.Parameter(default=1)

    def run(self):
        df = self.load_data_frame(required_columns={"query", "title"})

        client = OpenAI()

        df = df.groupby("query")["title"].apply(list) \
            .reset_index(name="titles")
        d = dict(zip(df["query"], df["titles"]))

        results = []
        errors = []
        for k, v in tqdm(d.items()):
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": gen_rel_prompt(k, v)
                    }
                ]
            )

            md_str = completion.choices[0].message.content
            
            json_str = clean_json(md_str)
            try:
                result = json.loads(json_str)
            except Exception as e:
                errors.append(json_str)
                continue
            results.extend(result)

        df = pd.DataFrame(results)
        print(f"{len(errors)} errors")
        self.dump(df)

