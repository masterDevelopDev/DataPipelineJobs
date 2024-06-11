from elasticsearch import Elasticsearch

class ElasticTextIndexCreator:
    def __init__(self, client):
        self.client = client

    def create_index(self, index_name, settings, mappings):
        """
        Create an index in Elasticsearch with the given settings and mappings.
        """
        if self.client.indices.exists(index=index_name):
            print(f"Index '{index_name}' already exists.")
            return

        body = {
            "settings": settings,
            "mappings": mappings
        }
        try:
            self.client.indices.create(index=index_name, body=body)
            print(f"Index '{index_name}' created successfully.")
        except Exception as e:
            print(f"Error creating index '{index_name}': {e}")

# Usage
if __name__ == "__main__":
    index_creator = ElasticTextIndexCreator(client)

    # Common settings and mappings for the indices
    request_body = {
        "settings": {
            "number_of_shards": 6,
            "number_of_replicas": 3
        },
        "mappings": {
            "properties": {"description": {"type": "text"}, 
                           "path": {"type": "text"}, 
                           "category": {"type": "text"}, 
                           "depot": {"type": "text"}, 
                           "country": {"type": "text"}, 
                           "year": {"type": "text"}, 
                           "design_id": {"type": "keyword"}
                          }
        }
    }



# List of indices to be created
indices = ['bottles_text', 'writing_instrument_text', 'watches_text', 'jewellery_text']

for index in indices:
    index_creator.create_index(index, **request_body)