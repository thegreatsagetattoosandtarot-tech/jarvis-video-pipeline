# J.A.R.V.I.S. OS - Architecture Documentation

## System Overview

J.A.R.V.I.S. OS is a unified AI operating system built on a dual-brain architecture with 12 specialized archangel agents, real-time voice pipeline, mission control dashboard, and automated backup/cron systems.

```
┌─────────────────────────────────────────────────────────────────┐
│                        J.A.R.V.I.S. OS                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  OBSIDIAN    │  │ HOLOGRAPHIC  │  │    VECTOR MEMORY     │  │
│  │   BRAIN      │◄─►│   BRAIN      │◄─►│    (ChromaDB)        │  │
│  │  (Raw Data)  │  │ (Applied)    │  │    (RAG Engine)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         ▲                ▲                   ▲                  │
│         └────────────────┼───────────────────┘                  │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    CORE SERVICES                           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │  │
│  │  │ Brain    │ │ Voice    │ │ Mission  │ │ Agent      │  │  │
│  │  │ Sync     │ │ Pipeline │ │ Control  │ │ Orchestr.  │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ▲                                      │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 12 ARCHANGEL│  │  INTEGRATION│  │  AUTOMATION │             │
│  │   AGENTS    │  │   SERVICES  │  │   (CRON)    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Dual-Brain Architecture

**Obsidian Brain** (`/brains/obsidian/`) - Raw Knowledge Storage
- `config/` - Core configuration files (Soul, User, Agent, Tools, etc.)
- `skills/` - Reusable procedures and implementations
- `projects/` - Project specifications and files
- `code/` - Code snippets, modules, libraries
- `raw_data/` - Unprocessed research, logs, dumps
- `clients/` - Client profiles and history
- `workflow/` - Documented workflows and SOPs
- `guides/` - How-to guides and tutorials
- `prices/` - Pricing models and quotes
- `preferences/` - Deep user preferences
- `content_style/` - Writing/style guidelines

**Holographic Brain** (`/brains/holographic/`) - Applied Knowledge
- `case_studies/` - Completed projects with outcomes
- `scenarios/` - What-if simulations
- `historical_tasks/` - Task history with results
- `outcomes/` - Measured results and metrics
- `applied_knowledge/` - Synthesized, actionable wisdom

**Vector Memory** (`/vector_db/`) - Semantic Search & RAG
- ChromaDB persistent storage
- Embedding model: all-MiniLM-L6-v2 (384-dim)
- Collection: `jarvis_dual_brain`
- RAG pipeline for grounded answers

**Feedback Loop** - Continuous synchronization:
- Obsidian → Holographic: Raw data becomes applied wisdom
- Holographic → Obsidian: Patterns become new structures
- Both → Vector: All content indexed for semantic search

### 2. 12 Archangel Agents

Each agent embodies a biblical archangel archetype with specialized domain expertise:

| Agent | Archangel | Role | Sintra Parallel | Tools |
|-------|-----------|------|-----------------|-------|
| Metatron | Metatron | Brain AI / Memory Hub | Brain AI | vector_memory, rag, knowledge_sync |
| Gabriel | Gabriel | Communication / Content | Penn (Copywriter) | web_search, content_gen, copywriting |
| Raphael | Raphael | Support / Healing | Cassie (Support) | email, ticketing, empathy_engine |
| Uriel | Uriel | Research / Analysis | Dexter (Data) | data_analysis, research, forecasting |
| Sandalphon | Sandalphon | Social / Community | Soshie (Social) | social_media, engagement, analytics |
| Jophiel | Jophiel | Marketing / Beauty | Emmie (Email) | email_marketing, campaigns, A/B |
| Michael | Michael | Leadership / Strategy | Buddy (Biz Dev) | strategic_planning, competitive_intel |
| Raguel | Raguel | Security / Compliance | Security Spec | security_audit, compliance, threat_model |
| Remiel | Remiel | Creative / Vision | Vince (Video) | video_gen, editing, motion_graphics |
| Sariel | Sariel | Knowledge / Learning | Scout (Research) | deep_research, OSINT, fact_checking |
| Azrael | Azrael | Archival / Cleanup | Archive Spec | data_archival, lifecycle, retention |
| Chamuel | Chamuel | Relationships / Ops | Milli (PM) | project_mgmt, CRM, workflow_opt |

### 3. Voice Pipeline

```
[Wake Word: Porcupine] → [STT: Whisper] → [Intent Parser] → [JARVIS Core] → [TTS: Piper] → [Audio Out]
                              ↓
                    [Interrupt Handler: Silero VAD] ← Real-time barge-in
```

Components:
- **Wake Word**: Porcupine ("Jarvis" / "Wake up Jarvis")
- **STT**: Whisper (local, base.en model)
- **TTS**: Piper (en_GB-alan-medium, British male)
- **RVC**: Optional voice conversion for JARVIS persona
- **VAD**: Silero for interruption detection

### 4. Mission Control Dashboard

9-panel real-time dashboard (FastAPI + WebSocket):

1. **System Health** - CPU, RAM, GPU, Disk, Network
2. **Agent Status** - 12 archangels + OpenJarvis agents
3. **Task Queue** - Pending/Running/Completed/Failed
4. **Memory Graph** - Dual-brain sync visualization
5. **Financial** - Revenue, expenses, forecasts
6. **Calendar** - Today/Week/Month views
7. **Communications** - Unread counts, priority items
8. **Research** - Active deep-dive threads
9. **Security** - Threat level, alerts, scans

### 5. Service Layer

```
services/
├── brain_sync/         # Dual-brain synchronization
├── mission_control/    # Dashboard backend (FastAPI)
├── voice_service/      # Voice pipeline service
├── backup_service/     # Hostinger SCP backup
├── cron_service/       # Scheduled job runner
├── integration_service/# External API integrations
└── agent_orchestrator/ # Sub-agent management
```

## Data Flow

```
User Input (Voice/Text)
         │
         ▼
┌────────────────────────┐
│
│
│   Intent Parser        ││
│   (Hermes + Custom)    ││
└──────────┬─────────────┘│
           │
           ▼
┌────────────────────────┐│
│  Agent Orchestrator    ││
│  (Routes to agent)     ││
└──────────┬─────────────┘│
           │
     ┌─────┴─────┐
     ▼           ▼
┌────────┐ ┌────────┐
│Archangel│ │OpenJarvis│
│Agents   │ │Agents   │
└────┬────┘ └────┬────┘
     │           │
     └─────┬─────┘
           ▼
┌────────────────────────┐│
│  Dual-Brain Memory     ││
│  (Obsidian + Holographic││
│   + Vector RAG)        ││
└──────────┬─────────────┘│
           │
           ▼
┌────────────────────────┐│
│  Response Generator    ││
│  (TTS for voice)       ││
└────────────────────────┘│
```

## Security Architecture

- **Prompt Injection Defense**: Only direct user prompts processed
- **API Key Security**: Environment variables only, never in files
- **Sub-Agent Verification**: All external calls verified before confirmation
- **Cross-Profile Guard**: Blocks cross-profile writes by default
- **Production Lock**: Explicit auth for system modifications
- **Audit Logging**: All security events logged to `/logs/security/`
- **Integrity Monitoring**: SHA256 hashes for critical files
- **Network Policy**: Allowlist for outbound domains

## Deployment

### Requirements
- Linux (tested on Ubuntu 22.04+)
- Python 3.11+
- Ollama for local LLMs
- 8GB+ RAM recommended
- 50GB+ disk space

### Quick Start
```bash
# Clone and setup
cd /opt/data/JARVIS_OS
./scripts/startup/init_jarvis.sh

# Or start individual services
python3 -m services.mission_control.main  # Dashboard on :8080
python3 -m services.voice_service.main    # Voice pipeline
python3 -m services.brain_sync.brain_sync_service  # Brain sync
python3 -m services.cron_service.scheduler  # Cron jobs
python3 -m services.backup_service.main  # Backup service
```

### Configuration
All configuration in `/config/`:
- `integrations.yaml` - API keys and connections
- `cron_jobs.yaml` - Scheduled jobs
- `dashboard.yaml` - Dashboard panels
- `voice.yaml` - Voice pipeline settings
- `security.yaml` - Security policies

## Monitoring & Operations

### Health Checks
- Dashboard: `GET http://localhost:8080/health`
- Voice: `GET http://localhost:8082/health`
- All services log to `/logs/<service>/`

### Logs
```
/logs/
├── jarvis/          # Core daemon
├── agents/          # Agent activity
├── skills/          # Skill execution
├── voice/           # Voice pipeline
├── brain_sync/      # Sync operations
├── backup/          # Backup operations
├── cron/            # Scheduled jobs
├── security/        # Security audit
├── integration/     # API integrations
└── daily_reports/   # Morning briefings
```

### Backup
- Daily SCP to Hostinger at 4:00 AM
- Retention: 30 days
- Includes: config, brains, vector_db, skills, scripts, agents
- Encryption: Optional (age/gpg)

## Extending JARVIS OS

### Adding a Skill
1. Create in `/skills/<category>/<skill-name>/`
2. Include `SKILL.md` with frontmatter
3. Register in agent's toolset
4. Test and document

### Adding an Agent
1. Create in `/agents/archangels/<name>/`
2. Extend `ArchangelAgent` base class
3. Define personality, tools, domain
4. Register in `agent_registry.json`
5. Add to spawn_all.py

### Adding Integration
1. Add to `integrations.yaml`
2. Create service module in `/services/integration_service/`
3. Add to cron jobs if scheduled
4. Test with dry-run mode

---

*Document Version: 1.0*
*Last Updated: 2026-06-29*
*J.A.R.V.I.S. OS Unified Architecture*