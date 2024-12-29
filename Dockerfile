FROM python:3.12.5-slim

# Prevents Python from writing .pyc files, reducing unnecessary I/O
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures stdout and stderr are unbuffered, making logs visible in real-time
ENV PYTHONUNBUFFERED 1

# Create working directory
WORKDIR /code

# Copy code to the working directory
COPY . /code/

# Update the package list and install netcat & PostgreSQL client
RUN apt-get update && apt-get install -y -f netcat-openbsd postgresql-client

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# This instruction only serves as documentation
# It does not actually publish the port to the host machine
EXPOSE 5002

# ENTRYPOINT
RUN chmod +x /code/scripts/entrypoint.sh /code/scripts/wait-for-migrations.sh
ENTRYPOINT ["/code/scripts/entrypoint.sh"]
