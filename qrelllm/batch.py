import random

import gokart
import luigi
from tqdm import tqdm


class GeneratePromptsBatch(gokart.TaskOnKart):
    """
    batchで投げるためのpromptを作成する
    """

    size: int = luigi.IntParameter(default=10)
    queries: list[str] = luigi.ListParameter()

    def run(self):
        queries = self.queries
        queries = random.sample(queries, self.size)

        prompts: list[str] = []
        for q in tqdm(queries):
            prompts = prompts.append(
                f"""「{q}」という医療系の検索クエリに関係のある記事タイトルと関係のない記事タイトルを複数作成し、クエリとの関連度を0~2の3段階で付与してください。2が最も関連度が高いものとします。関連度0はクエリと全く関係のないタイトル、関連度1は直接の関連はないが部分的、または間接的に関係のあるタイトル、関連度2はクエリと直接関係のあるタイトルとします。最大で8個作成してください。関連度は0,1,2全てのパターンが必ず出現するようにしてください。結果は次のようなkeyを持つJSON形式で提出してください。query: クエリの内容,title: クエリと関連のある記事タイトル,rel: 関連度(0~2),reason": "relの理由"""
            )

        self.dump(prompts)
