# Nginx Configuration Examples

This folder contains Nginx reverse proxy configurations for different deployment scenarios. Each configuration is designed to work with its corresponding Docker Compose setup.

## 📁 Available Configurations

### 1. `nginx-simple-w-auto-migration.conf`
**Best for:** Single-instance deployments

**Features:**
- HTTP to HTTPS redirect
- SSL/TLS with modern security settings (TLS 1.3)
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Reverse proxy to single Flask instance
- Static file caching

**Corresponding Docker Compose:** `docker-compose-examples/compose-simple-w-auto-migration.yaml`

---

### 2. `nginx-w-Load-Balancer.conf`
**Best for:** High-availability production deployments

**Features:**
- All features from simple config, plus:
- Upstream load balancing across 3 Flask instances
- IP hash for session persistence (sticky sessions)
- Health checks with fail-over
- Keepalive connections for better performance
- Detailed logging format (commented, for debugging)

**Corresponding Docker Compose:** `docker-compose-examples/compose-w-Load-Balancer-n-Network-Segregation.yaml`

---

## 🔧 Installation Guide

### Step 1: Copy configuration to Nginx
```bash
# Choose the appropriate config for your setup
sudo cp nginx-simple-w-auto-migration.conf /etc/nginx/sites-available/recipe.vladbortnik.dev

# OR for load-balanced setup
sudo cp nginx-w-Load-Balancer.conf /etc/nginx/sites-available/recipe.vladbortnik.dev
```

### Step 2: Update configuration
Edit the configuration file and update:
- `server_name` with your actual domain
- SSL certificate paths to match your Let's Encrypt location
- Upstream server ports if different from default

### Step 3: Enable the site
```bash
sudo ln -s /etc/nginx/sites-available/recipe.vladbortnik.dev /etc/nginx/sites-enabled/
```

### Step 4: Test and reload
```bash
# Test configuration syntax
sudo nginx -t

# Reload Nginx if test passes
sudo systemctl reload nginx
```

---

## 🔐 SSL Certificate Setup (Let's Encrypt)

### Install Certbot
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### Obtain Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### Auto-renewal
Certbot sets up auto-renewal automatically. Test with:
```bash
sudo certbot renew --dry-run
```

---

## 📊 Load Balancing Strategies

The load-balanced configuration uses `ip_hash` by default. You can change this:

```nginx
upstream recipe_app {
    # Choose ONE of the following strategies:
    
    # 1. IP Hash (default) - Same client always goes to same server
    ip_hash;
    
    # 2. Least Connections - Routes to server with fewest connections
    # least_conn;
    
    # 3. Round Robin (default if no directive) - Even distribution
    # (just remove ip_hash line)
    
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
    server 127.0.0.1:5004;
}
```

---

## 🛡️ Security Headers Explained

| Header | Purpose |
|--------|---------|
| `Strict-Transport-Security` | Forces HTTPS for 2 years |
| `X-Frame-Options` | Prevents clickjacking |
| `X-Content-Type-Options` | Prevents MIME sniffing |
| `Referrer-Policy` | Controls referrer information |
| `Permissions-Policy` | Restricts browser features |
| `Content-Security-Policy` | Prevents XSS attacks |

---

## 🔍 Debugging Tips

### Enable detailed logging
Uncomment the logging sections in the config:
```nginx
log_format upstream_time '$remote_addr - $remote_user [$time_local] '
                         '"$request" $status $body_bytes_sent '
                         'upstream_addr="$upstream_addr"';

access_log /var/log/nginx/recipe_access.log upstream_time;
error_log /var/log/nginx/recipe_error.log debug;
```

### Check upstream connectivity
```bash
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health
```

### View Nginx error logs
```bash
sudo tail -f /var/log/nginx/error.log
```

---

## 📚 Learning Resources

- **Nginx Documentation:** https://nginx.org/en/docs/
- **Mozilla SSL Configuration Generator:** https://ssl-config.mozilla.org/
- **Security Headers Scanner:** https://securityheaders.com/
- **SSL Labs Test:** https://www.ssllabs.com/ssltest/

