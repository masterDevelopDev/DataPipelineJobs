class ElasticSearchIndexManager:
    def __init__(self, client, index_name, embedding_dimension):
        self.client = client
        self.index_name = index_name
        self.embedding_dimension = embedding_dimension

    def create_index(self, number_of_shards=6, number_of_replicas=3):
        vector_dims = self.embedding_dimension
        request_body = {
            "settings" : {
                "number_of_shards": number_of_shards,
                "number_of_replicas": number_of_replicas
            },
            "mappings": {
                "properties": {
                    "image_embedding": {
                        "type": "dense_vector",
                        "dims": vector_dims,
                        "index": True,
                        "similarity": "cosine"
                    },
                }
            }
        }
        self.client.indices.create(index=self.index_name, body=request_body)
