from rest_framework.views import APIView
from rest_framework.response import Response
from openai import OpenAI
from django.conf import settings

from knowledge.models import ChatSession, Message

# Set OpenAI API key
client = OpenAI(api_key=settings.OPENAI_API_KEY)

from knowledge.utils import search_similar_documents

TOKEN_LIMIT = 3000


class QueryView(APIView):
    def post(self, request):
        query = request.data.get("query")
        session_id = request.data.get("session_id")

        if not query:
            return Response({"error": "Query is required"}, status=400)

        # If session_id is missing, create a new one
        if not session_id:
            chat_session = ChatSession.objects.create()
            session_id = str(chat_session.id)  # Ensure it returns a string
        else:
            chat_session, _ = ChatSession.objects.get_or_create(id=session_id)

        # Fetch all previous messages in the session
        messages = Message.objects.filter(chat_session=chat_session).order_by("created_at")
        chat_history = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Token limit handling
        total_tokens = sum(len(msg["content"].split()) for msg in chat_history)
        if total_tokens > TOKEN_LIMIT:
            summary_prompt = f"Summarize the following chat history while keeping important details:\n\n{chat_history}"
            summary_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": summary_prompt}],
                max_tokens=300
            )
            summary = summary_response.choices[0].message.content.strip()

            # Remove old messages and store summary instead
            Message.objects.filter(chat_session=chat_session).delete()
            Message.objects.create(chat_session=chat_session, role="system", content=summary)

            chat_history = [{"role": "system", "content": summary}]

        # Add current user query
        chat_history.append({"role": "user", "content": query})

        # Generate query embedding for retrieval
        embedding_response = client.embeddings.create(input=[query], model="text-embedding-ada-002")
        query_embedding = embedding_response.data[0].embedding

        # Search for relevant documents
        results = search_similar_documents(query_embedding)

        # Merge retrieved content into chat history
        context = "\n\n".join([doc["content"] for doc in results]) if results else "No relevant context found."
        chat_history.append({"role": "system", "content": f"Relevant context:\n\n{context}"})

        # Get AI response
        completion_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            max_tokens=150
        )

        answer = completion_response.choices[0].message.content.strip()

        # Save conversation history
        Message.objects.create(chat_session=chat_session, role="user", content=query)
        Message.objects.create(chat_session=chat_session, role="assistant", content=answer)

        return Response({"answer": answer, "context": context, "session_id": session_id})
