# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code to the working directory
COPY . .

# Command to run the application
# Assumes your Flask app instance is named 'app' in 'app.py'
# Gunicorn will listen on the port provided by Cloud Run through the $PORT environment variable
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]