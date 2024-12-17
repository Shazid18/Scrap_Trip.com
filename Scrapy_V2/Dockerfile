# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies for Scrapy
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && apt-get clean

# Copy requirements.txt file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose app volume for images
VOLUME ["/app/hotel_images"]

# Default command to run Scrapy
CMD ["sh", "-c", "scrapy crawl hotel_details_spider; sleep infinity"]
