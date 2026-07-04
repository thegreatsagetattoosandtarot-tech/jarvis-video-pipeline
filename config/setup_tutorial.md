# J.A.R.V.I.S. Setup Tutorial

> **Welcome.** This tutorial walks you through initializing your J.A.R.V.I.S. system from zero to fully operational.

---

## Phase 1: Core Configuration (COMPLETE)

The following files have been created in `/opt/data/jarvis/config/` and mirrored to `/opt/data/jarvis/obsidian_brain/config/`:

| File | Purpose | Status |
|------|---------|--------|
| `soul.md` | Core identity, directives, questionnaires | ✅ Created |
| `identity.md` | Agent identity configuration | ✅ Created |
| `user.md` | **YOUR PROFILE — NEEDS YOUR INPUT** | 📝 Template ready |
| `agent.md` | Agent configuration & architecture | ✅ Created |
| `tools.md` | Tool registry & integration targets | ✅ Created |
| `heartbeat.md` | Session tracking & health | ✅ Created |
| `continuity.md` | Session-to-session bridge | ✅ Created |

---

## Phase 2: Complete Your User Profile (REQUIRED)

**Action Required**: Edit `/opt/data/jarvis/config/user.md` with your answers.

### The 18 Questions:

1. **Name & Address**: What's your name? What should J.A.R.V.I.S. call you?
2. **Timezone**: (e.g., UTC-5, EST, PST, GMT+1)
3. **Pronouns**: (he/him, she/her, they/them, etc.)
4. **Role/Title**: What's your professional role?
5. **Business**: What does your business do? (One sentence)
6. **Current Projects**: What are you working on now?
7. **Tech Stack**: Tools, platforms, languages you use daily
8. **Work Hours**: When do you typically work?
9. **Response Style**: Concise or detailed?
10. **Formatting**: Bullets, prose, code blocks, tables?
11. **Tone**: Casual, formal, or balanced?
12. **Response Length**: Short, medium, comprehensive?
13. **Quarterly Priorities**: Top 3-5 goals this quarter
14. **AI Frustrations**: What annoys you about AI responses?
15. **Recurring Preferences**: What should J.A.R.V.I.S. always remember?
16. **Active Platforms**: Email, Slack, X, Discord, etc.
17. **Avoid List**: Words, phrases, styles to avoid
18. **Good Day**: What does a productive day look like?

**Once complete**, J.A.R.V.I.S. will have full context for every future interaction.

---

## Phase 3: Dual-Brain Architecture

### Obsidian Brain (Raw Knowledge)
```
/opt/data/jarvis/obsidian_brain/
├── config/           # Core configs (mirrored)
├── skills/           # Reusable procedures
├── projects/         # Project files & specs
├── code/             # Code snippets, modules
├── raw_data/         # Unprocessed research, logs
├── clients/          # Client profiles & history
├── workflow/         # Documented workflows
├── guides/           # How-to guides
├── prices/           # Pricing models
├── preferences/      # User preferences deep-dive
└── content_style/    # Writing/style guidelines
```

### Holographic Brain (Applied Knowledge)
```
/opt/data/jarvis/holographic_brain/
├── case_studies/     # Completed projects with outcomes
├── scenarios/        # What-if simulations
├── historical_tasks/ # Task history with results
├── outcomes/         # Measured results & metrics
└── applied_knowledge/ # Synthesized, actionable wisdom
```

### Feedback Loop
Both brains sync continuously:
- **Obsidian → Holographic**: Raw data becomes applied wisdom
- **Holographic → Obsidian**: Patterns become new structures
- **Result**: Compound intelligence growth

---

## Phase 4: Vector Memory & RAG (NEXT)

**Goal**: Semantic search across all memory with grounded answers.

### Implementation Plan:
1. Choose embedding model (local: sentence-transformers / remote: OpenAI/OpenRouter)
2. Create vector store (ChromaDB, FAISS, or pgvector)
3. Index all `.md` files in both brains
4. Build RAG pipeline: query → embed → retrieve → synthesize → answer
5. Expose as skill: `vector-memory-rag`

---

## Phase 5: Voice Pipeline (HIGH PRIORITY)

### Target Architecture:
```
[Wake Word] → [STT] → [Intent Parser] → [JARVIS Core] → [TTS] → [Audio Out]
                    ↓
            [Interrupt Handler] ← Real-time voice interruption
```

### Components Needed:
| Component | Options | Status |
|-----------|---------|--------|
| **Wake Word** | Porcupine, Precise, custom | 🔲 |
| **STT** | Whisper (local), Deepgram, AssemblyAI | 🔲 |
| **Intent Parsing** | Hermes native + custom | 🔲 |
| **TTS** | Coqui, ElevenLabs, Edge TTS, FAL | 🔲 |
| **Voice Emulation** | RVC, so-vits-svc, custom J.A.R.V.I.S. model | 🔲 |
| **Interrupt Handling** | VAD + streaming STT | 🔲 |

### J.A.R.V.I.S. Voice Target:
- **Style**: Paul Bettany — calm, measured, precise, British
- **Tone**: Professional butler, subtle wit
- **Latency**: <500ms end-to-end

---

## Phase 6: Mission Control Dashboard

### UI Stack Options:
| Approach | Pros | Cons |
|----------|------|------|
| **React + Tauri** | Native desktop, full control | More dev work |
| **Next.js + Electron** | Web tech, cross-platform | Electron overhead |
| **Streamlit** | Rapid Python UI | Limited customization |
| **FastAPI + HTMX** | Lightweight, Python-native | Less "app-like" |
| **Obsidian Plugin** | Integrates with knowledge base | Obsidian-only |

### Required Panels:
- System Health (CPU, RAM, GPU, Disk, Network)
- Agent Status (12 agents: active/idle/error)
- Task Queue (pending/running/completed)
- Memory Graph (dual-brain sync)
- Financial (revenue, expenses, forecasts)
- Calendar (today, week, conflicts)
- Communications (unread, priority)
- Research (active threads)
- Security (threat level, scans)

---

## Phase 7: 12 Archangel Agents (Sintra AI Architecture)

### Agent Factory Skill: `archangel-agent-factory`

| # | Agent | Archangel | Domain | Sintra Parallel |
|---|-------|-----------|--------|-----------------|
| 1 | **Metatron** | Metatron | Brain AI / Memory Hub | Brain AI |
| 2 | **Gabriel** | Gabriel | Communication / Content | Penn (Copywriter) |
| 3 | **Raphael** | Raphael | Support / Healing | Cassie (Customer Support) |
| 4 | **Uriel** | Uriel | Research / Analysis | Dexter (Data Analyst) |
| 5 | **Sandalphon** | Sandalphon | Social / Community | Soshie (Social Media) |
| 6 | **Jophiel** | Jophiel | Marketing / Beauty | Emmie (Email Marketing) |
| 7 | **Michael** | Michael | Leadership / Strategy | — |
| 8 | **Raguel** | Raguel | Security / Compliance | — |
| 9 | **Remiel** | Remiel | Creative / Vision | Vince (Video) |
| 10 | **Sariel** | Sariel | Knowledge / Learning | — |
| 11 | **Azrael** | Azrael | Archival / Cleanup | — |
| 12 | **Chamuel** | Chamuel | Relationships / HR / Ops | — |

### Each Agent Gets:
- Specialized toolset per domain
- Access to dual-brain memory
- Proactive insight generation
- Cross-agent coordination via Mission Control
- Archangel personality (biblical research-based)

---

## Phase 8: Integration Layer

### Priority Integrations (via Composio preferred):
1. **Gmail** — Email automation
2. **Google Calendar** — Scheduling
3. **Google Drive** — File access
4. **Notion** — Knowledge sync
5. **Slack/Discord/Telegram** — Team comms
6. **X/LinkedIn/Instagram/TikTok/Facebook** — Social
7. **GitHub** — Code operations
8. **OpenRouter/OpenAI/Anthropic/Grok/Gemini/FAL** — Model access

### Setup Process:
1. Get Composio API key
2. Connect each platform via OAuth
3. Test each integration
4. Create skills for common workflows

---

## Phase 9: Automation & Cron Jobs

### Scheduled Jobs:
| Job | Schedule | Skill |
|-----|----------|-------|
| Daily Report | 06:00 daily | `daily-report-generator` |
| Weather Summary | 06:15 daily | `weather-fetcher` |
| Stock Report | 09:30 market days | `stock-reporter` |
| Task Summary | 08:00 daily | `task-summarizer` |
| Financial Report | 18:00 daily | `financial-reporter` |
| Nightly Audit | 02:00 daily | `nightly-audit` |
| Weekly Review | Monday 07:00 | `weekly-review` |
| Monthly Review | 1st 08:00 | `monthly-review` |
| Dream Process | 03:00 daily | `dream-process` |
| Hostinger Backup | 04:00 daily | `hostinger-backup-sync` |

---

## Phase 10: Security Hardening

### Active Defenses:
- ✅ Prompt injection defense (only direct user prompts)
- ✅ Cross-profile write guard
- 🔲 API key rotation schedule
- 🔲 Sub-agent verification protocol
- 🔲 Audit logging for all external calls
- 🔲 Rate limiting on external APIs
- 🔲 Sandbox for untrusted code execution

---

## Quick Start Checklist

### Immediate (Do Now):
- [ ] Fill out `user.md` (18 questions)
- [ ] Verify `identity.md` matches your vision

### This Session:
- [ ] Initialize vector memory / RAG
- [ ] Create first skill: `vector-memory-rag`
- [ ] Set up STT/TTS proof of concept
- [ ] Spawn Metatron (Brain AI agent)

### This Week:
- [ ] Build Mission Control UI
- [ ] Configure Composio integrations
- [ ] Spawn remaining 11 agents
- [ ] Set up cron automation
- [ ] Configure Hostinger backup

### Ongoing:
- [ ] Daily: Review Heartbeat.md, update Continuity.md
- [ ] Weekly: Review dual-brain growth, prune/consolidate
- [ ] Monthly: Strategic alignment, architecture review

---

## Commands Reference

```bash
# View all config files
ls -la /opt/data/jarvis/config/

# Edit user profile
nano /opt/data/jarvis/config/user.md

# Check dual-brain structure
tree /opt/data/jarvis/obsidian_brain
tree /opt/data/jarvis/holographic_brain

# View session continuity
cat /opt/data/jarvis/config/continuity.md

# Check heartbeat
cat /opt/data/jarvis/config/heartbeat.md
```

---

## Next Steps

1. **You**: Complete `user.md` questionnaire
2. **J.A.R.V.I.S.**: Initialize vector memory & RAG
3. **J.A.R.V.I.S.**: Build voice pipeline prototype
4. **J.A.R.V.I.S.**: Spawn Metatron (Brain AI)
5. **Together**: Review and iterate

---

**Ready when you are, Sir.**