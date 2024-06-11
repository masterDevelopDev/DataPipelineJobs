import boto3
import clip
from elasticsearch import Elasticsearch
from DataPipelineJobs.src.data_pipeline.jobs_helpers.retrieve_image_paths import S3ImagePathsFetcher
from DataPipelineJobs.src.data_pipeline.jobs_helpers.download_process_images import S3ImageProcessor
from DataPipelineJobs.src.data_pipeline.jobs_helpers.embed_images import ImageEmbedder
from DataPipelineJobs.src.data_pipeline.jobs_helpers.create_images_index import ElasticSearchIndexManager
from DataPipelineJobs.src.data_pipeline.jobs_helpers.index_bulk_image_vectors import BulkIndexer

class DataPipeline:
    def __init__(self, s3_client, es_client, model, preprocess, bucket_name, list_image_indexes):
        self.s3_client = s3_client
        self.es_client = es_client
        self.model = model
        self.preprocess = preprocess
        self.bucket_name = bucket_name
        self.list_image_indexes = list_image_indexes
        self.embedding_dimension = model.ln_final.normalized_shape[0]

    def create_indices(self):
        for index_image in self.list_image_indexes:
            index_creator = ElasticSearchIndexManager(self.es_client, index_image, self.embedding_dimension)
            index_creator.create_index()

    def process_images(self):
        images_fetcher = S3ImagePathsFetcher(self.bucket_name)
        all_images = images_fetcher.get_image_paths()
        s3_image_processor = S3ImageProcessor(self.bucket_name, self.preprocess)
        preprocessed_images_input = s3_image_processor.process_images_batch(all_images)
        return preprocessed_images_input, all_images

    def embed_images(self, preprocessed_images_input):
        image_embedder = ImageEmbedder(self.model)
        features = image_embedder.generate_image_embeddings(preprocessed_images_input)
        return features

    def index_images(self, features, all_images):
        bulk_indexer = BulkIndexer(self.es_client)
        bulk_indexer.perform_bulk_indexing(features, all_images)

    def run(self):
        self.create_indices()
        preprocessed_images_input, all_images = self.process_images()
        features = self.embed_images(preprocessed_images_input)
        self.index_images(features, all_images)

if __name__ == "__main__":
    s3 = boto3.client('s3')
    model, preprocess = clip.load('ViT-B/16')

    ELASTIC_PASSWORD = "XXXXXXXXXXXX"
    CLOUD_ID = "XXXXXXXXXXXXXXXX"

    client = Elasticsearch(
        cloud_id=CLOUD_ID,
        basic_auth=("elastic", ELASTIC_PASSWORD)
    )

    bucket_name = 'your-bucket-name'
    list_image_indexes = ['bottles_images', 'watches_images', 'writing-intrument_images', 'jewellery_images']

    pipeline = DataPipeline(s3, client, model, preprocess, bucket_name, list_image_indexes)
    pipeline.run()
