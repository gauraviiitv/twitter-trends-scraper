# Use an official Python base image
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*
# Set the working directory
WORKDIR /app

# Copy the application code
COPY app/ ./app
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app/app.py"]
