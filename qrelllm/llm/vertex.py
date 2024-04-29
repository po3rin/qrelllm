import gokart
import luigi
import vertexai
from vertexai.language_models import TextGenerationModel


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
