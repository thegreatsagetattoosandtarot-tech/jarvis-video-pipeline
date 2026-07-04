---
name: openjarvis-integration
category: integration
description: Integration layer for OpenJarvis components - agents, skills, memory, speech, and local inference
version: 1.0.0
author: J.A.R.V.I.S.
tags: [openjarvis, agents, skills, memory, speech, local-llm, inference]
---

# OpenJarvis Integration Skill

## Overview
Integrates OpenJarvis (Stanford Hazy Research) components into J.A.R.V.I.S. system:
- 8 built-in agents (morning_digest, deep_research, monitor_operative, orchestrator, native_react, operative, native_openhands, simple)
- Skills system (Hermes ~150, OpenClaw ~13,700)
- Local inference (MLX, vLLM, Ollama, llamacpp)
- Memory system (extractor, service, store)
- Speech (faster-whisper, Deepgram, Cartesia, Kokoro, OpenAI TTS)
- Security sandboxing

## OpenJarvis Path
`/opt/data/jarvis/OpenJarvis` (cloned, uv synced)

## Config
- **Config Path**: `/opt/data/jarvis/.openjarvis/config.toml`
- **Home Dir**: `/opt/data/jarvis/.openjarvis`
- **Environment**: `OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis`

## Working Components ✅

### Ollama Engine
- **Status**: Reachable ✅
- **Model**: qwen3:0.6b (installed)
- **Endpoint**: http://localhost:11434

### Installed Skills (from Hermes)
| Skill | Version | Description |
|-------|---------|-------------|
| arxiv | 1.0.0 | Search arXiv papers by keyword, author, category |
| blogwatcher | 2.0.0 | Monitor blogs and RSS/Atom feeds |
| llm-wiki | 2.1.0 | Karpathy's LLM Wiki: build/query interlinked markdown |
| polymarket | 1.0.0 | Query Polymarket markets, prices, orderbooks |
| research-paper-writing | 1.1.0 | Write ML papers for NeurIPS/ICML/ICLR |

### Desktop Extras (installed via `uv sync --extra desktop`)
- faster-whisper ✅ (STT)
- REST API server ✅

### Agents Tested
| Agent | Status | Notes |
|-------|--------|-------|
| simple | ✅ Working | Single-turn chat, no tools |
| deep_research | ✅ Available | Multi-hop research with citations |
| orchestrator | ✅ Available | Multi-turn reasoning with tool selection |

## Usage

### Run OpenJarvis Commands
```bash
# Set environment
export OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis

# Or use inline
OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis cd /opt/data/jarvis/OpenJarvis && .venv/bin/python -m openjarvis.cli <command>

# Examples
OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis cd /opt/data/jarvis/OpenJarvis && .venv/bin/python -m openjarvis.cli ask "What is the capital of France?"
OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis cd /opt/data/jarvis/OpenJarvis && .venv/bin/python -m openjarvis.cli doctor
OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis cd /opt/data/jarvis/OpenJarvis && .venv/bin/python -m openjarvis.cli skill list
```

### Install More Skills
```bash
OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis cd /opt/data/jarvis/OpenJarvis && .venv/bin/python -m openjarvis.cli skill install hermes:arxiv
OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis cd /opt/data/jarvis/OpenJarvis && .venv/bin/python -m openjarvis.cli skill sync hermes --category research
```

### Available Presets
```bash
OPENJARVIS_HOME=/opt/data/jarvis/.openjarvis cd /opt/data/jarvis/OpenJarvis && .venv/bin/python -m openjarvis.cli init --preset <name>
# Presets: chat-simple, morning-digest-linux, deep-research, code-assistant, scheduled-monitor
```

## Integration Points with J.A.R.V.I.S.

1. **Metatron (Brain AI)** ←→ OpenJarvis `orchestrator` / `monitor_operative`
2. **Voice Pipeline** ←→ OpenJarvis `speech` (faster-whisper, kokoro)
3. **Archangel Agents** ←→ OpenJarvis `skills` system
4. **Cron Automation** ←→ OpenJarvis `scheduler` + `monitor_operative`
5. **Dual-Brain** ←→ OpenJarvis `memory` extractor/store

## Files

- `scripts/openjarvis_bridge.py` - Python bridge module
- `templates/agent_config.yaml` - Agent configuration template
- `scripts/sync_skills.py` - Skill synchronization script