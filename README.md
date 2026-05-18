<div align="center">

# 🍳 Recipe Hub

### Turn Ingredients Into Culinary Magic

[![Live Demo](https://img.shields.io/badge/Live%20Demo-recipe.vladbortnik.dev-brightgreen?style=for-the-badge&logo=google-chrome)](http://recipe.vladbortnik.dev)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

_An AI-powered web application that transforms ingredient photos into personalized recipe recommendations._

[Live Demo](http://recipe.vladbortnik.dev) • [Report Bug](https://github.com/vladbortnik/recipe-web-app/issues) • [Request Feature](https://github.com/vladbortnik/recipe-web-app/issues)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Live Demo](#-live-demo)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Security Features](#-security-features)
- [Performance](#-performance)
- [Connect With Me](#-connect-with-me)

---

## 🎯 Overview

**Recipe Hub** is a production-grade web application that empowers home chefs to discover recipes based on ingredients they already have. Upload photos of your ingredients and let Azure Computer Vision AI identify them automatically. The app then suggests personalized recipes using the Spoonacular API, eliminating food waste and inspiring culinary creativity.

Built with scalability, security, and user experience in mind, Recipe Hub features a load-balanced multi-instance architecture, OAuth integration, and comprehensive security hardening.

---

## ✨ Key Features

### 🤖 **AI-Powered Ingredient Recognition**

- Upload ingredient photos using Azure Computer Vision API
- Automatic ingredient identification and tagging
- Smart ingredient management with a virtual pantry

### 🔍 **Intelligent Recipe Discovery**

- Spoonacular API integration for 1M+ recipes
- Personalized recommendations based on available ingredients
- Favorite and save recipes to your account
- Global cuisine exploration with dietary filters

### 👤 **User Management & Authentication**

- Traditional email/password signup with email verification
- Google OAuth 2.0 integration for quick sign-in
- Secure password reset flow with time-limited tokens
- Session management with Flask-Login

### 🔐 **Enterprise-Grade Security**

- Password hashing with Bcrypt
- CSRF protection in all forms
- Network segregation with Docker (frontend/backend networks)
- Environment-based secrets management
- GDPR-compliant cookie consent

### ⚡ **Production-Ready Architecture**

- Load-balanced deployment (3 Gunicorn instances)
- PostgreSQL database with automated migrations
- Docker Compose orchestration
- Fault-tolerant multi-instance setup
- Health monitoring and auto-restart

### 📱 **Modern User Experience**

- Responsive design with Bootstrap 5
- Smooth animations using AOS library
- Google Analytics integration
- SEO-optimized with meta tags, sitemap, and structured data
- Progressive enhancement for all devices

---

## 🌐 Live Demo

**Experience Recipe Hub:** [recipe.vladbortnik.dev](http://recipe.vladbortnik.dev)

The application is deployed on a production server with:

- ✅ Load balancing across 3 instances
- ✅ SSL/TLS encryption
- ✅ Automated database migrations
- ✅ Zero-downtime deployments
- ✅ Health monitoring

---

## 🛠️ Tech Stack

### **Backend**

![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat&logo=gunicorn&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)

- **Flask 3.0+**: Lightweight WSGI web framework
- **Gunicorn**: Production WSGI server for concurrent request handling
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: Pythonic ORM with relationship management
- **Flask-Migrate**: Alembic-based database migrations

### **Authentication & Security**

![OAuth](https://img.shields.io/badge/OAuth%202.0-EB5424?style=flat&logo=auth0&logoColor=white)

- **Flask-Login**: User session management
- **Flask-Bcrypt**: Secure password hashing
- **Authlib**: Google OAuth 2.0 integration
- **Flask-WTF**: Form validation & CSRF protection
- **python-dotenv**: Environment variable management

### **Frontend**

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap_5-7952B3?style=flat&logo=bootstrap&logoColor=white)

- **Jinja2**: Server-side templating engine
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icon library
- **AOS**: Scroll animation library
- **Google Fonts**: Typography (Nunito)

### **External APIs**

![Azure](https://img.shields.io/badge/Azure-0078D4?style=flat&logo=microsoft-azure&logoColor=white)

- **Azure Computer Vision**: AI-powered ingredient recognition from images
- **Spoonacular API**: Recipe database and nutrition information

### **DevOps & Infrastructure**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat&logo=nginx&logoColor=white)

- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and load balancer (upstream deployment)
- **Git**: Version control

---

## 🏗️ Architecture

### **Multi-Instance Load-Balanced Design**

```
┌─────────────────────────────────────────────┐
│            Nginx Load Balancer              │
│         (Upstream Infrastructure)           │
└────────────┬────────────┬───────────────────┘
             │            │
   ┌─────────┴────┬───────┴────┬─────────────┐
   │              │             │             │
┌──▼───┐     ┌───▼──┐     ┌───▼──┐           │
│ web1 │     │ web2 │     │ web3 │           │
│:5002 │     │:5003 │     │:5004 │           │
└──┬───┘     └───┬──┘     └───┬──┘           │
   │             │             │              │
   └─────────────┴─────────────┴──────────────┘
                 │
          ┌──────▼──────┐
          │ PostgreSQL  │
          │  Database   │
          │   (db:5432) │
          └─────────────┘
```

### **Network Segregation**

- **Frontend Network**: Public-facing web services
- **Backend Network**: Database access (internal only)
- **No exposed database ports** to the host machine
- Internal DNS resolution between containers

---

## 📁 Project Structure

```
recipe-web-app/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration management
│   ├── models.py                # SQLAlchemy database models
│   ├── routes.py                # Application routes & views
│   ├── forms.py                 # WTForms definitions
│   ├── utils.py                 # Helper functions (API calls, email)
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── layout.html          # Base template (SEO-optimized)
│   │   ├── index.html           # Landing page
│   │   ├── dashboard.html       # User dashboard
│   │   ├── upload.html          # Image upload interface
│   │   ├── login.html           # Login page
│   │   ├── signup.html          # Registration page
│   │   └── ...
│   └── static/                  # CSS, images, favicon
│       ├── main.css
│       ├── robots.txt
│       └── favicon.ico
├── migrations/                  # Database migration files
├── docker-compose.yml           # Multi-container setup
├── Dockerfile                   # Container definition
├── entrypoint.sh               # Startup script (migrations)
├── requirements.txt            # Python dependencies
├── .env-example                # Environment variables template
├── GITHUB-ABOUT-SECTION.md     # GitHub repository metadata
└── README.md                   # This file
```

---

## 🚀 Getting Started

### **Prerequisites**

- [Docker](https://www.docker.com/get-started) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+
- Python 3.9+ _(optional, for local development)_

### **Installation**

1. **Clone the repository**

   ```bash
   git clone https://github.com/vladbortnik/recipe-web-app.git
   cd recipe-web-app
   ```

2. **Set up environment variables**

   ```bash
   cp .env-example .env
   ```

   Edit `.env` and add your API keys:

   ```env
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@db:5432/recipe_db

   # Azure Computer Vision
   AZURE_VISION_KEY=your-azure-key
   AZURE_VISION_ENDPOINT=your-azure-endpoint

   # Spoonacular API
   SPOONACULAR_API_KEY=your-spoonacular-key

   # Google OAuth (optional)
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret

   # Email (for password reset)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

3. **Build and run with Docker Compose**

   ```bash
   docker compose up --build -d
   ```

4. **Access the application**
   - **Web Instance 1**: http://localhost:5002
   - **Web Instance 2**: http://localhost:5003
   - **Web Instance 3**: http://localhost:5004

5. **View logs** (optional)

   ```bash
   docker compose logs -f web1 web2 web3
   ```

6. **Stop the application**
   ```bash
   docker compose down
   ```

### **Database Migrations**

Migrations are handled automatically by `scripts/entrypoint.sh`. No manual intervention required.

For manual migration management:

```bash
# Access container
docker exec -it <container_name> /bin/bash

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

---

## 🔐 Security Features

| Feature                   | Implementation      | Purpose                           |
| ------------------------- | ------------------- | --------------------------------- |
| **Password Hashing**      | Bcrypt with salt    | Secure credential storage         |
| **CSRF Protection**       | Flask-WTF tokens    | Prevent cross-site attacks        |
| **Network Isolation**     | Docker networks     | Database not exposed to host      |
| **OAuth 2.0**             | Google Sign-In      | Secure third-party authentication |
| **Environment Variables** | python-dotenv       | No hardcoded secrets              |
| **Route Protection**      | @login_required     | Authenticated-only endpoints      |
| **Session Management**    | Flask-Login         | Secure user sessions              |
| **Email Verification**    | Time-limited tokens | Prevent fake accounts             |

---

## ⚡ Performance

- **Load Balancing**: 3 Gunicorn worker instances
- **Concurrent Requests**: 6+ workers per instance (18+ total)
- **Database Connection Pooling**: SQLAlchemy pool management
- **Static Asset Caching**: Browser caching headers
- **Lazy Loading**: AOS animations on scroll
- **Fault Tolerance**: Auto-restart on failure

---

## 🤝 Connect With Me

<div align="center">

[![Portfolio](https://img.shields.io/badge/Portfolio-vladbortnik.dev-0EA5E9?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vladbortnik.dev)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vladbortnik)
[![Twitter](https://img.shields.io/badge/Twitter-@vladbortnik__dev-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/vladbortnik_dev)

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/vladbortnik)
[![Contact Me](https://img.shields.io/badge/Contact-Me-4B5563?style=for-the-badge&logo=gmail&logoColor=white)](https://vladbortnik.dev/contact.html)

<!-- [![Get In Touch](https://img.shields.io/badge/Get%20In%20Touch-Online-22C55E?style=for-the-badge&logo=wechat&logoColor=white)](https://vladbortnik.dev/contact.html) -->

**Built with real production experience by [Vlad Bortnik](https://vladbortnik.dev)**

---

<div align="center">

### 🌟 **Built with a passion for clean code, robust architecture, and scalable solutions**

_Software Engineer | Frontend (React 19) → Backend (Flask, PostgreSQL) → Infrastructure (Docker, Nginx, Cloud)_

**[vladbortnik.dev](https://vladbortnik.dev)** • **[Contact](https://vladbortnik.dev/contact.html)** • **CS degree** • **NYC 🗽**

---

_Last updated: May 2026_

</div>
</div>
