import re

def sanitize(text):
    text = text.strip().lower()
    text = utf8_to_ascii(text)
    text = del_white_space(text)
    return text

def sanitize_value(text):
    text = text.strip()
    text = utf8_to_ascii(text)
    return text

def utf8_to_ascii(text):
    return text\
            .replace('á', 'a')\
            .replace('ê', 'e')\
            .replace('Ú', 'u')\
            .replace('í', 'i')\
            .replace('ô', 'o')\
            .replace('ç', 'c')\
            .replace('ú', 'u')\
            .replace('ã', 'a')

def del_white_space(text):
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'\-+', '_', text)
    return text