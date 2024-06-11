from PIL import Image
from PIL.Image import new
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from src.data_pipeline.jobs_helpers.extract_pdf_file import PdfExtractor
import itertools
import shutil
import cv2
import glob
import os
import logging
LOG = logging.getLogger(__name__)


LIST_IMAGE_OUTPUT = [[], ['./simple_image_1.jpg'], ['./simple_image_1.jpg', './simple_image_2.jpg']]
LIST_TEXT_LINES = [[''], ["this is a test .pdf file."],
                   ["some street", "some town, some postcode", "in some country", "some day,",
                    "this is a test .pdf file which contains a simple image.",
                    "this is a test .pdf file which also contains text."]]

LIST_COMBINATIONS_TEXT_IMAGES = list(itertools.product(*[LIST_IMAGE_OUTPUT, LIST_TEXT_LINES]))
LIST_COLORS = [(209, 123, 193), (153, 153, 255)]

SIMPLE_IMAGE = 'simple_image'
COMBINATION_TEXT_IMAGE = 'combination_text_image'
EXTRACTED_DATA = 'extracted_data'


def create_mock_image(output_path, color, size=(400, 300)):
    img = new(mode="RGB", size=size, color=color)
    img.save(output_path)


def create_mock_pdf(list_image_paths, list_text_lines, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    story = []
    for image_path in list_image_paths:
        im = Image(image_path, 2 * inch, 2 * inch)
        story.append(im)
        story.append(Spacer(1, 12))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    for text in list_text_lines:
        ptext = '%s' % text.strip()
        story.append(Paragraph(ptext, styles["Normal"]))
        story.append(Spacer(1, 12))
    doc.build(story)


def remove_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
    except OSError:
        print(f'The folder path {folder_path} does not exist')


def remove_list_files(files_paths, file_extension):
    list_files = glob.glob(f'{files_paths}*.{file_extension}')
    for file_path in list_files:
        os.remove(file_path)


def test_extract_data():
    dict_images = {}
    LOG.info(f": ")
    for idx_color, color in enumerate(list(range(len(LIST_COLORS))), start=1):
        create_mock_image(f'./{SIMPLE_IMAGE}_{idx_color}.jpg', LIST_COLORS[idx_color-1])
        dict_images[f'image_{idx_color}'] = cv2.imread(f'./{SIMPLE_IMAGE}_{idx_color}.jpg')

    LOG.info(f": ")

    for idx, image_text_combination in enumerate(LIST_COMBINATIONS_TEXT_IMAGES):
        list_image_paths, list_text_lines = image_text_combination
        create_mock_pdf(list_image_paths, list_text_lines, f'./{COMBINATION_TEXT_IMAGE}_{idx}.pdf')
        pdf_extractor = PdfExtractor(f'{COMBINATION_TEXT_IMAGE}_{idx}.pdf',
                                     '.',
                                     EXTRACTED_DATA)

        pdf_extractor.extract_data()

        extracted_text = []
        with open(f'./{EXTRACTED_DATA}/{COMBINATION_TEXT_IMAGE}_{idx}/{COMBINATION_TEXT_IMAGE}_{idx}_text.txt') as myfile:
            for line in myfile.readlines():
                extracted_text.append(line.rstrip('\n'))
        assert all([a == b for a, b in zip(extracted_text, list_text_lines)])
        filelist = glob.glob(f'./{EXTRACTED_DATA}/{COMBINATION_TEXT_IMAGE}_{idx}/{COMBINATION_TEXT_IMAGE}_{idx}*.jpg')
        nbr_images = len(filelist)
        assert nbr_images == len(list_image_paths)
        for idx_image in range(1, len(filelist)+1):
            result_extracted_image = cv2.imread(f'./{EXTRACTED_DATA}/{COMBINATION_TEXT_IMAGE}_{idx}/{COMBINATION_TEXT_IMAGE}_{idx}_0_{idx_image}.jpg')
            expected_extracted_image = dict_images[f'image_{idx_image}']
            assert result_extracted_image.shape == expected_extracted_image.shape

    LOG.info(f": ")
    remove_folder(f'./{EXTRACTED_DATA}')
    LOG.info(f": ")

    LOG.info(f": ")
    remove_list_files(f'./{COMBINATION_TEXT_IMAGE}', 'pdf')
    LOG.info(f": ")

    LOG.info(f": ")
    remove_list_files(f'./{SIMPLE_IMAGE}', 'jpg')
    LOG.info(f": ")












