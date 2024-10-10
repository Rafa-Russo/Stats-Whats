import re
import json


CORRECTION_DICT = r'src\corrections.json'
STOPWORDS_LIST = r'src\custom_stopwords.txt'


def _treat_non_characters(text):
    """Removes non-character characters from a text."""
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def correct_messages(messages, file_path=CORRECTION_DICT):
    """Checks the file path for a dictionary of regex patterns to correct messages.
    The dictionary should be in the format: {"pattern": "replacement"}.

    Args:
        messages (list): A list of messages to correct.
        file_path (str): The file path to the dictionary of regex patterns.

    Returns:
        messages_corrected: A list of corrected messages.
        """
    with open(file_path, 'r', encoding='utf-8') as f:
        corrections = json.load(f)

    messages_corrected = []
    for message in messages:
        corrected_message = _treat_non_characters(message.content)
        for pattern, replacement in corrections.items():
            corrected_message = re.sub(pattern, replacement, corrected_message)
        messages_corrected.append(corrected_message)

    return messages_corrected


def remove_stopwords(messages_corrected, file_path=STOPWORDS_LIST):
    """ Removes stopwords from messages using regex patterns.

    Args:
        messages_corrected (list): A list of messages (already corrected) to remove stopwords from.
        file_path (str): The file path to the list of stopwords.

    Returns:
        messages_corrected_no_stopwords: A list of messages with stopwords removed.
            """
    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f]

    messages_corrected_no_stopwords = []
    for message in messages_corrected:
        message_no_stopwords = message
        for stopword in stopwords:
            message_no_stopwords = re.sub(stopword, "", message_no_stopwords)
        messages_corrected_no_stopwords.append(message_no_stopwords)

    return messages_corrected_no_stopwords


def tokenize_messages(messages_corrected_no_stopwords):
    """Tokenizes messages into words.

    Args:
        messages_corrected_no_stopwords (list): A list of messages (already corrected and with stopwords removed) to tokenize.

    Returns:
        messages_tokenized: A list of tokenized messages.
        """
    messages_tokenized = []
    for message in messages_corrected_no_stopwords:
        messages_tokenized.append(message.split())

    return messages_tokenized
