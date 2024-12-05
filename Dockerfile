# Use an official Python image as the base
FROM python:3.9-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    musl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set build arguments for Flask and environment variables
ARG FLASK_APP
ARG FLASK_ENV
ARG DATABASE_URL
ARG SCHEMA
ARG SECRET_KEY

# Set environment variables
ENV FLASK_APP=${FLASK_APP}
ENV FLASK_ENV=${FLASK_ENV}
ENV DATABASE_URL=${DATABASE_URL}
ENV SCHEMA=${SCHEMA}
ENV SECRET_KEY=${SECRET_KEY}

# Set working directory
WORKDIR /var/www

# Copy dependencies and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2

# Copy the application code
COPY . .

# Ensure the database migrations run successfully
RUN flask db upgrade || { echo "Database upgrade failed"; exit 1; }

# Ensure the database seeds run successfully
RUN flask seed all || { echo "Database seeding failed"; exit 1; }

# Use Gunicorn to serve the application
CMD ["gunicorn", "app:app"]
