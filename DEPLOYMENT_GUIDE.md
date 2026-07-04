# JARVIS Mission Control + n8n Deployment Guide
## Complete Hostinger VPS Deployment

---

## 📦 **Created Files Summary**

### **Docker & Infrastructure**
| File | Purpose |
|------|---------|
| `deploy/docker-compose.yml` | Full stack: Mission Control, n8n, Redis, PostgreSQL, Nginx, Certbot |
| `deploy/Dockerfile.mission-control` | Multi-stage build for Mission Control |
| `deploy/requirements.mission-control.txt` | Python dependencies |
| `deploy/nginx/nginx.conf` | Main nginx configuration |
| `deploy/nginx/conf.d/jarvis.conf` | Virtual host configuration |

### **Deployment Scripts**
| File | Purpose |
|------|---------|
| `scripts/deployment/deploy_hostinger.sh` | Master deployment script |
| `scripts/deployment/setup_n8n_hostinger.sh` | n8n server setup with SSL |
| `scripts/deployment/setup_ssl_hostinger.sh` | SSL/TLS with Let's Encrypt |

### **CI/CD**
| File | Purpose |
|------|---------|
| `.github/workflows/deploy-mission-control.yml` | GitHub Actions CI/CD pipeline |

### **Integration**
| File | Purpose |
|------|---------|
| `config/integrations.yaml` | Updated with n8n + GitHub config |
| `skills/automation/n8n-integration/SKILL.md` | Skill documentation |
| `skills/automation/n8n-integration/n8n_integration.py` | Skill implementation |

---

## 🚀 **Quick Deployment**

### **1. On Hostinger VPS (as root)**

```bash
# Clone the repository
cd /opt
git clone https://github.com/YOUR_USERNAME/JARVIS_OS.git jarvis
cd jarvis

# Run master deployment (sets up everything)
chmod +x scripts/deployment/deploy_hostinger.sh
./scripts/deployment/deploy_hostinger.sh
```

### **2. Configure Environment**

```bash
# Copy and edit environment file
cp deploy/.env.example deploy/.env
nano deploy/.env

# Required variables:
# DOMAIN=jarvis.yourdomain.com
# N8N_DOMAIN=n8n.yourdomain.com
# LETSENCRYPT_EMAIL=admin@yourdomain.com
# N8N_USER=admin
# N8N_PASSWORD=secure_password
# POSTGRES_PASSWORD=secure_password
# GITHUB_PAT=ghp_xxx
# HOSTINGER_HOST=your-vps-ip
# HOSTINGER_USER=root
# HOSTINGER_SSH_KEY=~/.ssh/id_ed25519
```

### **3. Setup SSL Certificates**

```bash
chmod +x scripts/deployment/setup_ssl_hostinger.sh
./scripts/deployment/setup_ssl_hostinger.sh
```

### **4. Configure GitHub Secrets**

Add to GitHub repository settings → Secrets → Actions:

| Secret | Value |
|--------|-------|
| `HOSTINGER_HOST` | Your VPS IP |
| `HOSTINGER_USER` | root |
| `HOSTINGER_SSH_KEY` | Private SSH key |
| `HOSTINGER_PORT` | 65002 (or 22) |
| `DISCORD_WEBHOOK_URL` | Optional |
| `SLACK_WEBHOOK_URL` | Optional |
| `TELEGRAM_BOT_TOKEN` | Optional |
| `TELEGRAM_CHAT_ID` | Optional |

---

## 🔧 **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    HOSTINGER VPS                            │
├─────────────────────────────────────────────────────────────┤
│  NGINX (Port 80/443)                                        │
│    ├── jarvis.yourdomain.com  ──▶ Mission Control (8080)   │
│    ├── n8n.yourdomain.com     ──▶ n8n (5678)               │
│    └── /webhook/*             ──▶ n8n Webhooks             │
├─────────────────────────────────────────────────────────────┤
│  DOCKER COMPOSE SERVICES                                    │
│    ├── mission-control  (FastAPI + WebSocket)              │
│    ├── n8n              (Workflow Automation)              │
│    ├── postgres         (n8n Database)                     │
│    ├── redis            (n8n Queue/Cache)                  │
│    ├── nginx            (Reverse Proxy + SSL)              │
│    └── certbot          (Let's Encrypt Auto-renewal)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 **Access Points**

| Service | URL | Credentials |
|---------|-----|-------------|
| **Mission Control** | `https://jarvis.yourdomain.com` | None (public dashboard) |
| **Mission Control API** | `https://jarvis.yourdomain.com/api/` | API key if configured |
| **n8n Editor** | `https://n8n.yourdomain.com` | Basic Auth (N8N_USER/N8N_PASSWORD) |
| **n8n API** | `https://n8n.yourdomain.com/api/v1/` | X-N8N-API-KEY header |
| **Webhooks** | `https://n8n.yourdomain.com/webhook/*` | Public endpoints |

---

## 🤖 **JARVIS Agent Integration**

### **Available n8n Tools**
```python
# List workflows
await n8n_list_workflows()

# Execute workflow
await n8n_execute_workflow(workflow_id="abc", data={"task": "backup"})

# Trigger webhook
await n8n_trigger_webhook(webhook_path="jarvis/trigger", data={...})

# Get execution status
await n8n_get_execution(execution_id="exec_123")

# Manage workflows
await n8n_activate_workflow(workflow_id="abc")
await n8n_deactivate_workflow(workflow_id="abc")
```

### **Agent Use Cases**

| Agent | n8n Workflows |
|-------|---------------|
| **Metatron** | Brain sync, knowledge indexing, vector DB updates |
| **Gabriel** | Send notifications, post to social media |
| **Uriel** | Research workflows, data collection |
| **Michael** | Strategic planning, task orchestration |
| **Azrael** | Cleanup, archival, backup workflows |
| **Tattoo Business** | Booking, client management, invoices, reminders |

---

## 🔄 **Common Workflows to Create in n8n**

### **1. Daily Report Generation**
```
Cron (7:00 AM) → HTTP Request (Mission Control /api/financial) 
  → Format Data → Send Email/Telegram → Log to Database
```

### **2. Brain Sync**
```
Cron (Every 5 min) → HTTP Request (JARVIS brain sync endpoint)
  → Verify Sync → Update Status → Alert on Failure
```

### **3. Backup Automation**
```
Cron (3:00 AM) → HTTP Request (Backup Service) 
  → Verify Upload → Notify on Success/Failure
```

### **4. Security Scan**
```
Cron (2:00 AM) → Run Security Audit Script
  → Parse Results → Create Issues → Alert on Critical
```

### **5. Tattoo Business - Appointment Reminders**
```
Cron (Every hour) → Query Calendar → Filter Upcoming
  → Send SMS/Email → Update Status
```

### **6. Client Onboarding**
```
Webhook (/webhook/client/new) → Create in CRM
  → Send Welcome Email → Create Calendar Event → Notify Team
```

---

## 🛠️ **Management Commands**

```bash
# Check status
cd /opt/jarvis/deploy
docker-compose ps

# View logs
docker-compose logs -f mission-control
docker-compose logs -f n8n
docker-compose logs -f nginx

# Restart services
docker-compose restart mission-control
docker-compose restart n8n

# Update and redeploy
docker-compose pull
docker-compose up -d --remove-orphans

# Backup n8n data
docker exec jarvis-postgres pg_dump -U n8n n8n > backup_$(date +%Y%m%d).sql

# Renew SSL manually
certbot renew --post-hook "systemctl reload nginx"
```

---

## 🔒 **Security Checklist**

- [ ] Change default passwords in `.env`
- [ ] Configure firewall (UFW): `ufw allow 80,443,22,65002/tcp`
- [ ] Enable fail2ban for SSH
- [ ] Set up monitoring (Prometheus/Grafana or Datadog)
- [ ] Configure backup retention
- [ ] Test disaster recovery
- [ ] Rotate API keys quarterly
- [ ] Review n8n execution logs regularly

---

## 📞 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| Mission Control not loading | Check `docker-compose logs mission-control` |
| n8n 502 Bad Gateway | Check `docker-compose logs n8n`, verify PostgreSQL |
| SSL certificate errors | Run `./scripts/deployment/setup_ssl_hostinger.sh` |
| Webhook not working | Check n8n webhook URL, verify nginx config |
| GitHub Actions failing | Check secrets, verify SSH key permissions |

---

## 📚 **Next Steps**

1. **Create n8n workflows** for your automation needs
2. **Connect JARVIS agents** using the n8n integration skill
3. **Set up monitoring** with health check endpoints
4. **Configure backups** for n8n database and JARVIS brains
5. **Add custom domains** for each service if needed

---

**Deployment complete!** 🎉

Your JARVIS Mission Control and n8n automation server are now live on Hostinger with:
- ✅ HTTPS/SSL via Let's Encrypt
- ✅ Reverse proxy with WebSocket support
- ✅ CI/CD via GitHub Actions
- ✅ n8n workflow automation
- ✅ JARVIS agent integration
- ✅ Auto-renewing certificates