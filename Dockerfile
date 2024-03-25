# Use an official Python runtime as a parent image
FROM python:3.8-slim

ENV  PYTHONUNBUFFERED  True

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install Gunicorn and other dependencies
RUN pip install --no-cache-dir flask flask-cors qdrant-client sentence-transformers gunicorn

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV QDRANT_URL=https://e3541770-0ff4-4afd-82a7-1fcd383f93c9.us-east4-0.gcp.cloud.qdrant.io:6333
ENV QDRANT_API_KEY=2qW8PUMwWLxGl4B7h-vK3CKrafvIiaYsk40wuVFFOzFp3yukdEbZ6Q

# Run Gunicorn with main:app as the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "main:app"]
