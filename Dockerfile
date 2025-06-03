FROM python:3.12.5-slim

# Prevents Python from writing .pyc files, reducing unnecessary I/O
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures stdout and stderr are unbuffered, making logs visible in real-time
ENV PYTHONUNBUFFERED=1
# Prevents interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install netcat, apt-utils & PostgreSQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create working directory
WORKDIR /code

# Copy code to the working directory
COPY . /code/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# This instruction only serves as documentation
# It does not actually publish the port to the host machine
EXPOSE 5002

# Permissions
# RUN chmod +x /code/scripts/wait-for-migrations.sh
RUN chmod +x /code/scripts/entrypoint.sh

# ENTRYPOINT
ENTRYPOINT ["/code/scripts/entrypoint.sh"]
