import os
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from io import StringIO
import plotly.express as px
import plotly.io as pio
from src.Chat import ChatParser
from src.utils import load_custom_stopwords
from nltk.corpus import stopwords
from nltk.util import bigrams
from collections import Counter
import nltk

app = FastAPI()
templates = Jinja2Templates(directory="templates")


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
    return fig


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
    return fig


stop_words = set(stopwords.words('portuguese'))

custom_stop_words = load_custom_stopwords('src/custom_stopwords.txt')

# Merge nltk stopwords and custom stopwords
all_stopwords = stop_words.union(custom_stop_words)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    chat_text = contents.decode("utf-8")

    # Save the uploaded file temporarily
    temp_file_path = "temp_chat.txt"
    with open(temp_file_path, "w", encoding="utf-8") as temp_file:
        temp_file.write(chat_text)

    # Parse the chat
    parser = ChatParser(temp_file_path)
    parser.parse()
    people = parser.get_people()

    # Generate plots
    plots = {}
    for person in people:
        word_freq = get_word_frequencies(people[person].get_messages_tokenized())
        word_plot = plot_word_frequencies(word_freq, person)
        bigram_freq = get_bigram_frequencies(people[person].get_messages_tokenized())
        bigram_plot = plot_bigram_frequencies(bigram_freq, person)

        plots[person] = {
            "word_freq": pio.to_html(word_plot, full_html=False),
            "bigram_freq": pio.to_html(bigram_plot, full_html=False)
        }

    # Remove the temporary file
    os.remove(temp_file_path)

    return {"plots": plots}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

