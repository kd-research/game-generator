FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app:app
ENV FLASK_RUN_PORT=5001
# Note: FLASK_ENV=production is default in newer Flask versions when not in debug.
# Gunicorn will be used, so FLASK_ENV might not be directly used by Flask itself in this setup.

# Install uv and system dependencies
RUN pip install --no-cache-dir uv \
    && apt-get update && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy dependency definition files
# pyproject.toml contains the primary dependencies including the git-based 'techies'
COPY pyproject.toml ./
# If requirements.in is also used by uv sync in your specific setup, uncomment the next line
# COPY requirements.in ./

# Install dependencies using uv
# This will install gunicorn and dependencies from pyproject.toml
# uv should handle the git dependency defined in pyproject.toml
RUN uv pip install --no-cache --system gunicorn \
    && uv pip install --system .

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application using Gunicorn
# Make sure 'app:app' correctly points to your Flask app instance.
# 'app' refers to the directory/module 'app' (specifically app/__init__.py where 'app = Flask(__name__)' is)
# The second 'app' refers to the Flask instance variable named 'app'.
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"] 