#!/bin/bash

# Telegram Self-Bot Docker Runner
# This script builds and runs the bot using Docker

echo "🚀 Starting Telegram Self-Bot with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    echo "📦 Building and starting with docker-compose..."
    docker-compose up --build
else
    echo "📦 Building Docker image..."
    docker build -t telegram-selfbot .
    
    echo "🔄 Running container..."
    docker run -it --rm \
        --name telegram-bot \
        -v "$(pwd)/sessions:/app/sessions" \
        -v "$(pwd)/downloads:/app/downloads" \
        -v "$(pwd)/config.py:/app/config.py" \
        -v "$(pwd)/reactor_data.json:/app/reactor_data.json" \
        telegram-selfbot
fi
