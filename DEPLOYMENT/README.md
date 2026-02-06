# Deployment Documentation - Recipe Hub

## Overview

Recipe Hub is deployed on a production server at **recipe.vladbortnik.dev** using a containerized, load-balanced architecture.

---

## Deployment Architecture

### **Infrastructure Stack**

```
Internet
    ↓
Nginx Reverse Proxy (Port 80/443)
    ↓
Load Balancer
    ↓
Docker Compose Multi-Instance Setup
    ├── Web Instance 1 (web1:5002)
    ├── Web Instance 2 (web2:5003)
    └── Web Instance 3 (web3:5004)
    ↓
PostgreSQL Database (db:5432)
```

### **Network Architecture**

- **Frontend Network**: Connects Nginx to web instances
- **Backend Network**: Connects web instances to database
- **No Direct Database Access**: Database port (5432) not exposed to host
- **Internal DNS**: Containers communicate via Docker DNS

---

## Deployment Steps

### 1. **Server Setup**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io docker-compose -y

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. **Application Deployment**

```bash
# Clone repository
git clone https://github.com/vladbortnik/recipe-web-app.git
cd recipe-web-app

# Set up environment variables
cp .env-example .env
nano .env  # Edit with production values

# Build and start containers
docker-compose up --build -d

# Verify deployment
docker-compose ps
docker-compose logs -f
```

### 3. **Nginx Configuration** (Upstream Server)

Located at `/etc/nginx/sites-available/recipe.vladbortnik.dev`

```nginx
upstream recipe_backend {
    least_conn;
    server localhost:5002 max_fails=3 fail_timeout=30s;
    server localhost:5003 max_fails=3 fail_timeout=30s;
    server localhost:5004 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name recipe.vladbortnik.dev;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name recipe.vladbortnik.dev;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/recipe.vladbortnik.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/recipe.vladbortnik.dev/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy settings
    location / {
        proxy_pass http://recipe_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files caching
    location /static/ {
        proxy_pass http://recipe_backend;
        proxy_cache_valid 200 30d;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4. **SSL Certificate** (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d recipe.vladbortnik.dev

# Auto-renewal (cron job)
sudo certbot renew --dry-run
```

---

## Environment Variables (Production)

```env
# Flask Configuration
SECRET_KEY=<strong-random-secret>
FLASK_ENV=production
FLASK_DEBUG=0

# Database
DATABASE_URL=postgresql://recipe_user:secure_password@db:5432/recipe_db

# Azure Computer Vision
AZURE_VISION_KEY=<production-azure-key>
AZURE_VISION_ENDPOINT=https://<region>.api.cognitive.microsoft.com/

# Spoonacular API
SPOONACULAR_API_KEY=<production-api-key>

# Google OAuth
GOOGLE_CLIENT_ID=<production-client-id>
GOOGLE_CLIENT_SECRET=<production-client-secret>

# Email (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=<production-email>
MAIL_PASSWORD=<app-specific-password>

# Google Analytics
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

---

## Docker Compose Configuration

**File**: `docker-compose.yml`

```yaml
version: "3.8"

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: recipe_db
      POSTGRES_USER: recipe_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    restart: unless-stopped

  web1:
    build: .
    ports:
      - "5002:5000"
    env_file:
      - .env
    depends_on:
      - db
    networks:
      - frontend
      - backend
    restart: unless-stopped

  web2:
    build: .
    ports:
      - "5003:5000"
    env_file:
      - .env
    depends_on:
      - db
    networks:
      - frontend
      - backend
    restart: unless-stopped

  web3:
    build: .
    ports:
      - "5004:5000"
    env_file:
      - .env
    depends_on:
      - db
    networks:
      - frontend
      - backend
    restart: unless-stopped

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: false

volumes:
  postgres_data:
```

---

## Monitoring & Maintenance

### **Health Checks**

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f web1 web2 web3

# Check database status
docker exec -it recipe-web-app_db_1 psql -U recipe_user -d recipe_db -c "SELECT version();"
```

### **Application Updates**

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker-compose down
docker-compose up --build -d

# Run database migrations (if needed)
docker exec -it recipe-web-app_web1_1 flask db upgrade
```

### **Database Backup**

```bash
# Backup database
docker exec -it recipe-web-app_db_1 pg_dump -U recipe_user recipe_db > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251017.sql | docker exec -i recipe-web-app_db_1 psql -U recipe_user -d recipe_db
```

---

## Performance Metrics

- **Load Balancing**: Distributes traffic across 3 instances
- **Concurrent Requests**: 18+ workers (6 per instance)
- **Response Time**: <500ms for most requests
- **Uptime**: 99.9% (auto-restart on failure)
- **Database Connections**: Pooled via SQLAlchemy

---

## Security Measures

✅ **SSL/TLS Encryption** (Let's Encrypt)
✅ **Network Segregation** (Docker networks)
✅ **No Exposed Database Ports** (internal only)
✅ **Environment-Based Secrets** (.env files)
✅ **Security Headers** (via Nginx)
✅ **CSRF Protection** (Flask-WTF)
✅ **Password Hashing** (Bcrypt)
✅ **OAuth 2.0** (Google Sign-In)

---

## Troubleshooting

### Issue: Containers fail to start

```bash
# Check logs
docker-compose logs

# Verify environment variables
cat .env

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Issue: Database connection errors

```bash
# Check database status
docker exec -it recipe-web-app_db_1 pg_isready -U recipe_user

# Reset database
docker-compose down
docker volume rm recipe-web-app_postgres_data
docker-compose up -d
```

### Issue: Nginx 502 Bad Gateway

```bash
# Check if containers are running
docker-compose ps

# Test upstream connectivity
curl http://localhost:5002
curl http://localhost:5003
curl http://localhost:5004

# Restart Nginx
sudo systemctl restart nginx
```

---

## Rollback Procedure

```bash
# Revert to previous version
git log --oneline  # Find commit hash
git checkout <previous-commit>

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

---

## Future Enhancements

- [ ] Implement Redis for session storage
- [ ] Add Prometheus + Grafana monitoring
- [ ] Set up automated backups to S3/Cloud Storage
- [ ] Implement blue-green deployment strategy
- [ ] Add rate limiting for API endpoints
- [ ] Set up log aggregation (ELK stack)
- [ ] Implement CDN for static assets

---

**Last Updated**: October 17, 2025
**Deployed By**: Vlad Bortnik
**Production URL**: https://recipe.vladbortnik.dev
