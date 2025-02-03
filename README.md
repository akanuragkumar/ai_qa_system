AI QA System
============

Overview
--------

The AI QA System is a Django-based web application designed to help users interact with their code repositories through natural language queries. Users can upload their code repositories and ask questions about the code, such as "Where is this function?" or "Show me similar functions." The system leverages AI to provide intelligent and context-aware responses.

Features
--------

-   Code Repository Upload: Users can upload their code repositories for analysis.

-   Natural Language Queries: Users can ask questions about the code in natural language.

-   AI-Powered Responses: The system uses AI to understand and respond to user queries.

-   User Authentication: Secure user authentication and session management.

-   Session Management: Auto-logout after 15 minutes of inactivity for security.

Quick Setup
-----------

### Prerequisites

-   Docker

-   Docker Compose

-   Python 3.9

-   PostgreSQL

### Installation

1.  Clone the Repository:

    bashCopy

    ```
    https://github.com/akanuragkumar/ai_qa_system.git
    ```

2.  Set Up Environment Variables: Create a `.env` file in the root directory with the following content:

    envCopy

    ```
    SECRET_KEY=your_secret_key_here
    DATABASE_NAME=your_database_name
    DATABASE_USER=your_database_user
    DATABASE_PASSWORD=your_database_password
    DATABASE_HOST=your_database_host
    DATABASE_PORT=your_database_port
    OPENAI_API_KEY=your_openai_api_key
    ```

3.  Build and Run the Docker Containers:

    bashCopy

    ```
    docker-compose up --build
    ```

4.  Ingest Codebase:

    bashCopy

    ```
    docker-compose run web python manage.py ingest_code
    ```

5.  Run the Development Server:

    bashCopy

    ```
    docker-compose run web python manage.py runserver
    ```

6.  Access the Application: Open your web browser and navigate to `http://127.0.0.1:8000/`.

### Usage

1.  Homepage:

    -   Navigate to `http://127.0.0.1:8000/`. This will guide you to the registration page.

    -   Register an account and log in.

2.  Chat Interface:

    -   After logging in, you will be redirected to `http://127.0.0.1:8000/chat/`.

    -   Here, you can start asking questions about your codebase.

### Database Setup

1.  Run PostgreSQL Extensions:

    -   Access the PostgreSQL shell:

        bashCopy

        ```
        docker-compose run web psql -h DATABASE_HOST -U DATABASE_USER -d DATABASE_NAME
        ```

    -   Run the following commands to create the necessary extensions:

        sqlCopy

        ```
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        CREATE EXTENSION IF NOT EXISTS vector;
        ```

### Development

1.  Run Migrations:

    bashCopy

    ```
    docker-compose run web python manage.py migrate
    ```

### Deployment

For production deployment, ensure the following:

-   Set `DEBUG` to `False` in the settings file.

-   Configure `ALLOWED_HOSTS` appropriately.

-   Use a secure web server like Nginx or Gunicorn.

-   Set up a PostgreSQL database and configure the settings accordingly.

-   Use environment variables to manage sensitive information.
