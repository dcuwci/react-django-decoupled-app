# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
# Copy the requirements file
COPY requirements.txt /app/

# Install dependencies
RUN apt-get update && apt-get install -y awscli dos2unix && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . /app/

# Fix line endings and permissions for the entrypoint script
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "if [ \"$DJANGO_ENV\" = \"development\" ]; then python manage.py runserver 0.0.0.0:8000; else gunicorn -c gunicorn.conf.py backend.wsgi:application; fi"]