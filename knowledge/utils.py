import re
import spacy
import gensim.downloader as api

from django.conf import settings
from django.db import connection

from openai import OpenAI


# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# Load spaCy model
nlp = spacy.load("en_core_web_md")


# Load pre-trained word vectors
try:
    word_vectors = api.load("word2vec-google-news-300")
except Exception:
    word_vectors = api.load("glove-wiki-gigaword-100")


# Domain-specific synonym dictionary
SYNONYM_DICT = {
    "function": ["method", "routine", "procedure"],
    "class": ["blueprint", "structure", "object"],
    "variable": ["parameter", "attribute", "property"],
    "find": ["search", "lookup", "retrieve"],
    "similar": ["related", "matching", "comparable"],
    "documentation": ["docstring", "comment", "explanation"],
}

def search_similar_documents(query_embedding, top_k=3):
    """
    Search for similar documents based on the provided query embedding.

    Args:
        query_embedding (list): The embedding vector of the query.
        top_k (int, optional): The number of top results to return. Defaults to 3.

    Returns:
        list: A list of dictionaries containing document details and their distances.
    """
    embedding_array = f"[{','.join(map(str, query_embedding))}]"
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, title, content, docstring, file_path, embedding <=> %s::vector AS distance
            FROM document
            ORDER BY distance ASC
            LIMIT %s;
            """,
            [embedding_array, top_k]
        )
        results = cursor.fetchall()
    return [
        {"id": row[0], "title": row[1], "content": row[2], "docstring": row[3], "file_path": row[4], "distance": row[5]}
        for row in results
    ]

def get_word_embeddings(words):
    """
    Fetch embeddings for words from OpenAI API.

    Args:
        words (list): A list of words to get embeddings for.

    Returns:
        list: The embedding vector for the input words.
    """
    response = client.embeddings.create(input=" ".join(words), model="text-embedding-ada-002")
    return response.data[0].embedding  # Return the embedding vector

def expand_with_embeddings(words):
    """
    Expand query with embeddings (placeholder for future use).

    Args:
        words (list): A list of words to expand.

    Returns:
        list: The expanded list of words (currently returns the original list).
    """
    return words  # Currently, embeddings are fetched but not modifying query terms

def preprocess_query(query):
    """
    Improved Query Preprocessing with Performance Optimizations.

    Args:
        query (str): The input query to preprocess.

    Returns:
        str: The cleaned and expanded query.
    """
    query = query.lower()
    query = re.sub(r"[^a-z0-9\s]", "", query)  # Remove special chars

    doc = nlp(query)

    # Extract useful tokens (NOUN, VERB, PROPN) and remove stopwords
    words = {token.lemma_ for token in doc if token.pos_ in {"NOUN", "VERB", "PROPN"} and not token.is_stop}

    # Expand with synonyms
    words.update({syn for word in words if word in SYNONYM_DICT for syn in SYNONYM_DICT[word]})

    # Convert to a list for API request
    word_list = list(words)

    # Expand words with embeddings (this function currently doesn't modify words)
    expanded_words = expand_with_embeddings(word_list)

    return " ".join(expanded_words)  # Return cleaned & expanded query
