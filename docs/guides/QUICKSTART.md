# J.A.R.V.I.S. OS - Quickstart Guide

## Prerequisites

- Linux (Ubuntu 22.04+, Debian 12+, or similar)
- Python 3.11+
- 8GB+ RAM (16GB recommended for local LLMs)
- 50GB+ free disk space
- Internet connection (for initial setup)

## Installation

### 1. Clone Repository
```bash
git clone <your-repo> /opt/data/JARVIS_OS
cd /opt/data/JARVIS_OS
```

### 2. Run Initialization
```bash
chmod +x scripts/startup/init_jarvis.sh
./scripts/startup/init_jarvis.sh
```

This will:
- Check prerequisites
- Start Ollama (local LLMs)
- Initialize all services in order:
  1. JARVIS Daemon (core)
  2. Brain Sync (dual-brain)
  3. Mission Control Dashboard (port 8080)
  4. Voice Pipeline
  5. Agent Orchestrator
  6. Cron Service
  4. Backup Service

### 3. Verify Installation
```bash
# Check all services
./scripts/startup/init_jarvis.sh status

# Open dashboard
# Navigate http://localhost:8080

# Test voice
 Say "Jarvis" - should respond
```

## First Configuration

### 1. Configure API Keys
Edit `/opt/data/JARVIS_OS/config/integrations.yaml` with your keys:
```yaml
integrations:
  openrouter:
    enabled: true
    api_key: "your-openrouter-key"
  composio:
    enabled: true
    api_key: "your-composio-key"
  github:
    enabled: true
    token: "your-github-pat"
  # ... etc
```

### 2. Configure Hostinger Backup
```bash
# Generate SSH key for Hostinger
ssh-keygen -t ed25519 -f /opt/data/JARVIS_OS/config/ssh/hostinger_key -N ""

# Add public key to Hostinger authorized_keys
cat /opt/data/JARVIS_OS/config/ssh/hostinger_key.pub

# Edit backup config
nano /opt/data/JARVIS_OS/config/hostinger_backup.json
```

### 3. Set Custom Wake Word (Optional)
1. Go to https://console.picovoice.ai/
2. Create free account (3 custom keywords)
3. Create keyword: "Wake up Jarvis"
4. Download .ppn file for Linux
5. Place at `/opt/data/JARVIS_OS/voice/models/porcupine/wake_up_jarvis_linux.ppn`
6. Update `config/voice.yaml` with custom keyword path

### 4. Complete User Profile
```bash
nano /opt/data/JARVIS_OS/config/user.md
```
Fill in all 18 questions for personalized experience.

## Basic Usage

### Voice Commands
```
"Jarvis"                    # Wake word
"System status"             # Health check
"Run nightly audit"         # Trigger audit
"Spawn Gabriel"             # Activate agent
"What's my schedule?"       # Calendar check
"Generate daily report"     # Morning briefing
"Stop"                      # Cancel current task
```

### Dashboard
Open http://localhost:8080 for Mission Control with 9 panels:
1. System Health
2. Agent Status
3. Task Queue
4. Memory Graph
5. Financial
6. Calendar
7. Communications
8. Research
9. Security

### Agent Interaction
```bash
# List agents
python3 /opt/data/JARVIS_OS/agents/factory/spawn_all.py --list

# Spawn specific agent
python3 /opt/data/JARVIS_OS/agents/factory/spawn_all.py --agent metatron

# Spawn all
python3 /opt/data/JARVIS_OS/agents/factory/spawn_all.py --spawn-all
```

### Run Manual Jobs
```bash
# Daily report
python3 /opt/data/JARVIS_OS/scripts/daily_report.py

# Nightly audit
python3 /opt/data/JARVIS_OS/scripts/nightly_audit.py

# Security audit
python3 /opt/data/JARVIS_OS/scripts/security_audit.py

# Backup now
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --once

# Verify backup
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --verify
```

## Directory Structure
```
/opt/data/JARVIS_OS/
├── config/                 # All configuration files
├── brains/
│   ├── obsidian/           # Raw knowledge
│   ├── holographic/        # Applied knowledge
│   └── vector/             # ChromaDB
├── agents/
│   ├── archangels/         # 12 specialized agents
│   ├── factory/            # Agent spawner
│   └── specialized/        # Domain agents
├── skills/
│   ├── core/               # System skills
│   ├── research/           # Research skills
│   ├── development/        # Dev skills
│   ├── creative/           # Creative skills
│   ├── business/           # Business automation
│   └── infrastructure/     # DevOps skills
├── services/               # Background services
├── scripts/                # Utility scripts
├── dashboard/              # Mission Control UI
├── voice/                  # Voice models & cache
├── logs/                   # All service logs
├── backups/                # Local backup staging
└── docs/                   # Documentation
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
tail -f /opt/data/JARVIS_OS/logs/<service>/<service>.log

# Check port conflicts
netstat -tlnp | grep <port>

# Restart service
pkill -f <service>
python3 -m services.<service>.main
```

### Voice Not Working
```bash
# Test audio devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Check Picovoice key
grep access_key /opt/data/JARVIS_OS/config/voice.yaml

# Test wake word
python3 /opt/data/JARVIS_OS/skills/core/voice-pipeline/wake_porcupine.py
```

### Dashboard Blank
```bash
# Check API
curl http://localhost:8080/api/all

# Check WebSocket
# Open browser dev tools → Network → WS

# Restart
pkill -f mission_control
python3 -m services.mission_control.main
```

### Backup Failing
```bash
# Test SSH
ssh -i /opt/data/JARVIS_OS/config/ssh/hostinger_key user@host

# Check disk space
df -h /opt/data/JARVIS_OS

# Manual test
python3 /opt/data/JARVIS_OS/services/backup_service/backup_scheduler.py --dry-run
```

## Next Steps

1. **Complete user.md** - Fill all 18 questions
2. **Add API keys** - OpenRouter, Composio, GitHub, etc.
3. **Configure Hostinger** - Add SSH key to server
4. **Test voice pipeline** - Say "Jarvis"
5. **Review dashboard** - Check all 9 panels
6. **Run first audit** - `nightly_audit.py`
7. **Schedule cron jobs** - Already configured, verify in dashboard
8. **Build first skill** - Check `/skills/core/` for examples

## Support

- Documentation: `/opt/data/JARVIS_OS/docs/`
- Architecture: `docs/architecture/OVERVIEW.md`
- Runbooks: `docs/runbooks/OPERATIONS.md`
- Logs: `/opt/data/JARVIS_OS/logs/`

---

*Quickstart Version: 1.0*
*J.A.R.V.I.S. OS Unified System*