---
name: cron-automation
category: automation
description: Scheduled automation jobs for J.A.R.V.I.S. system - daily reports, nightly audits, weekly/monthly reviews
version: 1.0.0
author: J.A.R.V.I.S.
tags: [cron, automation, scheduling, reports, maintenance]
---

# Cron Automation Skill

## Overview
Manages all scheduled jobs for the J.A.R.V.I.S. system including daily reports, nightly audits, weekly reviews, monthly reviews, and system maintenance.

## Scheduled Jobs

| Job | Schedule | Description | Skill/Script |
|-----|----------|-------------|--------------|
| Daily Report | 06:00 daily | Morning briefing: weather, stocks, tasks, calendar | `daily-report-generator` |
| Weather Summary | 06:15 daily | Current conditions + forecast | `weather-fetcher` |
| Stock Report | 09:30 market days | Portfolio & market summary | `stock-reporter` |
| Task Summary | 08:00 daily | Today's tasks & priorities | `task-summarizer` |
| Financial Report | 18:00 daily | Revenue, expenses, forecasts | `financial-reporter` |
| Nightly Audit | 02:00 daily | Code review, security scan, perf check | `nightly-audit` |
| Weekly Review | Mon 07:00 | Progress, patterns, adjustments | `weekly-review` |
| Monthly Review | 1st 08:00 | Strategic alignment, course correction | `monthly-review` |
| Dream Process | 03:00 daily | Nightly synthesis, pattern recognition | `dream-process` |
| Hostinger Backup | 04:00 daily | Full system backup to Hostinger | `hostinger-backup-sync` |
| Vector Re-index | 05:00 daily | Re-index brains to vector memory | `vector-memory-rag` |
| Health Check | */15 * * * * | System health monitoring | `health-check` |

## Configuration

### Environment Variables
```bash
# Report delivery
REPORT_EMAIL=your@email.com
REPORT_TELEGRAM_CHAT_ID=123456789
REPORT_DISCORD_WEBHOOK=https://discord.com/api/webhooks/...

# API Keys (for weather, stocks, etc.)
OPENWEATHER_API_KEY=...
ALPHA_VANTAGE_API_KEY=...
```

## Usage

### Install Cron Jobs
```bash
python install_cron.py --install
```

### List Jobs
```bash
python install_cron.py --list
```

### Remove All Jobs
```bash
python install_cron.py --remove
```

### Run Single Job Manually
```bash
python run_job.py --job daily_report
```

## Files

- `install_cron.py` - Cron installation/management
- `run_job.py` - Manual job runner
- `jobs/daily_report.py` - Morning briefing
- `jobs/nightly_audit.py` - Security & code audit
- `jobs/weekly_review.py` - Weekly synthesis
- `jobs/monthly_review.py` - Monthly strategic review
- `jobs/dream_process.py` - Nightly pattern synthesis
- `jobs/health_check.py` - System health monitoring
- `templates/crontab_template` - Crontab template

## Integration with Mission Control

Dashboard at `http://localhost:8080` shows:
- Next scheduled runs
- Last run status
- Job history
- Manual trigger buttons