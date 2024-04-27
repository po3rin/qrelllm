import gokart
import luigi
from google.cloud import storage


class DownloadFromGCS(gokart.TaskOnKart):
    bucket_name: str = luigi.Parameter()
    source_blob_name: str = luigi.Parameter()
    destination_file_name: str = luigi.Parameter()

    def run(self):
        storage_client = storage.Client()

        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(self.source_blob_name)
        blob.download_to_filename(self.destination_file_name)

        self.dump("done")
