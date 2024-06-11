import boto3
import re
from ..jobs_helpers.extract_pdf_file import PdfExtractor
s3_client = boto3.client('s3')

class PdfBatchExtractor:
    def __init__(self, input_bucket, output_bucket):
        self.input_bucket = input_bucket
        self.output_bucket = output_bucket
        
    def process_pdf_bucket(self):
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.input_bucket):
            for content in page.get('Contents', []):
                pdf_key = content['Key']
                if pdf_key.endswith('.pdf'):
                    input_folder, input_prefix, pdf_name = self.extract_file_details(pdf_key)
                    pdf_extractor = PdfExtractor(pdf_name, input_prefix, input_folder, self.input_bucket, self.output_bucket)
                    pdf_extractor.extract_data()

        
    @staticmethod
    def extract_file_details(key):
        """
        Extracts specific parts of the given path and returns them as a list.

        Parameters:
        path (str): The path string from which to extract elements.

        Returns:
        list: A list containing the desired elements.
        """
        parts = key.split('/')
        input_folder = parts[0]
        input_prefix = '/'.join(parts[1:3])
        pdf_name = re.sub(r'\.pdf$', '', parts[-1])
        return input_folder, input_prefix, pdf_name
    
if __name__ == "__main__":
    INPUT_BUCKET = 'sample-design-documents'
    OUTPUT_BUCKET = 'sample-extracted-design-documents'
    extractor = PdfBatchExtractor(INPUT_BUCKET, OUTPUT_BUCKET)
    extractor.process_pdf_bucket(folder_prefix)
        