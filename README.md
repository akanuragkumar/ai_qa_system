**AI-powered Question Answering System with Django and OpenAI**

This is a Django-based web application that integrates OpenAI’s GPT model to create an AI-powered question answering system. The system provides users with accurate, context-aware responses based on historical conversation and relevant documents stored in a database.

**Features:**

•**Django Backend**: A robust backend built with Django REST Framework to handle API requests and responses.

•**OpenAI Integration**: Uses OpenAI’s GPT model to generate intelligent responses based on the context of previous conversations and relevant documents.

•**Session-based Conversations**: Maintains chat sessions to allow for ongoing conversations with context retention across multiple interactions.

•**Document Embedding**: Documents are embedded using OpenAI’s text-embedding-ada-002 model and stored in the database for similarity search.

•**Efficient Token Management**: Automatically handles long conversation histories by summarizing older messages when the token limit is exceeded.

•**Document Search**: Retrieves relevant documents based on the user’s query using embeddings and vector-based similarity search.

**Tech Stack:**

•**Backend**: Django, Django REST Framework

•**AI Model**: OpenAI GPT-3.5 for completions and text embeddings

•**Database**: PostgreSQL (for storing chat sessions, messages, and documents)

•**Containerization**: Docker for easy deployment

•**Environment Management**: .env file for managing API keys and configurations

**How It Works:**

1.**User Query**: Users can send queries to the system via a REST API. Each query is processed to find the relevant context from previous messages and documents.

2.**Chat Session Management**: Each interaction is stored as part of a chat session, with the history of previous messages being used to provide more accurate answers.

3.**Embedding Search**: The system generates embeddings for documents and user queries, then performs a similarity search to retrieve relevant content.

4.**Response Generation**: The relevant documents and chat history are passed into the OpenAI GPT model to generate a response to the user’s query.

5.**Efficient Handling**: If the conversation becomes too long (exceeding OpenAI’s token limit), older messages are summarized and retained in the session.

**Installation Instructions:**

1.Clone the repository:

git clone [[https://github.com/your-username/ai-qa-system.git](https://github.com/akanuragkumar/ai_qa_system.git)](https://github.com/akanuragkumar/ai_qa_system.git)

cd ai-qa-system

2.Set up a virtual environment and install dependencies:

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

3.Create a .env file and add your OpenAI API key and other settings:

_OPENAI_\_API\_KEY=your\_openai\_api\_key

_DJANGO_\_SETTINGS\_MODULE=your\_project.settings

4.Run database migrations:

python manage.py migrate

5.Start the Django development server:

python manage.py runserver

**Docker Setup:**

To run the project in Docker, follow these steps:

1.Build the Docker image:

docker-compose build

2.Start the application:

docker-compose up

This will run the application inside Docker containers with all environment variables loaded from the .env file.

**License:**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
