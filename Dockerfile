# DataViz Lab - Dockerfile
# Base image: Python 3.6 slim
FROM python:3.6-slim-buster

LABEL maintainer="jakejrc"
LABEL description="DataViz Lab - Data visualization course teaching system"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (if exists) or install directly
RUN pip install --no-cache-dir \
    flask==1.1.4 \
    numpy==1.18.5 \
    pandas==1.1.5 \
    matplotlib==3.3.4 \
    seaborn==0.11.1 \
    wordcloud==1.8.1 \
    jinja2==2.11.3

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
