import boto3

# Initialize a session using Amazon S3
s3 = boto3.client('s3')

class S3ImagePathsFetcher:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        
    def get_image_paths(self):
        all_images_paths = []
        bucket_name = 'sample-extracted-design-documents'
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket_name):
            for content in page.get('Contents', []):
                file_key = content['Key']
                if file_key.endswith('.jpg'):
                    all_images_paths.append(f"s3://{self.bucket_name}/{file_key}")
        return all_images_paths
        