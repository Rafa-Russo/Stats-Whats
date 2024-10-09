import re


def load_custom_stopwords(filepath):
    """Load custom stopwords (including regex patterns) from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        custom_stopwords = [line.strip().lower() for line in f]
    return custom_stopwords


def is_media_omitted(text):
    return text == "<Media omitted>"


def is_deleted_message(text):
    return text == "This message was deleted" or text == "You deleted this message"


def match_regex_list(word, list_words):
    """Check if a word matches stop words or regex patterns."""
    for pattern in list_words:
        if re.match(pattern, word):
            return True
    return False
