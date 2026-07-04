#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Mission Control Dashboard Backend
FastAPI + WebSocket real-time dashboard
"""

import asyncio
import json
import os
import psutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Configuration
JARVIS_ROOT = Path("/opt/data/JARVIS_OS")
CONFIG_DIR = JARVIS_ROOT / "config"
LOGS_DIR = JARVIS_ROOT / "logs"
DASHBOARD_CONFIG = CONFIG_DIR / "dashboard.yaml"

class SystemMonitor:
    """System metrics collector."""

    @staticmethod
    def get_cpu() -> Dict[str, Any]:
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }

    @staticmethod
    def get_memory() -> Dict[str, Any]:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent
        }

    @staticmethod
    def get_disk() -> Dict[str, Any]:
        disk = psutil.disk_usage("/")
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100
        }

    @staticmethod
    def get_network() -> Dict[str, Any]:
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv
        }

    @staticmethod
    def get_gpu() -> Dict[str, Any]:
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    "name": gpu.name,
                    "load": gpu.load * 100,
                    "memory_used": gpu.memoryUsed,
                    "memory_total": gpu.memoryTotal,
                    "memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100,
                    "temperature": gpu.temperature
                }
        except:
            pass
        return {"available": False}

    @staticmethod
    def get_uptime() -> float:
        return time.time() - psutil.boot_time()

    @staticmethod
    def get_all() -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": SystemMonitor.get_cpu(),
            "memory": SystemMonitor.get_memory(),
            "disk": SystemMonitor.get_disk(),
            "network": SystemMonitor.get_network(),
            "gpu": SystemMonitor.get_gpu(),
            "uptime": SystemMonitor.get_uptime()
        }


class AgentMonitor:
    """Monitor agent statuses."""

    AGENTS_DIR = JARVIS_ROOT / "agents" / "factory"

    @staticmethod
    def get_agent_statuses() -> Dict[str, Any]:
        statuses = {}
        for agent_dir in AgentMonitor.AGENTS_DIR.iterdir():
            if agent_dir.is_dir():
                status_file = agent_dir / "status.json"
                process_file = agent_dir / "process.json"
                if status_file.exists():
                    try:
                        with open(status_file) as f:
                            statuses[agent_dir.name] = json.load(f)
                    except:
                        pass
                elif process_file.exists():
                    try:
                        with open(process_file) as f:
                            statuses[agent_dir.name] = {"status": "active", **json.load(f)}
                    except:
                        pass
        return statuses


class TaskQueueMonitor:
    """Monitor task queue."""

    @staticmethod
    def get_queue_status() -> Dict[str, Any]:
        # In production, connect to actual task queue
        return {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "queue_depth": 0
        }


class MemoryGraphMonitor:
    """Monitor dual-brain sync status."""

    @staticmethod
    def get_memory_status() -> Dict[str, Any]:
        obsidian = JARVIS_ROOT / "brains" / "obsidian"
        holographic = JARVIS_ROOT / "brains" / "holographic"
        vector = JARVIS_ROOT / "vector_db" / "chroma_db"

        obsidian_files = len(list(obsidian.rglob("*.md"))) if obsidian.exists() else 0
        holographic_files = len(list(holographic.rglob("*.md"))) if holographic.exists() else 0

        vector_chunks = 0
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(vector))
            collection = client.get_collection("jarvis_dual_brain")
            vector_chunks = collection.count()
        except:
            pass

        return {
            "obsidian_files": obsidian_files,
            "holographic_files": holographic_files,
            "vector_chunks": vector_chunks,
            "sync_status": "active" if vector_chunks > 0 else "inactive",
            "last_sync": None  # TODO: read from sync_metadata.json
        }


class FinancialMonitor:
    """Financial metrics (placeholder for real integration)."""

    @staticmethod
    def get_financials() -> Dict[str, Any]:
        return {
            "revenue_today": 0,
            "revenue_week": 0,
            "revenue_month": 0,
            "expenses_today": 0,
            "expenses_week": 0,
            "expenses_month": 0,
            "profit_margin": 0,
            "forecast_30d": 0,
            "forecast_90d": 0,
            "tattoo_bookings": 0,
            "automation_revenue": 0
        }


class CalendarMonitor:
    """Calendar events (placeholder)."""

    @staticmethod
    def get_calendar() -> Dict[str, Any]:
        return {
            "today": [],
            "week": [],
            "conflicts": []
        }


class CommunicationsMonitor:
    """Communications status (placeholder)."""

    @staticmethod
    def get_communications() -> Dict[str, Any]:
        return {
            "email_unread": 0,
            "slack_unread": 0,
            "discord_unread": 0,
            "telegram_unread": 0,
            "priority_items": []
        }


class ResearchMonitor:
    """Research threads (placeholder)."""

    @staticmethod
    def get_research() -> Dict[str, Any]:
        return {
            "active_threads": [],
            "arxiv_papers": [],
            "market_analysis": [],
            "competitor_intel": []
        }


class SecurityMonitor:
    """Security status."""

    @staticmethod
    def get_security() -> Dict[str, Any]:
        return {
            "threat_level": "low",
            "failed_logins": 0,
            "api_anomalies": 0,
            "file_integrity": "ok",
            "network_scans": 0,
            "vulnerability_alerts": 0,
            "alerts": []
        }


class ConnectionManager:
    """WebSocket connection manager."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()
system_monitor = SystemMonitor()
agent_monitor = AgentMonitor()
task_monitor = TaskQueueMonitor()
memory_monitor = MemoryGraphMonitor()
financial_monitor = FinancialMonitor()
calendar_monitor = CalendarMonitor()
comm_monitor = CommunicationsMonitor()
research_monitor = ResearchMonitor()
security_monitor = SecurityMonitor()


async def metrics_broadcaster():
    """Background task to broadcast metrics via WebSocket."""
    while True:
        try:
            metrics = {
                "type": "metrics_update",
                "timestamp": datetime.now().isoformat(),
                "system": system_monitor.get_all(),
                "agents": agent_monitor.get_agent_statuses(),
                "tasks": task_monitor.get_queue_status(),
                "memory": memory_monitor.get_memory_status(),
                "financial": financial_monitor.get_financials(),
                "calendar": calendar_monitor.get_calendar(),
                "communications": comm_monitor.get_communications(),
                "research": research_monitor.get_research(),
                "security": security_monitor.get_security()
            }
            await manager.broadcast(metrics)
        except Exception as e:
            print(f"Broadcast error: {e}")
        await asyncio.sleep(5)  # Update every 5 seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    broadcaster_task = asyncio.create_task(metrics_broadcaster())
    yield
    # Shutdown
    broadcaster_task.cancel()
    try:
        await broadcaster_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="J.A.R.V.I.S. Mission Control",
    description="Real-time system dashboard for J.A.R.V.I.S. OS",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for dashboard
DASHBOARD_DIR = JARVIS_ROOT / "dashboard" / "public"
if DASHBOARD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR)), name="static")

@app.get("/dashboard")
async def dashboard():
    """Serve the Mission Control dashboard HTML."""
    index_file = DASHBOARD_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"error": "Dashboard not built. Run build script first."}


@app.get("/")
async def root():
    return {"service": "J.A.R.V.I.S. Mission Control", "version": "1.0.0", "status": "operational"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/system")
async def get_system():
    return system_monitor.get_all()


@app.get("/api/agents")
async def get_agents():
    return agent_monitor.get_agent_statuses()


@app.get("/api/tasks")
async def get_tasks():
    return task_monitor.get_queue_status()


@app.get("/api/memory")
async def get_memory():
    return memory_monitor.get_memory_status()


@app.get("/api/financial")
async def get_financial():
    return financial_monitor.get_financials()


@app.get("/api/calendar")
async def get_calendar():
    return calendar_monitor.get_calendar()


@app.get("/api/communications")
async def get_communications():
    return comm_monitor.get_communications()


@app.get("/api/research")
async def get_research():
    return research_monitor.get_research()


@app.get("/api/security")
async def get_security():
    return security_monitor.get_security()


@app.get("/api/all")
async def get_all():
    return {
        "system": system_monitor.get_all(),
        "agents": agent_monitor.get_agent_statuses(),
        "tasks": task_monitor.get_queue_status(),
        "memory": memory_monitor.get_memory_status(),
        "financial": financial_monitor.get_financials(),
        "calendar": calendar_monitor.get_calendar(),
        "communications": comm_monitor.get_communications(),
        "research": research_monitor.get_research(),
        "security": security_monitor.get_security()
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        initial = {
            "type": "initial_state",
            "timestamp": datetime.now().isoformat(),
            "system": system_monitor.get_all(),
            "agents": agent_monitor.get_agent_statuses(),
            "tasks": task_monitor.get_queue_status(),
            "memory": memory_monitor.get_memory_status(),
            "financial": financial_monitor.get_financials(),
            "calendar": calendar_monitor.get_calendar(),
            "communications": comm_monitor.get_communications(),
            "research": research_monitor.get_research(),
            "security": security_monitor.get_security()
        }
        await websocket.send_json(initial)

        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)