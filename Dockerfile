# Use a smaller base image for better performance and security
FROM python:3.9-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=ai_qa_system.settings \
    PATH="/scripts:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libpq \
    bash

# Create a virtual environment for better dependency isolation
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy only requirements first for efficient caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a scripts directory for startup scripts
RUN mkdir /scripts
COPY ./entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh

# Expose the port Gunicorn will run on
EXPOSE 8000

# Run entrypoint script
CMD ["entrypoint.sh"]