# J.A.R.V.I.S. OS

> **J.A.R.V.I.S. OS** — A unified AI operating system with dual-brain architecture, 12 specialized Archangel agents, real-time voice pipeline, and Mission Control dashboard.

[![Deploy to Fly.io](https://github.com/your-username/jarvis-os/actions/workflows/deploy.yml/badge.svg)](https://github.com/your-username/jarvis-os/actions/workflows/deploy.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### 🧠 Dual-Brain Architecture
- **Obsidian Brain** — Raw knowledge storage (config, skills, projects, code, clients)
- **Holographic Brain** — Applied wisdom (case studies, scenarios, outcomes)
- **Vector Memory** — ChromaDB + RAG for semantic search across both brains
- **Infinite Feedback Loop** — Continuous synchronization between all three

### 👼 12 Archangel Agents
| Agent | Archangel | Domain | Sintra Parallel |
|-------|-----------|--------|-----------------|
| Metatron | Metatron | Brain AI / Memory Hub | Brain AI |
| Gabriel | Gabriel | Communication / Content | Penn (Copywriter) |
| Raphael | Raphael | Support / Healing | Cassie (Support) |
| Uriel | Uriel | Research / Analysis | Dexter (Data) |
| Sandalphon | Sandalphon | Social / Community | Soshie (Social) |
| Jophiel | Jophiel | Marketing / Beauty | Emmie (Email) |
| Michael | Michael | Leadership / Strategy | Buddy (Biz Dev) |
| Raguel | Raguel | Security / Compliance | Security Spec |
| Remiel | Remiel | Creative / Vision | Vince (Video) |
| Sariel | Sariel | Knowledge / Learning | Scout (Research) |
| Azrael | Azrael | Archival / Cleanup | Archive Spec |
| Chamuel | Chamuel | Relationships / Ops | Milli (PM) |

### 🎙️ Voice Pipeline
- **Wake Word**: Porcupine ("Jarvis" / "Wake up Jarvis")
- **STT**: Whisper (local, base.en model)
- **TTS**: Piper (en_GB-alan-medium, British male)
- **RVC**: Optional voice conversion for JARVIS persona
- **Barge-in**: Real-time interruption handling via Silero VAD

### 📊 Mission Control Dashboard
9-panel real-time dashboard (FastAPI + WebSocket):
1. **System Health** — CPU, RAM, GPU, Disk, Network
2. **Agent Status** — 12 archangels + OpenJarvis agents
3. **Task Queue** — Pending/Running/Completed/Failed
4. **Memory Graph** — Dual-brain sync visualization
5. **Financial** — Revenue, expenses, forecasts
6. **Calendar** — Today/Week/Month views
7. **Communications** — Unread counts, priority items
8. **Research** — Active deep-dive threads
9. **Security** — Threat level, alerts, scans

### ⚙️ Automation
- **25+ Cron Jobs** — Health checks, daily reports, nightly audits, brain sync, backups
- **Hostinger Backup** — SCP encryption, 30-day retention
- **Security Hardening** — File integrity, audit logging, prompt injection defense

## 🚀 Quick Start

### Local Development
```bash
# Clone
git clone https://github.com/your-username/jarvis-os.git
cd jarvis-os

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# OR with uv (faster)
uv pip install -r requirements.txt

# Configure
cp config/integrations.yaml.example config/integrations.yaml
# Edit with your API keys

# Start all services
./scripts/startup/init_jarvis.sh start

# Open dashboard
open http://localhost:8080/dashboard
```

### Voice Commands
```
"Jarvis"                 # Wake word
"System status"          # Health check
"Run nightly audit"      # Trigger audit
"Spawn Gabriel"          # Activate agent
"What's my schedule?"    # Calendar check
"Generate daily report"  # Morning briefing
"Stop"                   # Cancel current task
```

## ☁️ Deploy to Fly.io (Free Tier)

### Prerequisites
- [Fly.io account](https://fly.io) (free, no credit card for trial)
- `flyctl` CLI installed

### One-Command Deploy
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch (creates fly.toml if needed)
fly launch --no-deploy

# Create persistent volume (3GB free)
fly volumes create jarvis_data --size 3 --region lax

# Set secrets (required for full functionality)
fly secrets set OPENROUTER_API_KEY=xxx
fly secrets set COMPOSIO_API_KEY=xxx
fly secrets set HOSTINGER_SSH_KEY="$(cat ~/.ssh/id_ed25519)"
fly secrets set PICOVOICE_ACCESS_KEY=xxx

# Deploy
fly deploy
```

### Your Live Dashboard
```
https://jarvis-os.fly.dev/dashboard
```

### Free Tier Limits
- 3 shared-CPU VMs (256MB RAM each)
- 3GB persistent volume
- 160GB outbound data/month
- No sleep — always on for cron/voice

## 📁 Project Structure

```
jarvis-os/
├── agents/                 # 12 Archangel agents + factory
├── brains/                 # Dual-brain architecture
│   ├── obsidian/           # Raw knowledge
│   ├── holographic/        # Applied wisdom
│   └── vector/             # ChromaDB
├── config/                 # All configuration (YAML + MD)
├── core/                   # Core system (jarvis_os.py, session_manager)
├── dashboard/              # Mission Control UI
│   └── public/index.html   # Single-file dashboard
├── deployment/             # Deployment configs
├── docs/                   # Architecture, runbooks, guides
├── integrations/           # External service integrations
├── scripts/                # Utility scripts (startup, maintenance)
├── services/               # Background services
│   ├── brain_sync/         # Dual-brain synchronization
│   ├── mission_control/    # Dashboard backend
│   ├── voice_service/      # Voice pipeline
│   ├── backup_service/     # Hostinger SCP backup
│   ├── cron_service/       # Scheduled jobs
│   └── agent_orchestrator/ # Sub-agent management
├── skills/                 # Reusable procedures (6 categories)
├── tests/                  # Test suite
├── vector_db/              # ChromaDB persistence
├── voice/                  # Voice models & cache
├── .github/workflows/      # CI/CD pipelines
├── Dockerfile              # Multi-stage Docker build
├── fly.toml               # Fly.io configuration
├── pyproject.toml          # Python package config
├── requirements.txt        # Python dependencies
└── README.md
```

## 🔧 Configuration

### Required API Keys (set as Fly.io secrets or `.env`)
```bash
# AI Providers
OPENROUTER_API_KEY=           # OpenRouter for 100+ models
ANTHROPIC_API_KEY=            # Claude
OPENAI_API_KEY=               # GPT-4o, embeddings
GROQ_API_KEY=                 # Fast inference
GEMINI_API_KEY=               # Google Gemini

# Voice
PICOVOICE_ACCESS_KEY=         # Porcupine wake word (free tier: 3 keywords)

# Integrations
COMPOSIO_API_KEY=             # 100+ tool integrations
GITHUB_TOKEN=                 # GitHub API
HOSTINGER_SSH_KEY=            # Backup server (ed25519 private key)
HOSTINGER_HOST=               # e.g., "srv123.hostinger.com"
HOSTINGER_USER=               # e.g., "u1234567"
HOSTINGER_PATH=               # e.g., "/home/u1234567/jarvis_backups"

# Optional
STRIPE_API_KEY=               # Financial reporting
SQUARE_API_KEY=               # Financial reporting
GOOGLE_CLIENT_ID=             # Calendar/Gmail
GOOGLE_CLIENT_SECRET=
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/OVERVIEW.md)
- [Operational Runbooks](docs/runbooks/OPERATIONS.md)
- [Quickstart Guide](docs/guides/QUICKSTART.md)
- [API Reference](docs/api/REFERENCE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a PR

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Nous Research** — Hermes Agent framework
- **Fly.io** — Generous free tier hosting
- **Porcupine** — Wake word engine
- **Whisper** — OpenAI STT
- **Piper** — Local TTS
- **ChromaDB** — Vector database
- **Sentence Transformers** — Embeddings

---

**Built with precision for Angel (Sir) — Founder, The Great Sage Tattoos and Tarot**

*J.A.R.V.I.S. OS — Your calm intelligence in the room.*