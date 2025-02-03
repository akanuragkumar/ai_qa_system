import ast
import os
import pickle

from django.core.management.base import BaseCommand
from django.conf import settings

from gensim.models import Word2Vec

from knowledge.models import Document

from openai import OpenAI


client = OpenAI(api_key=settings.OPENAI_API_KEY)
TOKEN_LIMIT = 512


def extract_functions_from_file(file_path):
    """Extract function/class names, code, and docstrings from a Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content)
    functions = []
    tokens = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            name = node.name
            start_line = node.lineno
            end_line = node.body[-1].lineno if node.body else start_line

            function_code = "\n".join(content.splitlines()[start_line - 1:end_line])

            # Extract docstring if available
            docstring = ast.get_docstring(node) or ""

            functions.append((name, function_code, docstring))

            # Tokenize function name, code, and docstring for Word2Vec
            tokens.append(name.split("_") + function_code.split() + docstring.split())

    return functions, tokens


def save_to_database(file_path):
    """Save extracted functions along with docstrings to the database."""
    functions, tokens = extract_functions_from_file(file_path)

    documents_to_create = []
    for name, code, docstring in functions:
        chunk_id = f"{os.path.basename(file_path)}-{name}"
        embedding_response = client.embeddings.create(input=[code + " " + docstring], model="text-embedding-ada-002")
        embedding = embedding_response.data[0].embedding

        documents_to_create.append(
            Document(
                title=name,
                content=code,
                docstring=docstring,  # Store docstring separately
                chunk_id=chunk_id,
                file_path=file_path,
                embedding=embedding
            )
        )

    Document.objects.bulk_create(documents_to_create, ignore_conflicts=True)
    print(f"✅ {len(documents_to_create)} Functions Saved from {file_path}")

    return tokens


def process_repository(directory_path):
    """Recursively process all Python files in a directory and train Word2Vec model."""
    all_tokens = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                tokens = save_to_database(file_path)
                all_tokens.extend(tokens)

    # Train and save Word2Vec model
    if all_tokens:
        w2v_model = Word2Vec(all_tokens, vector_size=100, window=5, min_count=1, workers=4)
        w2v_path = os.path.join(settings.BASE_DIR, "word2vec_model.pkl")
        with open(w2v_path, "wb") as f:
            pickle.dump(w2v_model, f)
        print("✅ Word2Vec model trained and saved!")


class Command(BaseCommand):
    help = "Ingest Python functions into the database"

    def handle(self, *args, **kwargs):
        repo_path = "path/to/your/repository"  # Replace with your repository path"
        process_repository(repo_path)
        print("🎯 Repository Ingestion Done!")
