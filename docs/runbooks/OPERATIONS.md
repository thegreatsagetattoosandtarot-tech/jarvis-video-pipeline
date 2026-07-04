# J.A.R.V.I.S. OS - Operational Runbooks

## Table of Contents
1. [Daily Operations](#daily-operations)
2. [Weekly Maintenance](#weekly-maintenance)
3. [Monthly Review](#monthly-review)
4. [Incident Response](#incident-response)
5. [Backup & Recovery](#backup--recovery)
6. [Service Management](#service-management)
7. [Scaling & Performance](#scaling--performance)

---

## Daily Operations

### Morning Startup (Automated at 6:00 AM)
- System health check
- Weather forecast
- Stock market pre-market
- Task queue summary
- Calendar review
- Financial summary

### Manual Daily Checks
```bash
# Check all services running
/opt/data/JARVIS_OS/scripts/startup/init_jarvis.sh status

# View dashboard
# Open http://localhost:8080

# Check voice pipeline
# Say "Jarvis" and verify response

# Review overnight logs
tail -f /opt/data/JARVIS_OS/logs/cron/cron_jobs.log
```

### End of Day
- Verify daily report generated
- Check backup completed (4:00 AM)
- Review any security alerts
- Update task priorities for tomorrow

---

## Weekly Maintenance (Monday 7:00 AM)

### Automated
- Weekly review generation
- Pattern analysis
- Performance trending
- Dependency update check

### Manual
```bash
# Full system audit
python3 /opt/data/JARVIS_OS/scripts/nightly_audit.py

# Security audit
python3 /opt/data/JARVIS_OS/scripts/security_audit.py

# Integrity check
python3 /opt/data/JARVIS_OS/scripts/integrity_check.py --verify

# Log rotation
python3 /opt/data/JARVIS_OS/scripts/log_rotate.py --max-age 30 --max-size 100

# Clean old backups
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --cleanup
```

### Review Items
- [ ] Agent performance metrics
- [ ] Task completion rates
- [ ] Voice pipeline accuracy
- [ ] Dashboard uptime
- [ ] Backup success rate
- [ ] Security audit findings
- [ ] Dependency updates needed

---

## Monthly Review (1st of Month, 8:00 AM)

### Automated
- Monthly strategic review
- Financial forecasting
- Architecture assessment
- Capacity planning

### Manual
```bash
# Full backup verification
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --verify

# Vector DB reindex
python3 /opt/data/JARVIS_OS/scripts/brain_sync/index_brains.py

# Update system packages
apt update && apt upgrade -y

# Update Python packages
pip list --outdated --format=json | python3 -c "
import json, sys
for pkg in json.load(sys.stdin):
    print(pkg['name'])
" | xargs pip install --upgrade

# Ollama model updates
ollama pull qwen3:0.6b
ollama pull llama3.1:8b
```

### Strategic Review
- [ ] Quarterly goal progress
- [ ] Revenue vs automation targets
- [ ] New skill/agent requirements
- [ ] Infrastructure scaling needs
- [ ] Security posture assessment
- [ ] User experience improvements

---

## Incident Response

### Severity Levels

| Level | Response Time | Escalation |
|-------|---------------|------------|
| Critical | Immediate | Page/Call |
| High | 15 min | Alert |
| Medium | 1 hour | Log |
| Low | Next business day | Log |

### Common Incidents

#### Service Down
```bash
# Check service status
/opt/data/JARVIS_OS/scripts/startup/init_jarvis.sh status

# Restart specific service
/opt/data/JARVIS_OS/scripts/startup/init_jarvis.sh stop
# Wait 10 seconds
/opt/data/JARVIS_OS/scripts/startup/init_jarvis.sh start

# Check logs
tail -f /opt/data/JARVIS_OS/logs/<service>/<service>.log
```

#### Voice Pipeline Not Responding
```bash
# Check audio devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Restart voice service
pkill -f voice_service
python3 -m services.voice_service.main

# Test wake word
# Check Picovoice access key in config/voice.yaml
```

#### Dashboard Unavailable
```bash
# Check port 8080
netstat -tlnp | grep 8080

# Check mission control logs
tail -f /opt/data/JARVIS_OS/logs/mission_control/mission_control.log

# Restart
pkill -f mission_control
python3 -m services.mission_control.main
```

#### Backup Failed
```bash
# Check SSH connectivity
ssh -i /opt/data/JARVIS_OS/config/ssh/hostinger_key user@host

# Check disk space
df -h /opt/data/JARVIS_OS

# Manual backup
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --once

# Verify
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --verify
```

#### Agent Unresponsive
```bash
# Check agent status via dashboard
# Or check agent logs
tail -f /opt/data/JARVIS_OS/logs/agents/agent_<name>.log

# Restart agent orchestrator
pkill -f agent_orchestrator
python3 -m core.agent_orchestrator

# Re-spawn specific agent
python3 /opt/data/JARVIS_OS/agents/factory/spawn_all.py --agent <name>
```

#### Security Alert
```bash
# Check security logs
cat /opt/data/JARVIS_OS/logs/security/audit.log | tail -50

# Run security audit
python3 /opt/data/JARVIS_OS/scripts/security_audit.py

# Check integrity
python3 /opt/data/JARVIS_OS/scripts/integrity_check.py --verify

# If compromise suspected:
# 1. Stop all services
/opt/data/JARVIS_OS/scripts/shutdown/stop_all.sh
# 2. Restore from last known good backup
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --restore --backup-date latest
# 3. Rotate all API keys
# 4. Review access logs
```

---

## Backup & Recovery

### Backup Schedule
- **Daily Full**: 4:00 AM (SCP to Hostinger)
- **Retention**: 30 days
- **Scope**: config, brains, vector_db, skills, scripts, agents

### Manual Backup
```bash
# Full backup
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --once

# Dry run (test)
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --dry-run

# Verify backup
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --verify
```

### Recovery Procedures

#### Full System Restore
```bash
# 1. Stop all services
/opt/data/JARVIS_OS/scripts/shutdown/stop_all.sh

# 2. Restore from backup
python3 /opt/data/JARVIS_OS/skills/core/hostinger-backup-sync/restore_from_hostinger.py --backup-date latest

# 3. Verify integrity
python3 /opt/data/JARVIS_OS/scripts/integrity_check.py --verify

# 4. Restart services
/opt/data/JARVIS_OS/scripts/startup/init_jarvis.sh start
```

#### Selective Restore
```bash
# Restore only config
python3 /opt/data/JARVIS_OS/skills/core/hostinger-backup-sync/restore_from_hostinger.py --backup-date 2026-06-25 --only config

# Restore only brains
python3 /opt/data/JARVIS_OS/skills/core/hostinger-backup-sync/restore_from_hostinger.py --backup-date latest --only brains
```

#### Disaster Recovery (New Server)
```bash
# 1. Provision new server
# 2. Install dependencies
apt-get update && apt-get install -y python3 python3-pip git rsync ssh age gnupg

# 3. Clone JARVIS OS
git clone <repo> /opt/data/JARVIS_OS

# 4. Configure SSH to Hostinger
# Copy SSH key to /opt/data/JARVIS_OS/config/ssh/hostinger_key
chmod 600 /opt/data/JARVIS_OS/config/ssh/hostinger_key

# 5. Restore from backup
python3 /opt/data/JARVIS_OS/skills/core/hostinger-backup-sync/restore_from_hostinger.py --backup-date latest

# 6. Verify and start
python3 /opt/data/JARVIS_OS/scripts/integrity_check.py --verify
/opt/data/JARVIS_OS/scripts/startup/init_jarvis.sh start
```

---

## Service Management

### Start All Services
```bash
/opt/data/JARVIS_OS/scripts/startup/init_jarvis.sh start
```

### Stop All Services
```bash
/opt/data/JARVIS_OS/scripts/shutdown/stop_all.sh
```

### Restart Services
```bash
/opt/data/JARVIS_OS/scripts/startup/init_jarvis.sh restart
```

### Individual Service Control
```bash
# Mission Control Dashboard
python3 -m services.mission_control.main
# Access: http://localhost:8080

# Voice Pipeline
python3 -m services.voice_service.main

# Brain Sync
python3 -m services.brain_sync.brain_sync_service

# Cron Service
python3 -m services.cron_service.scheduler

# Backup Service
python3 -m services.backup_service.main

# Agent Orchestrator
python3 -m core.agent_orchestrator
```

### Service Logs
```bash
# View all logs
ls /opt/data/JARVIS_OS/logs/

# Tail specific service
tail -f /opt/data/JARVIS_OS/logs/<service>/<service>.log

# View cron job logs
tail -f /opt/data/JARVIS_OS/logs/cron/cron_jobs.log
```

---

## Scaling & Performance

### Vertical Scaling
- Increase RAM for larger models
- Add GPU for faster inference
- Expand disk for more logs/backups

### Horizontal Scaling
- Run agents on separate machines
- Use message queue (Redis/RabbitMQ)
- Load balance dashboard

### Performance Tuning

#### Voice Pipeline
- Use `faster-whisper` for lower latency
- Enable CUDA for Whisper/Piper
- Reduce sample rate for faster processing

#### Vector DB
- Use HNSW index for faster search
- Increase batch size for indexing
- Consider pgvector for production scale

#### Dashboard
- Enable Redis caching for metrics
- Use WebSocket compression
- Implement data pagination

### Monitoring Metrics
- CPU/Memory/Disk/Network
- Agent response times
- Voice pipeline latency
- Backup duration/size
- Task queue depth
- Error rates by service

---

## Contact & Escalation

### Primary
- **System Owner**: Angel (Sir)
- **Timezone**: MST (UTC-7)
- **Hours**: 8am-8pm MST

### Emergency Procedures
1. Stop all services: `stop_all.sh`
2. Assess damage from logs
3. Restore from backup if needed
4. Rotate credentials if compromised
5. Document incident in holographic brain

---

*Runbook Version: 1.0*
*Last Updated: 2026-06-29*
*J.A.R.V.I.S. OS Operational Runbooks*