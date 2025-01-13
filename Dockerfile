# Use the official Python image
FROM python:3.9-slim

# Install system dependencies (LibreOffice and necessary packages)
RUN apt-get update && apt-get install -y \
    libreoffice \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app will run on
EXPOSE 8000

# Command to run the FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
