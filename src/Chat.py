import re
from datetime import datetime
from unidecode import unidecode
from src.utils import is_media_omitted, is_deleted_message


class Message:
    def __init__(self, timestamp, author, content):
        self.timestamp = timestamp
        self.author = author
        self.content = content

    def __repr__(self):
        return f"{self.timestamp} - {self.author}: {self.content}"


class Person:
    def __init__(self, name):
        self.name = name
        self.messages = []
        self.deleted_messages = []
        self.media_messages = []
        self.messages_corrected = []
        self.messages_corrected_no_stopwords = []
        self.messages_tokenized = []

    def correct_messages(self, file_path):
        """Checks the file path for a dictionary of regex patterns to correct messages.
        The dictionary should be in the format: {"pattern": "replacement"}.

        Args:
            file_path (str): The file path to the dictionary of regex patterns.

        Returns:
            None
            """
        # TODO Test
        with open(file_path, 'r', encoding='utf-8') as f:
            corrections = dict([line.strip().split(",") for line in f])

        for message in self.messages:
            corrected_message = message.content
            for pattern, replacement in corrections.items():
                corrected_message = re.sub(pattern, replacement, corrected_message)
            self.messages_corrected.append(corrected_message)

    def remove_stopwords(self, file_path):
        """ Removes stopwords from messages using regex patterns.

        Args:
            file_path (str): The file path to the list of stopwords.

        Returns:
            None
                """
        # TODO Test
        with open(file_path, 'r', encoding='utf-8') as f:
            stopwords = [line.strip() for line in f]

        for message in self.messages_corrected:
            message_no_stopwords = message
            for stopword in stopwords:
                message_no_stopwords = re.sub(stopword, "", message_no_stopwords)
            self.messages_corrected_no_stopwords.append(message_no_stopwords)

    def tokenize_messages(self):
        """Tokenizes messages into words.

        Args:
            None

        Returns:
            None
            """
        for message in self.messages_corrected_no_stopwords:
            self.messages_tokenized.append(message.split())
    def add_message(self, message):
        self.messages.append(message)

    def __repr__(self):
        return f"Person({self.name}, {len(self.messages)} messages)"


class ChatParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.messages = []
        self.people = {}
        self.deleted_messages = []
        self.media_messages = []

    def parse(self):
        message_pattern = r"(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}) - (.*?): (.*)"

        with open(self.file_path, 'r', encoding='utf-8') as f:
            current_message = None
            for line in f:
                match = re.match(message_pattern, line)
                if match:
                    # New message found
                    timestamp_str = match.group(1)
                    author = match.group(2)
                    if author not in self.people:
                        self.people[author] = Person(author)
                    content = unidecode(match.group(3)).lower()

                    # Convert timestamp to datetime object
                    timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y, %H:%M")

                    # Create a new message object
                    current_message = Message(timestamp, author, content)
                    if is_deleted_message(content) or is_media_omitted(content):
                        if is_deleted_message(content):
                            self.deleted_messages.append(current_message)
                            self.people[author].deleted_messages.append(current_message)
                        if is_media_omitted(content):
                            self.media_messages.append(current_message)
                            self.people[author].media_messages.append(current_message)
                    else:
                        self.messages.append(current_message)
                        self.people[author].add_message(current_message)

                elif current_message:
                    # Append to the last message if the current line is a continuation
                    self.people[author].messages[-1].content += "\n" + line.strip()

    def get_messages(self):
        return self.messages

    def get_people(self):
        return self.people
