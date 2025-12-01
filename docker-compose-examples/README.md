# Docker Compose Configuration Examples

This folder contains different Docker Compose configurations for various deployment scenarios. Choose the one that best fits your needs.

## 📁 Available Configurations

### 1. `compose-simple-w-auto-migration.yaml`
**Best for:** Development, testing, or small-scale production

**Features:**
- Single Flask application instance
- Automatic database migrations on startup
- PostgreSQL database with exposed port (for local development)
- Simple setup with minimal configuration

**Architecture:**
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   migration  │ ──► │     web1     │ ──► │      db      │
│  (one-time)  │     │   (Flask)    │     │  (PostgreSQL)│
└──────────────┘     └──────────────┘     └──────────────┘
                           ↑
                      Port 5002
```

**Usage:**
```bash
docker compose -f docker-compose-examples/compose-simple-w-auto-migration.yaml up --build -d
```

---

### 2. `compose-w-Load-Balancer-n-Network-Segregation.yaml`
**Best for:** Production deployments requiring high availability

**Features:**
- 3 Flask application instances for load balancing
- Network segregation (frontend/backend isolation)
- Database NOT exposed to host (security)
- Resource limits (CPU/Memory) for each container
- Health checks for all services

**Architecture:**
```
         ┌─────── Frontend Network ───────┐
         │                                │
         │  ┌────────┐  ┌────────┐  ┌────────┐
         │  │  web1  │  │  web2  │  │  web3  │
         │  │ :5002  │  │ :5003  │  │ :5004  │
         │  └───┬────┘  └───┬────┘  └───┬────┘
         │      │           │           │
         └──────┼───────────┼───────────┼─────┘
                │           │           │
         ┌──────┼───────────┼───────────┼─────┐
         │      └───────────┴───────────┘     │
         │                  │                 │
         │          ┌───────▼───────┐         │
         │          │      db       │         │
         │          │  (PostgreSQL) │  Backend │
         │          │    :5432      │  Network │
         │          └───────────────┘ (Internal)
         └────────────────────────────────────┘
```

**Usage:**
```bash
docker compose -f docker-compose-examples/compose-w-Load-Balancer-n-Network-Segregation.yaml up --build -d
```

---

## 🔗 Related Nginx Configurations

Each Docker Compose configuration has a corresponding Nginx configuration:

| Docker Compose File | Nginx Config File |
|---------------------|-------------------|
| `compose-simple-w-auto-migration.yaml` | `nginx.conf-examples/nginx-simple-w-auto-migration.conf` |
| `compose-w-Load-Balancer-n-Network-Segregation.yaml` | `nginx.conf-examples/nginx-w-Load-Balancer.conf` |

---

## 🚀 Quick Start Guide

### Step 1: Choose your configuration
- **Development/Testing:** Use `compose-simple-w-auto-migration.yaml`
- **Production:** Use `compose-w-Load-Balancer-n-Network-Segregation.yaml`

### Step 2: Set up environment variables
```bash
cp .env-example .env
# Edit .env with your configuration
```

### Step 3: Start the services
```bash
# Simple setup
docker compose -f docker-compose-examples/compose-simple-w-auto-migration.yaml up --build -d

# OR Load balanced setup
docker compose -f docker-compose-examples/compose-w-Load-Balancer-n-Network-Segregation.yaml up --build -d
```

### Step 4: Configure Nginx (production only)
Copy the appropriate Nginx config to `/etc/nginx/sites-available/` and create a symlink.

---

## 📚 Learning Resources

- **Docker Compose Documentation:** https://docs.docker.com/compose/
- **Nginx Reverse Proxy Guide:** https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- **PostgreSQL Docker Image:** https://hub.docker.com/_/postgres

---

## 🔒 Security Notes

1. **Never expose database ports in production** - The load-balanced config keeps the database on an internal network only
2. **Use strong passwords** - Generate secure passwords for `POSTGRES_PASSWORD` and `SECRET_KEY`
3. **SSL/TLS is required** - Always use HTTPS in production (configured in Nginx)
4. **Environment variables** - Never commit `.env` files to version control

