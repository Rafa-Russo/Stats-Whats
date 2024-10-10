import re
from datetime import datetime
from unidecode import unidecode
from src.Pre_processing import correct_messages, tokenize_messages, remove_stopwords
from src.utils import is_media_omitted, is_deleted_message, is_edited_message


class Message:
    def __init__(self, id, timestamp, author, content):
        self.id = id
        self.timestamp = timestamp
        self.author = author
        self.content = content

    def __repr__(self):
        return f"id: {self.id} => {self.timestamp} - {self.author}: {self.content}"


class Person:
    def __init__(self, name):
        self.name = name
        self.messages = []
        self.deleted_messages = []
        self.media_messages = []
        self.messages_corrected = []
        self.messages_corrected_no_stopwords = []
        self.messages_tokenized = []

    def add_message(self, message):
        self.messages.append(message)

    def get_deleted_messages(self):
        return self.deleted_messages

    def get_media_messages(self):
        return self.media_messages

    def get_messages(self):
        return self.messages

    def get_messages_corrected(self):
        if self.messages_corrected:
            return self.messages_corrected

        self.messages_corrected = correct_messages(self.messages)
        return self.messages_corrected

    def get_messages_corrected_no_stopwords(self):
        if self.messages_corrected_no_stopwords:
            return self.messages_corrected_no_stopwords

        self.messages_corrected_no_stopwords = remove_stopwords(self.get_messages_corrected())
        return self.messages_corrected_no_stopwords

    def get_messages_tokenized(self):
        if self.messages_tokenized:
            return self.messages_tokenized

        self.messages_tokenized = tokenize_messages(self.get_messages_corrected_no_stopwords())
        return self.messages_tokenized

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
            for message_id, line in enumerate(f):
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
                    current_message = Message(message_id, timestamp, author, content)

                    if is_deleted_message(content) or is_media_omitted(content):
                        if is_deleted_message(content):
                            self.deleted_messages.append(current_message)
                            self.people[author].deleted_messages.append(current_message)
                        if is_media_omitted(content):
                            self.media_messages.append(current_message)
                            self.people[author].media_messages.append(current_message)
                    else:
                        if is_edited_message(content):
                            current_message.content = current_message.content[:-26]
                        self.messages.append(current_message)
                        self.people[author].add_message(current_message)

                elif current_message:
                    # Append to the last message if the current line is a continuation
                    self.people[author].messages[-1].content += "\n" + line.strip()

    def get_messages(self):
        return self.messages

    def get_people(self):
        return self.people
