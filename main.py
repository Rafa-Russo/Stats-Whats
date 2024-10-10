import re
from nltk.corpus import stopwords
from nltk.util import bigrams
from collections import Counter
import plotly.express as px
from src.Chat import ChatParser
from src.utils import load_custom_stopwords, match_regex_list
import nltk
nltk.download('stopwords')


def get_word_frequencies(messages_tokenized):
    all_text = [word for message in messages_tokenized for word in message]
    word_freq = Counter(all_text)

    return word_freq


def plot_word_frequencies(word_freq, author):
    # Convert the Counter dictionary to a list of words and their frequencies
    word_data = list(word_freq.items())

    # Sort by frequency and take the top 20 words
    top_words = sorted(word_data, key=lambda x: x[1], reverse=True)[:20]

    # Prepare the data for Plotly
    words, frequencies = zip(*top_words)

    # Create a bar plot using Plotly
    fig = px.bar(x=words, y=frequencies, labels={'x': 'Words', 'y': 'Frequency'},
                 title=f'Most Used Words by {author}')
    fig.show()


def get_bigram_frequencies(messages_tokenized):
    """Get bigram frequencies from a list of messages."""
    # Concatenate all words in one list
    all_text = [word for message in messages_tokenized for word in message]

    # Generate bigrams (pairs of consecutive words)
    bigrams_list = list(bigrams(all_text))

    # Count bigram frequencies
    bigram_freq = Counter(bigrams_list)

    return bigram_freq


def plot_bigram_frequencies(bigram_freq, author):
    """Plot the top 10 bigram frequencies for a person."""
    # Convert the Counter dictionary to a list of bigrams and their frequencies
    bigram_data = list(bigram_freq.items())

    # Sort by frequency and take the top 20 bigrams
    top_bigrams = sorted(bigram_data, key=lambda x: x[1], reverse=True)[:20]

    # Prepare the data for Plotly
    bigrams_str = [' '.join(bigram) for bigram, _ in top_bigrams]
    frequencies = [freq for _, freq in top_bigrams]

    # Create a bar plot using Plotly
    fig = px.bar(x=bigrams_str, y=frequencies, labels={'x': 'Bigrams', 'y': 'Frequency'},
                 title=f'Most Common Bigrams by {author}')
    fig.show()


stop_words = set(stopwords.words('portuguese'))

custom_stop_words = load_custom_stopwords('src/custom_stopwords.txt')

# Merge nltk stopwords and custom stopwords
all_stopwords = stop_words.union(custom_stop_words)


if __name__ == "__main__":
    parser = ChatParser('WhatsApp_Chat_Isa/chat_Isa.txt')
    parser.parse()
    people = parser.get_people()

    for person in people:
        word_freq = get_word_frequencies(people[person].get_messages_tokenized())
        plot_word_frequencies(word_freq, person)
        bigram_freq = get_bigram_frequencies(people[person].get_messages_tokenized())
        plot_bigram_frequencies(bigram_freq, person)
