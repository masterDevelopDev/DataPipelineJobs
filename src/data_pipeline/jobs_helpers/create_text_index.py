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