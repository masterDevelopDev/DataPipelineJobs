from DataPipeline.src.utils.clean_text import TextCleaner


def test_strip_accents():
    assert TextCleaner.transliterate('kožušček') == 'kozuscek'
    assert TextCleaner.transliterate('北亰') == 'Bei Jing '
    assert TextCleaner.transliterate('François') == 'Francois'


def test_lower_characters():
    assert TextCleaner.lower_characters('THiS Is a TEST') == 'this is a test'
    assert TextCleaner.lower_characters('this is another test') == 'this is another test'


def test_clean():
    text = 'ThIs IS A test TEXT with UpPERCase LETTERS anD acçents'
    text_cleaner = TextCleaner(text)
    assert text_cleaner.clean() == 'this is a test text with uppercase letters and accents'
