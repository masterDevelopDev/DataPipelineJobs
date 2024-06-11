from PIL import Image
import io
import boto3
import numpy as np
import torch

s3_client = boto3.client('s3')

class S3ImageProcessor:
    def __init__(self, bucket_name, preprocess, batch_size=32):
        self.bucket_name = bucket_name
        self.preprocess = preprocess
        self.batch_size = batch_size

    def download_image(self, s3_uri):
        s3_object_key = s3_uri.split(f'{self.bucket_name}/')[-1]
        file_byte_string = s3_client.get_object(Bucket=self.bucket_name, Key=s3_object_key)['Body'].read()
        image = Image.open(io.BytesIO(file_byte_string)).convert("RGB")
        return image

    def process_images_batch(self, list_images_paths):
        list_preprocessed_images = []
        # Process images in batches
        for i in range(0, len(list_images_paths), self.batch_size):
            batch_paths = list_images_paths[i:i + self.batch_size]
            batch_images = [self.download_image(path) for path in batch_paths]
            batch_preprocessed_images = [self.preprocess(image) for image in batch_images]
            list_preprocessed_images.extend(batch_preprocessed_images)
        # Convert the list of images to a tensor
        preprocessed_images_input = torch.tensor(np.stack(list_preprocessed_images))
        return preprocessed_images_input
