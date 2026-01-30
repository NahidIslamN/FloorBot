# Use an official Python runtime as a parent image
FROM python:3.12-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn daphne

# Copy project
COPY . /app/

# Make start script executable
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Script to run the application
CMD ["/bin/sh", "/app/start.sh"]


