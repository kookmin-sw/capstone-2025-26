# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Specify Poetry version
ENV POETRY_VERSION=2.1.1
# Ensure Poetry runs without prompts
ENV POETRY_NO_INTERACTION=1
# Do not create virtualenvs
ENV POETRY_VIRTUALENVS_CREATE=false

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies using Poetry
# Use --no-dev to exclude development dependencies
RUN poetry install --no-root

# Copy project
COPY . /app/

# Copy environment file
COPY .env /app/.env

# Expose port 8000 for the application
EXPOSE 8000

RUN poetry run python manage.py migrate

# Specify the command to run the application using Gunicorn
# Replace 'config' with the actual name of your Django project directory containing wsgi.py
CMD ["poetry", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"] 