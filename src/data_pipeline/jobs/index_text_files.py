import boto3
import os

# Create an S3 client
s3 = boto3.client('s3')
bucket_name = 'sample-extracted-design-documents'

def index_files_text(category, bucket_name):
    """
    Download all 'combined_text.txt' files from the specified S3 bucket.
    """
    # List objects within a given prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=category)
    if 'Contents' in response:
        for item in response['Contents']:
            key = item['Key']
            if key.endswith('combined_text.txt'):
                _, depot, year, design_id = key.split('/')[:4] 
                file_obj = s3.get_object(Bucket=f'{bucket_name}', Key=f'{key}')
                file_content = file_obj['Body'].read().decode('utf-8')
                processed_content = ''.join([line for line in file_content.splitlines() if line.strip()])
                client.index(index=f'{category}_text', document={'description':processed_content.lower(), 
                                                     'path': f"s3://{bucket_name}/{key}", 
                                                     'category': category.lower(),
                                                     'depot': depot,
                                                     'country': depot,
                                                     'year': year,
                                                     'design_id': design_id 
                                                    })

categories = ['bottles', 'writing_instrument', 'watches', 'jewellery']
for category in categories:
    index_files_text(category, bucket_name)