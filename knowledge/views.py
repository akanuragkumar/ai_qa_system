from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import redirect, render
from django.utils.timezone import now, timedelta

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from knowledge.models import ChatSession, Message, Document
from knowledge.utils import search_similar_documents, preprocess_query

from openai import OpenAI

import tiktoken

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)
TOKEN_LIMIT = 3000
MAX_QUERIES_PER_HOUR = 100


class QueryView(APIView):
    """
    API view to handle user queries and generate AI responses.

    This view processes user queries, checks rate limits, fetches relevant context,
    generates AI responses, and caches results for future queries.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST request to process user query.

        Args:
            request (Request): The incoming request object containing user data.

        Returns:
            Response: JSON response containing the AI-generated answer, context, and session ID.
        """
        query = request.data.get("query")
        session_id = request.data.get("session_id")

        if not query:
            return Response({"error": "Query is required"}, status=400)

        # Normalize and expand query (e.g., synonyms, tokenization)
        query = preprocess_query(query)

        if not session_id:
            chat_session = ChatSession.objects.create()
            session_id = str(chat_session.id)
        else:
            chat_session, _ = ChatSession.objects.get_or_create(id=session_id)

        # Rate limiting using DB + Cache
        one_hour_ago = now() - timedelta(hours=1)
        user_message_count = Message.objects.filter(
            chat_session=chat_session, role="user", created_at__gte=one_hour_ago
        ).count()

        if user_message_count >= MAX_QUERIES_PER_HOUR:
            return Response({"error": "Query limit reached. Try again in an hour."}, status=429)

        # Fetch and clean chat history
        messages = Message.objects.filter(chat_session=chat_session).order_by("created_at")
        chat_history = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Handle token limit
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        total_tokens = sum(len(encoding.encode(msg["content"])) for msg in chat_history)

        if total_tokens > TOKEN_LIMIT:
            summary_prompt = f"Summarize the chat while retaining key details:\n\n{chat_history}"
            try:
                summary_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": summary_prompt}],
                    max_tokens=300
                )
                summary = summary_response.choices[0].message.content.strip()
            except Exception as e:
                return Response({"error": "Failed to summarize chat."}, status=500)

            Message.objects.filter(chat_session=chat_session).delete()
            Message.objects.create(chat_session=chat_session, role="system", content=summary)
            chat_history = [{"role": "system", "content": summary}]

        # Add query to chat history
        chat_history.append({"role": "user", "content": query})

        # Check cache for similar queries
        cache_key = f"query_response_{hash(query)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response({"answer": cached_response["answer"], "context": cached_response["context"], "session_id": session_id})

        # Generate embedding
        try:
            embedding_response = client.embeddings.create(input=query, model="text-embedding-ada-002")
            query_embedding = embedding_response.data[0].embedding
        except Exception as e:
            return Response({"error": "Embedding generation failed."}, status=500)

        # Hybrid Search: Vector + Keyword
        vector_results = search_similar_documents(query_embedding)

        # Use TrigramSimilarity for better text search
        keyword_results = Document.objects.annotate(
            similarity=TrigramSimilarity("title", query) + TrigramSimilarity("docstring", query)
        ).filter(similarity__gt=0.3).order_by("-similarity")[:3]

        # Merge results
        results = {doc["id"]: doc for doc in vector_results}
        for doc in keyword_results:
            if doc.id not in results:
                results[doc.id] = {"id": doc.id, "title": doc.title, "content": doc.content, "file_path": doc.file_path}

        context = "\n\n".join([
            f"File: {doc['file_path']}\n{doc['content']}\n\nDocstring: {doc['docstring']}"
            for doc in results.values()
        ]) if results else "No relevant context found."
        chat_history.append({"role": "system", "content": f"Relevant context:\n\n{context}"})


        # AI Response
        try:
            completion_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_history,
                max_tokens=500
            )
            answer = completion_response.choices[0].message.content.strip()
        except Exception as e:
            return Response({"error": "Failed to generate response."}, status=500)

        # Store message history
        Message.objects.create(chat_session=chat_session, role="user", content=query)
        Message.objects.create(chat_session=chat_session, role="assistant", content=answer)

        # Cache response for future queries
        cache.set(cache_key, {"answer": answer, "context": context}, timeout=3600)

        return Response({"answer": answer, "context": context, "session_id": session_id})


@login_required
def chat_view(request):
    """
    View to render the chat interface.

    Args:
        request (Request): The incoming request object.

    Returns:
        HttpResponse: Redirects to the login page if the user is not authenticated.
    """
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if session expires
    return render(request, "chat.html")


def home(request):
    """
    View to render the home page.

    Args:
        request (Request): The incoming request object.

    Returns:
        HttpResponse: The rendered home page.
    """
    return render(request, "home.html")
