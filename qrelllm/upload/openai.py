import io
import json

import gokart
import luigi
from google.cloud import storage
from openai import OpenAI
from tqdm import tqdm


class UploadOpenAI(gokart.TaskOnKart):
    """
    batchで投げるためのpromptを作成してアップロード。主にOpenAI用
    """

    queries: list[str] = gokart.TaskInstanceParameter()

    def run(self):
        client = OpenAI()
        queries = self.load("queries")
        model_name = "gpt-3.5-turbo"

        with open("data/prompts_openai.jsonl", "rb") as f:
            for i, q in enumerate(tqdm(queries)):
                q = q.replace("\n", "")
                if q == "query":
                    continue
                content = f"""「{q}」という医療系の検索クエリに関係のある記事タイトルと関係のない記事タイトルを複数作成し、クエリとの関連度を0~2の3段階で付与してください。2が最も関連度が高いものとします。関連度0はクエリと全く関係のないタイトル、関連度1は直接の関連はないが部分的、または間接的に関係のあるタイトル、関連度2はクエリと直接関係のあるタイトルとします。最大で8個作成してください。関連度は0,1,2全てのパターンが必ず出現するようにしてください。結果は次のようなkeyを持つJSON形式で提出してください。query:クエリの内容,title:クエリと関連のある記事タイトル,score:関連度(0~2),reason:scoreの理由"""
                prompt = {
                    "custom_id": f"prompt{i}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": "あなたはクエリとドキュメントの関連度を紐づけるのを助けるアシスタントです",
                            },
                            {"role": "user", "content": content},
                        ],
                    },
                }

                json_str = json.dumps(prompt, ensure_ascii=False)
                f.write(json_str)
                f.write("\n")

            file_response = client.files.create(file=f, purpose="batch")
            self.dump({"dist": file_response.id})
