import tiktoken
from django.core.management.base import BaseCommand

from openai import OpenAI

from django.conf import settings

from knowledge.models import Document

# Set OpenAI API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)
TOKEN_LIMIT = 512  # Safe chunk size


def parse_text_file(file_path):
    """Reads the text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content.strip()


def chunk_text(text, max_tokens=TOKEN_LIMIT):
    """Splits text into token-sized chunks."""
    enc = tiktoken.encoding_for_model("text-embedding-ada-002")
    tokens = enc.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]  # Slice tokens
        chunk_text = enc.decode(chunk_tokens)  # Convert back to text
        chunks.append(chunk_text)

    print(f"🔹 Total Chunks Created: {len(chunks)}")  # Debugging
    for idx, chunk in enumerate(chunks):
        print(f"Chunk {idx + 1}: {len(enc.encode(chunk))} tokens")  # Debugging

    return chunks


def save_to_database(text):
    """Saves chunked documents into the database."""
    chunks = chunk_text(text)
    documents_to_create = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"singapore-{i}"
        documents_to_create.append(Document(title="Singapore Guide", content=chunk, chunk_id=chunk_id))

    Document.objects.bulk_create(documents_to_create, ignore_conflicts=True)
    print(f"✅ {len(documents_to_create)} Chunks Saved to Database")  # Debugging


def generate_embeddings_for_documents():
    """Generates embeddings for documents chunk-by-chunk."""
    documents = Document.objects.filter(embedding__isnull=True)

    for doc in documents:
        num_tokens = len(tiktoken.encoding_for_model("text-embedding-ada-002").encode(doc.content))
        print(f"Processing Doc ID {doc.id} - {num_tokens} tokens")  # Debugging

        try:
            response = client.embeddings.create(input=[doc.content], model="text-embedding-ada-002")  # Pass single chunk
            embedding = response.data[0].embedding
            doc.embedding = embedding
            doc.save()
            print(f"✅ Embedding saved for Doc ID {doc.id}")

        except Exception as e:
            print(f"❌ Error processing Doc ID {doc.id}: {e}")

    print("✅ All embeddings generated successfully!")


class Command(BaseCommand):
    help = "Ingest documents and generate embeddings"

    def handle(self, *args, **kwargs):
        text = parse_text_file(
            '/Users/anuragkumar/Desktop/personal/ai_qa_system/knowledge/management/commands/singapore.txt')
        save_to_database(text)
        generate_embeddings_for_documents()
        print("🎯 Done Successfully!")