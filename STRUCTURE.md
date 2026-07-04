# J.A.R.V.I.S. OS — Unified Directory Structure

```
/opt/data/JARVIS_OS/
├── core/                           # Core system files
│   ├── jarvis_core.py              # Main JARVIS class
│   ├── session_manager.py          # Session lifecycle
│   ├── config_loader.py            # Configuration management
│   ├── memory_manager.py           # Dual-brain + vector sync
│   ├── agent_orchestrator.py       # Sub-agent management
│   ├── security.py                 # Prompt injection, auth
│   └── __init__.py
│
├── brains/                         # Dual-brain architecture
│   ├── obsidian/                   # Obsidian Brain (Raw Knowledge)
│   │   ├── config/                 # Core configs (Soul, User, Agent, Tools, etc.)
│   │   ├── skills/                 # Skill implementations & references
│   │   ├── projects/               # Project files & specs
│   │   ├── code/                   # Code snippets, modules, libraries
│   │   ├── raw_data/               # Unprocessed research, logs, dumps
│   │   ├── clients/                # Client profiles & history
│   │   ├── workflow/               # Documented workflows & SOPs
│   │   ├── guides/                 # How-to guides & tutorials
│   │   ├── prices/                 # Pricing models & quotes
│   │   ├── preferences/            # Deep user preferences
│   │   └── content_style/          # Writing/style guidelines
│   │
│   ├── holographic/                # Holographic Brain (Applied Knowledge)
│   │   ├── case_studies/           # Completed projects with outcomes
│   │   ├── scenarios/              # What-if simulations
│   │   ├── historical_tasks/       # Task history with results
│   │   ├── outcomes/               # Measured results & metrics
│   │   └── applied_knowledge/      # Synthesized, actionable wisdom
│   │
│   └── vector/                     # Vector Memory (ChromaDB)
│       ├── chroma_db/              # ChromaDB persistence
│       ├── embeddings/             # Embedding model cache
│       ├── index/                  # Search indices
│       └── rag_engine/             # RAG query pipeline
│
├── agents/                         # 12 Archangel Agents + Specialized
│   ├── archangels/                 # The 12 biblical archetype agents
│   │   ├── metatron/               # Brain AI / Memory Hub (Scribe)
│   │   ├── gabriel/                # Communication / Content (Messenger)
│   │   ├── raphael/                # Support / Healing (Healer)
│   │   ├── uriel/                  # Research / Analysis (Illuminator)
│   │   ├── sandalphon/             # Social / Community (Prayer Bearer)
│   │   ├── jophiel/                # Marketing / Beauty (Wisdom)
│   │   ├── michael/                # Leadership / Strategy (Protector)
│   │   ├── raguel/                 # Security / Compliance (Justice)
│   │   ├── remiel/                 # Creative / Vision (Thunder)
│   │   ├── sariel/                 # Knowledge / Learning (Command)
│   │   ├── azrael/                 # Archival / Cleanup (Transition)
│   │   └── chamuel/                # Relationships / Ops (Peace)
│   │
│   ├── openjarvis/                 # OpenJarvis built-in agents (8)
│   │   ├── simple/                 # Simple conversational agent
│   │   ├── deep_research/          # Deep research agent
│   │   ├── code_assistant/         # Coding assistant
│   │   ├── morning_digest/         # Morning briefing
│   │   ├── scheduled_monitor/      # Scheduled monitoring
│   │   └── ...
│   │
│   ├── factory/                    # Agent factory & spawner
│   │   ├── agent_template.py       # Base agent class
│   │   ├── spawn_all.py            # Spawn all 12 agents
│   │   └── agent_registry.json     # Active agent registry
│   │
│   └── specialized/                # Domain-specific agents
│       ├── tattoo_business/        # Great Sage Tattoos automation
│       ├── financial/              # Finance & revenue
│       ├── marketing/              # Marketing automation
│       └── security/               # Security monitoring
│
├── skills/                         # Skill library (Hermes-compatible)
│   ├── core/                       # Core system skills
│   │   ├── vector-memory-rag/      # RAG system
│   │   ├── voice-pipeline/         # STT/TTS/Wake/RVC
│   │   ├── security-hardening/     # System hardening
│   │   ├── archangel-agent-factory/ # 12-agent spawner
│   │   ├── hostinger-backup-sync/  # SCP backup automation
│   │   ├── cron-automation/        # Scheduled jobs
│   │   └── openjarvis-integration/ # OpenJarvis bridge
│   │
│   ├── research/                   # Research & analysis skills
│   │   ├── tavily-search/          # Tavily web search
│   │   ├── stealth-browser-pro/    # Anti-bot browser
│   │   ├── bug-bounty-hunting/     # Security research
│   │   ├── osint-deep-research/    # OSINT workflows
│   │   └── arxiv-research/         # Academic paper search
│   │
│   ├── development/                # Development skills
│   │   ├── code-self-audit/        # Automated code review
│   │   ├── test-driven-development/ # TDD enforcement
│   │   ├── systematic-debugging/   # 4-phase debugging
│   │   └── simplify-code/          # Code cleanup
│   │
│   ├── creative/                   # Creative skills
│   │   ├── image-generation/       # FLUX/Stable Diffusion
│   │   ├── video-generation/       # Video creation
│   │   ├── design-system/          # UI/UX design
│   │   └── content-creation/       # Writing, copy
│   │
│   ├── business/                   # Business automation
│   │   ├── tattoo-booking/         # Appointment management
│   │   ├── client-management/      # CRM workflows
│   │   ├── invoice-generation/     # Billing automation
│   │   ├── social-media/           # Multi-platform posting
│   │   └── email-marketing/        # Campaign automation
│   │
│   └── infrastructure/             # Infra & DevOps
│       ├── docker-orchestration/   # Container management
│       ├── kubernetes/             # K8s operations
│       ├── monitoring/             # System monitoring
│       └── ci-cd/                  # Pipeline automation
│
├── config/                         # Unified configuration
│   ├── soul.md                     # Core identity & directives
│   ├── identity.md                 # Agent identity
│   ├── user.md                     # User profile (18 questions)
│   ├── agent.md                    # Agent configuration
│   ├── tools.md                    # Tool registry
│   ├── heartbeat.md                # Session tracking
│   ├── continuity.md               # Session bridge
│   ├── setup_tutorial.md           # Setup guide
│   ├── agents.md                   # Sub-agent registry
│   ├── integrations.yaml           # API keys & connections
│   ├── cron_jobs.yaml              # Scheduled jobs config
│   ├── voice.yaml                  # Voice pipeline config
│   ├── dashboard.yaml              # Mission Control config
│   └── security.yaml               # Security policies
│
├── services/                       # System services
│   ├── jarvis_daemon.py            # Main daemon
│   ├── mission_control/            # Dashboard backend (FastAPI)
│   │   ├── main.py                 # FastAPI app
│   │   ├── websocket.py            # Real-time updates
│   │   ├── panels/                 # 9 panel implementations
│   │   └── api/                    # REST endpoints
│   ├── voice_service/              # Voice pipeline service
│   │   ├── wake_word.py            # Porcupine wake detection
│   │   ├── stt.py                  # Whisper STT
│   │   ├── tts.py                  # Piper/Edge TTS
│   │   ├── rvc.py                  # RVC voice conversion
│   │   └── interrupt.py            # Real-time interruption
│   ├── brain_sync/                 # Dual-brain sync service
│   │   ├── obsidian_watcher.py     # File watcher
│   │   ├── holographic_synthesizer.py # Knowledge synthesis
│   │   └── vector_indexer.py       # ChromaDB indexer
│   ├── backup_service/             # Hostinger backup
│   │   ├── scp_sync.py             # SCP synchronization
│   │   ├── ssh_manager.py          # SSH key management
│   │   └── backup_scheduler.py     # Scheduled backups
│   ├── cron_service/               # Job scheduler
│   │   ├── scheduler.py            # Cron job runner
│   │   ├── jobs/                   # Job implementations
│   │   └── health_check.py         # System health
│   └── integration_service/        # External API integrations
│       ├── composio/               # Composio connections
│       ├── openrouter/             # OpenRouter models
│       ├── github/                 # GitHub operations
│       └── social/                 # Social media APIs
│
├── dashboard/                      # Mission Control Frontend
│   ├── src/                        # React/Vue/HTMX source
│   ├── public/                     # Static assets
│   ├── components/                 # UI components
│   │   ├── SystemHealth/           # CPU, RAM, GPU, Disk, Network
│   │   ├── AgentStatus/            # 12 agents status
│   │   ├── TaskQueue/              # Pending/running/completed
│   │   ├── MemoryGraph/            # Dual-brain sync visualization
│   │   ├── Financial/              # Revenue, expenses, forecasts
│   │   ├── Calendar/               # Today, week, conflicts
│   │   ├── Communications/         # Unread, priority items
│   │   ├── Research/               # Active deep-dive threads
│   │   └── Security/               # Threat level, scans
│   └── build/                      # Production build
│
├── voice/                          # Voice pipeline assets
│   ├── models/                     # TTS/STT/RVC models
│   │   ├── porcupine/              # Wake word models
│   │   ├── whisper/                # Whisper models
│   │   ├── piper/                  # Piper voices
│   │   └── rvc/                    # RVC voice models
│   ├── audio_cache/                # Generated audio cache
│   ├── recordings/                 # User recordings
│   └── jarvis_voice/               # Custom JARVIS voice
│
├── integrations/                   # Integration configurations
│   ├── composio/                   # Composio OAuth tokens
│   ├── api_keys/                   # Encrypted API keys (gitignored)
│   ├── webhooks/                   # Webhook endpoints
│   └── oauth/                      # OAuth tokens
│
├── backups/                        # Backup storage
│   ├── hostinger/                  # Hostinger SCP backups
│   ├── local/                      # Local snapshots
│   ├── git/                        # Git bundle backups
│   └── schedule/                   # Backup metadata
│
├── logs/                           # System logs
│   ├── jarvis/                     # Core daemon logs
│   ├── agents/                     # Agent activity logs
│   ├── skills/                     # Skill execution logs
│   ├── voice/                      # Voice pipeline logs
│   ├── brain_sync/                 # Sync operation logs
│   ├── backup/                     # Backup operation logs
│   ├── cron/                       # Scheduled job logs
│   ├── security/                   # Security audit logs
│   └── integration/                # API integration logs
│
├── scripts/                        # Utility scripts
│   ├── startup/                    # Boot scripts
│   │   ├── init_javis.sh           # Full system init
│   │   ├── start_daemon.sh         # Start JARVIS daemon
│   │   ├── start_dashboard.sh      # Start Mission Control
│   │   ├── start_voice.sh          # Start voice pipeline
│   │   └── start_all.sh            # Start everything
│   ├── shutdown/                   # Graceful shutdown
│   │   ├── stop_all.sh             # Stop everything
│   │   ├── backup_before_shutdown.sh
│   │   └── save_state.sh
│   ├── maintenance/                # Maintenance scripts
│   │   ├── nightly_audit.sh        # Code/security audit
│   │   ├── weekly_review.sh        # Weekly synthesis
│   │   ├── monthly_review.sh       # Monthly strategic
│   │   ├── prune_logs.sh           # Log rotation
│   │   └── verify_integrity.sh     # File integrity check
│   ├── deployment/                 # Deployment scripts
│   │   ├── deploy_hostinger.sh     # Hostinger deploy
│   │   ├── deploy_dashboard.sh     # Dashboard deploy
│   │   └── sync_brains.sh          # Brain synchronization
│   └── development/                # Dev utilities
│       ├── create_skill.sh         # Skill scaffolding
│       ├── spawn_agent.sh          # Agent spawning
│       ├── test_voice.sh           # Voice pipeline test
│       └── debug_agent.sh          # Agent debugging
│
├── docs/                           # Documentation
│   ├── architecture/               # System architecture docs
│   ├── api/                        # API reference
│   ├── guides/                     # User guides
│   ├── runbooks/                   # Operational runbooks
│   ├── skills/                     # Skill documentation
│   ├── agents/                     # Agent documentation
│   └── troubleshooting/            # Common issues
│
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   ├── e2e/                        # End-to-end tests
│   ├── voice/                      # Voice pipeline tests
│   ├── agents/                     # Agent behavior tests
│   └── fixtures/                   # Test fixtures
│
└── vector_db/                      # ChromaDB persistent storage
    ├── chroma.sqlite3
    └── collections/
```

## Symlink Strategy (for backward compatibility)

```
/opt/data/jarvis/           →  /opt/data/JARVIS_OS/brains/obsidian/
/opt/data/jarvis/config/    →  /opt/data/JARVIS_OS/config/
/opt/data/jarvis/skills/    →  /opt/data/JARVIS_OS/skills/
/opt/data/jarvis/agents/    →  /opt/data/JARVIS_OS/agents/
/opt/data/jarvis/logs/      →  /opt/data/JARVIS_OS/logs/
/opt/data/jarvis/voices/    →  /opt/data/JARVIS_OS/voice/
/opt/data/jarvis/vector_memory/ → /opt/data/JARVIS_OS/vector_db/
/opt/data/.hermes/          →  /opt/data/JARVIS_OS/ (Hermes profile)
```
