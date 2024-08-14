# Use the official Python image from the Docker Hub
FROM python:3.12.5-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create working directory
WORKDIR /code

# Update the package list and install netcat
RUN apt-get update && apt-get install -y -f netcat-openbsd

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /code/

EXPOSE 5001

# Ensure entrypoint script is executable
RUN chmod +x /code/scripts/entrypoint.sh

# Run entrypoint script
ENTRYPOINT ["/code/scripts/entrypoint.sh"]
# CMD ["flask", "run", "--host=0.0.0.0:5001"]