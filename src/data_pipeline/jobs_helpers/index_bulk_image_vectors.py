from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging

class BulkIndexer:
    def __init__(self, client):
        self.client = client

    def create_bulk_data(self, feature_vectors, image_paths):
        for vector, path in zip(feature_vectors, image_paths):
            category = path.split('/')[3]
            yield {
                "_index": f'{category}_images',
                "_id": path,
                "_source": {
                    "image_embedding": vector,  
                    "image_path": path
                }
            }

    def perform_bulk_indexing(self, feature_vectors, image_paths):
        list_feature_vectors = feature_vectors.tolist()
        bulk_data = self.create_bulk_data(list_feature_vectors, image_paths)
        success, failed = bulk(self.client, bulk_data, raise_on_error=False)
        logging.info(f"Bulk indexing completed: {success} succeeded, {failed} failed.")
