FROM python:3.12.5-slim
# FROM python:3.12.5

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create working directory
WORKDIR /code

# Copy the current directory . in the project to the workdir . in the image
COPY . .

# Update the package list and install netcat & PostgreSQL client
RUN apt-get update && apt-get install -y -f netcat-openbsd postgresql-client

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

# Ensure entrypoint script is executable
RUN chmod +x /code/scripts/entrypoint.sh

# Run entrypoint script
ENTRYPOINT ["/code/scripts/entrypoint.sh"]
# CMD ["flask", "run", "--host=0.0.0.0:5001"]