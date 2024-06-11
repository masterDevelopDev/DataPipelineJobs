import boto3
import fitz  # PyMuPDF
import io
from io import BytesIO
import os
import numpy as np
from PIL import Image, ImageCms
import easyocr
import pypdf
import logging
from ...constants import EXTRACTED_TEXT_FROM_IMAGE, EXTRACTED_TEXT_FROM_PDF, COMBINED_TEXT, THRESHOLD_WHITE_PIXEL, \
    THRESHOLD_BLACK_PIXEL
from ..utils.clean_text import *

# Configure the logger
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

s3_client = boto3.client('s3')

reader = easyocr.Reader(['en', 'ch_sim'])

class PdfExtractor:
    def __init__(self, pdf_name, input_prefix, input_folder, input_bucket, output_bucket):
        LOG.info("Initializing PdfExtractor")
        self.pdf_name = pdf_name
        self.input_prefix = input_prefix
        self.input_folder = input_folder
        self.input_bucket = input_bucket
        self.output_bucket = output_bucket
        self.output_prefix = f'{input_folder}/{input_prefix}'

    def extract_data(self):
        """
        This is the main method of the class. This extracts the image and the text contained in a .pdf file
        and saves them in a separate folder.
        """
        try:
            PdfExtractor.extract_images_text_from_pdf(self.pdf_name, self.input_prefix, self.input_folder, self.input_bucket, 
                                                  self.output_bucket, self.output_prefix)
            PdfExtractor.concatenate_text_files_s3(self.output_bucket, self.pdf_name, self.output_prefix)
        except Exception as e:
            print(f"An error occurred: {e} - the file located in s3://{self.input_bucket}/{self.input_folder}/{self.input_prefix}/{self.pdf_name}.pdf has not been processed.")


    @staticmethod
    def extract_images_text_from_pdf(pdf_name, input_prefix, input_folder, input_bucket, output_bucket, output_prefix):
        # Create a byte stream object to download the PDF into memory
        pdf_stream = io.BytesIO()
        s3_client.download_fileobj(Bucket=input_bucket, Key=f'{input_folder}/{input_prefix}/{pdf_name}.pdf', Fileobj=pdf_stream)
        pdf_stream.seek(0)  # Go to the start of the stream
        print(f"{output_bucket}/{output_prefix}/{pdf_name}.pdf")
        PdfExtractor.extract_text_from_pdf(pdf_name, pdf_stream, output_bucket, output_prefix)
        # Open the PDF from the byte stream
        pdf = fitz.open(stream=pdf_stream, filetype="pdf")
        # Initialize a text buffer to store all extracted text
        text_buffer = io.StringIO()
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            for image_index, img in enumerate(page.get_images(), start=1):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                # Convert CMYK to RGB if necessary
                if image.mode == 'CMYK':
                        image = image.convert('RGB')
                # Check for non-white and non-black images before OCR
                if THRESHOLD_WHITE_PIXEL > np.mean(image) > THRESHOLD_BLACK_PIXEL:
                    # Perform OCR and clean text
                    result = reader.readtext(np.array(image))
                    text = ' '.join([detected_text[1] for detected_text in result])
                    cleaner_text = TextCleaner(text)
                    # Append cleaned text to the buffer
                    text_buffer.write(cleaner_text.clean() + '\n')
                    # Save image to S3
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    image_key = f"{output_prefix}/{pdf_name}/images/{page_index}_{image_index}.png"
                    s3_client.upload_fileobj(img_byte_arr, Bucket=output_bucket, Key=image_key)
        # Save extracted text to S3
        text_content = text_buffer.getvalue()
        text_key = f"{output_prefix}/{pdf_name}/{EXTRACTED_TEXT_FROM_IMAGE}.txt"
        s3_client.put_object(Bucket=output_bucket, Key=text_key, Body=text_content)
        # Cleanup
        pdf_stream.close()
        text_buffer.close()
            

    @staticmethod
    def extract_text_from_pdf(pdf_name, pdf_stream, output_bucket, output_prefix):
        pdf_reader = pypdf.PdfReader(pdf_stream)
        num_pages = len(pdf_reader.pages)
        # Initialize a text buffer
        text_buffer = io.StringIO()
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            cleaner_text = TextCleaner(text)  # Assuming this returns a string
            text_buffer.write(cleaner_text.clean())
        # Move the cursor to the beginning of the text buffer
        text_buffer.seek(0)
        # Write the concatenated text to a file in the output S3 bucket
        output_key = os.path.join(f'{output_prefix}/{pdf_name}', f"{EXTRACTED_TEXT_FROM_PDF}.txt")
        s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=text_buffer.getvalue())

    @staticmethod
    def concatenate_text_files_s3(output_bucket, pdf_name, output_prefix):
        # Download and read the content of the first file
        obj1 = s3_client.get_object(Bucket=output_bucket, Key=f'{output_prefix}/{pdf_name}/{EXTRACTED_TEXT_FROM_IMAGE}.txt')
        text1 = obj1['Body'].read().decode('utf-8')

        # Download and read the content of the second file
        obj2 = s3_client.get_object(Bucket=output_bucket, Key=f'{output_prefix}/{pdf_name}/{EXTRACTED_TEXT_FROM_PDF}.txt')
        text2 = obj2['Body'].read().decode('utf-8')

        # Concatenate the contents of the two files
        combined_text = text1 + "\n" + text2
    

        # Write the combined content back to a new file in S3
        s3_client.put_object(Bucket=output_bucket, 
                             Key=f'{output_prefix}/{pdf_name}/{COMBINED_TEXT}.txt', 
                             Body=combined_text)
