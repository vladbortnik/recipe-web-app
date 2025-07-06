# About

**Recipe** is a Web Application that enables users to upload images of whole food items, and generates meal recipes based on the available ingredients.

**Live**: [Recipe Hub](http://recipe.vladbortnik.dev)

---

## **Implementation:**

### `TECH STACK`

- **Flask**:
  - A lightweight WSGI web application framework in Python
  - Essential for routing, content rendering, etc

- **Extensions**:
  - **Flask-SQLAlchemy**
    - Integration with SQLAlchemy for ORM capabilities
  - **Flask-Migrate**
    - Handles database migrations
  - **Flask-Bcrypt**
    - Provides password hashing for security
  - **Flask-Login**
    - Handles User Authentication, Session Management, and Protecting Routes
  - **Flask-WTF**
    - Used for Form Creation and Handling
    - Includes Text, Email, Password and File Validations to ensure Data Integrity
  - **Python-dotenv**
    - Used for loading environment variables from a `.env` file

- **PostgreSQL**:
  - A powerful, open-source object-relational database system
  - Used for storing and managing application data

- **Docker and Docker Compose**:
  - Fully containerized using Docker Images and `docker compose` for orchestration

- **Gunicorn**:
  - WSGI Server allows for handling multiple requests concurrently, improving performance and reliability in a production environment

- **Azure Cognitive Services**:
  - Provides computer vision capabilities to analyze images
  - Enables automatic ingredient recognition from uploaded images

- **Spoonacular API**:
  - Integration for fetching recipes based on ingredients
  - Provides additional recipe-related functionalities

<br> 

### `FEATURES`

- **Frontend and User Interface**:
  - HTML templates and CSS styles are used to construct a responsive and intuitive user interface
  - Built using `Jinja2` templating to dynamically render content based on backend data

- **User Authentication and Security**:
  - Implements `Flask-Login` for user session management
  - `Bcrypt` is employed for secure password hashing and protection

- **Deployment and Containerization**:
  - `Dockerfile` defines the app environment using a Python base image, ensuring consistency across deployments
  - `Docker Compose` manages services, enabling a multi-container architecture that includes a web service and a `PostgreSQL` database

- **API Integration**:
  - Utilizes external APIs such as `Azure Computer Vision` and `Spoonacular API` to enhance functionality with features like image recognition and recipe retrieval
  - Utility functions are managed within `utils.py`, ensuring clear code logic and readability

- **Database and Migrations**:
  - `Flask-Migrate` for handling database migrations
  - Utilizes `PostgreSQL` for robust data storage
  - `entrypoint.sh` handles migrations automatically

- **Environment Configuration and Secrets Management**:
  - Uses `.env` to manage sensitive information and environment variables securely
  - `config.py` manages environment-dependent configurations and API keys securely

- **Script Automation**:
  - Automated scripts such as `entrypoint.sh` manage startup processes and dependencies efficiently

- **Network Segregation**:
  - Implemented Docker network isolation by creating separate `frontend` and `backend networks`
  - Removed direct host exposure of database `port 5432`, ensuring database access is only possible through internal Docker networks
  - `Frontend network` for public-facing services
  - `Backend network` for sensitive services (database)
  - No exposed database ports to host
  - `Internal DNS resolution` between containers

- **Load Balancer**:
  - Deployed multiple instances (`web1`, `web2` and `web3`) of the web app using Docker Compose
  - Configured for `Load Balancer` (e.g., Nginx, Apache) to distribute incoming requests across multiple instances
  - Ensured continuous application availability by routing traffic to healthy instances
  - Demonstrated `fault tolerance` in a multi-instance environment
  - Improved user experience with faster response times

- **Production Deployment with Gunicorn**:
  - The application is served using `Gunicorn`, which allows for handling `multiple requests concurrently`, improving performance and reliability in a production environment
  - `Gunicorn` can be easily configured to work with various worker types and settings to optimize performance based on the deployment needs

<br>

### `SECURITY`

- **Password Encryption**: Utilizes Flask-Bcrypt to hash and securely store user passwords.
- **Environment Variables**: Manages sensitive information such as the secret key using environment variables to avoid hardcoding credentials.
- **Access Control**: Protects routes to ensure that only Authenticated Users can access certain pages and perform specific actions.
- **CSRF Protection**: Uses Flask-WTF to include CSRF (Cross-Site Request Forgery) Tokens in Forms, preventing Unauthorized Actions from being executed.
- **Network Segregation**: Implemented Docker network isolation by creating separate frontend and backend networks.

<br>

This project combines modern web technologies and external APIs to deliver a rich feature set for recipe enthusiasts. It is designed for easy deployment and scalability in mind, making it a robust choice for culinary exploration.

---

## How to Install

To set up and run the application using Docker Compose, follow these steps:

1. **Prerequisites**:
    - Make sure you have Docker and Docker Compose installed on your machine
    - Virtual Environments are strongly recommended

2. **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

3. **Create an `.env` file**:
    - Add your environment variables as needed
    - Example of `.env` file is included
    - This file will be used for both the web and database services

4. **Build and run the containers**:

    ```bash
    docker-compose up --build -d
    ```

5. **Access the application**:
    - The web application will be accessible at:
      - http://localhost:5002
      - http://localhost:5003
      - http://localhost:5004

6. **Stop running containers**:

    ```bash
    docker-compose down
    ```

7. **Database Initialization**:
   - `entrypoint.sh` handles migrations automatically
   - There is **NO** need to manually run migrations:

      ```bash
      flask db init
      flask db migrate -m "Initial migration."
      flask db upgrade
      ```

This setup includes a web application powered by Gunicorn and a PostgreSQL database. The services will automatically restart unless manually stopped.

---

## Access Running Container

1. **List running containers**:

   ```bash
   docker ps
   ```

2. **Access a Container**:

   ```bash
   docker exec -it <container_id_or_name> /bin/bash
   ```

3. **Docker Logs**:

   ```bash
   # Tail the logs 
   docker-compose logs -f web1 web2 web3
   docker-compose logs -f db
   ```
