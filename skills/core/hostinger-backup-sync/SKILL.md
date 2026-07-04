---
name: hostinger-backup-sync
category: infrastructure
description: Automated backup synchronization to Hostinger server for J.A.R.V.I.S. system persistence
version: 1.0.0
author: J.A.R.V.I.S.
tags: [backup, hostinger, sync, infrastructure, disaster-recovery]
---

# Hostinger Backup Sync Skill

## Overview
Provides automated backup and synchronization of the entire J.A.R.V.I.S. system (configs, brains, skills, logs) to Hostinger hosting for disaster recovery and cross-session persistence.

## Backup Scope

| Directory | Contents | Frequency |
|-----------|----------|-----------|
| `/opt/data/jarvis/config/` | Core configs (soul.md, user.md, agent.md, etc.) | Every sync |
| `/opt/data/jarvis/obsidian_brain/` | Raw knowledge base | Every sync |
| `/opt/data/jarvis/holographic_brain/` | Applied knowledge | Every sync |
| `/opt/data/jarvis/vector_memory/` | ChromaDB vector store | Every sync |
| `/opt/data/jarvis/skills/` | Custom skills | Every sync |
| `/opt/data/jarvis/scripts/` | Automation scripts | Every sync |
| `/opt/data/jarvis/security/hashes/` | Integrity hashes | Every sync |
| `/opt/data/jarvis/logs/` | Audit logs (rotated) | Daily |
| `/opt/data/jarvis/agents/` | Agent configs | Every sync |

## Configuration

### Required Environment Variables
```bash
HOSTINGER_HOST=your-hostinger-server.com
HOSTINGER_USER=your-username
HOSTINGER_PATH=/home/youruser/jarvis_backups
HOSTINGER_SSH_KEY=/path/to/private/key
```

### Optional Settings
```bash
BACKUP_RETENTION_DAYS=30
BACKUP_COMPRESSION=zstd
BACKUP_ENCRYPTION=age  # or gpg
SYNC_PARALLEL=4
```

## Usage

### Manual Sync
```bash
python sync_to_hostinger.py --full
```

### Incremental Sync
```bash
python sync_to_hostinger.py --incremental
```

### Restore from Backup
```bash
python restore_from_hostinger.py --backup-date 2026-06-27
```

### Verify Backup Integrity
```bash
python verify_backup.py
```

## Automation

### Cron Schedule (Recommended)
```
# Daily full backup at 4:00 AM
0 4 * * * /opt/data/jarvis/scripts/backup_hostinger.sh

# Hourly incremental during work hours
0 8-20 * * * /opt/data/jarvis/scripts/backup_hostinger.sh --incremental
```

## Files

- `sync_to_hostinger.py` - Main sync script
- `restore_from_hostinger.py` - Restore script
- `verify_backup.py` - Integrity verification
- `scripts/backup_hostinger.sh` - Wrapper for cron
- `templates/ssh_config` - SSH config template
- `templates/rsync_exclude` - Exclude patterns

## Security

- SSH key-based authentication only
- Optional encryption at rest (age/gpg)
- Integrity verification via SHA256 manifests
- No credentials in code - environment variables only

## Disaster Recovery

1. Provision new server
2. Install dependencies: `apt-get install rsync ssh age`
3. Configure SSH access to Hostinger
4. Run: `python restore_from_hostinger.py --latest`
5. Verify: `python verify_backup.py`
6. Restart J.A.R.V.I.S. services