#!/usr/bin/env python3
"""
Archangel Agent Factory - Base Agent Class
Each agent inherits from this base with specialized personality and tools.
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

JARVIS_ROOT = Path("/opt/data/jarvis")
CONFIG_DIR = JARVIS_ROOT / "config"
OBSIDIAN_BRAIN = JARVIS_ROOT / "obsidian_brain"
HOLOGRAPHIC_BRAIN = JARVIS_ROOT / "holographic_brain"
VECTOR_MEMORY = JARVIS_ROOT / "vector_memory"
LOGS_DIR = JARVIS_ROOT / "logs"
AGENTS_DIR = JARVIS_ROOT / "config" / "agents"


class ArchangelAgent(ABC):
    """Base class for all Archangel agents."""
    
    def __init__(self, agent_id: str, config: Dict):
        self.agent_id = agent_id
        self.config = config
        self.name = config.get("name", agent_id.title())
        self.archangel = config.get("archangel", "")
        self.role = config.get("role", "")
        self.domain = config.get("domain", "")
        self.sintra_parallel = config.get("sintra_parallel", "")
        self.tools = config.get("tools", [])
        self.personality = config.get("personality", {})
        self.status = "idle"
        self.task_history: List[Dict] = []
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now()
        
        # Paths
        self.agent_dir = AGENTS_DIR / agent_id
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = LOGS_DIR / f"agent_{agent_id}.log"
        
        # Load soul directives
        self.soul_path = CONFIG_DIR / "soul.md"
        self.user_path = CONFIG_DIR / "user.md"
        
    def log(self, level: str, message: str):
        """Structured logging for agent activity."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "session_id": self.session_id,
            "level": level,
            "message": message
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[{self.name}] {level}: {message}")
    
    @abstractmethod
    async def initialize(self):
        """Initialize agent-specific resources."""
        pass
    
    @abstractmethod
    async def execute_task(self, task: Dict) -> Dict:
        """Execute a task assigned to this agent."""
        pass
    
    @abstractmethod
    async def proactive_insight(self) -> Optional[Dict]:
        """Generate proactive insights based on domain expertise."""
        pass
    
    async def start(self):
        """Start the agent."""
        self.log("INFO", f"Starting {self.name} ({self.archangel})")
        await self.initialize()
        self.status = "active"
        self.save_status()
        self.log("INFO", f"{self.name} online - Domain: {self.domain}")
    
    async def stop(self):
        """Stop the agent."""
        self.log("INFO", f"Stopping {self.name}")
        self.status = "idle"
        self.save_status()
    
    def save_status(self):
        """Save agent status to config."""
        status = {
            "agent_id": self.agent_id,
            "name": self.name,
            "archangel": self.archangel,
            "role": self.role,
            "domain": self.domain,
            "status": self.status,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "last_active": datetime.now().isoformat(),
            "tasks_completed": len(self.task_history)
        }
        with open(self.agent_dir / "status.json", "w") as f:
            json.dump(status, f, indent=2)
    
    def record_task(self, task: Dict, result: Dict):
        """Record task execution in history."""
        entry = {
            "task_id": task.get("id", str(uuid.uuid4())[:8]),
            "type": task.get("type", "unknown"),
            "input": task,
            "output": result,
            "timestamp": datetime.now().isoformat(),
            "status": result.get("status", "completed")
        }
        self.task_history.append(entry)
        self.save_status()
    
    def get_context(self) -> Dict:
        """Get context for task execution (dual-brain access)."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "archangel": self.archangel,
            "role": self.role,
            "domain": self.domain,
            "tools": self.tools,
            "personality": self.personality,
            "session_id": self.session_id,
            "obsidian_brain": str(OBSIDIAN_BRAIN),
            "holographic_brain": str(HOLOGRAPHIC_BRAIN),
            "vector_memory": str(VECTOR_MEMORY),
            "user_profile": str(self.user_path),
            "soul_directives": str(self.soul_path)
        }


# Agent Registry - maps agent_id to (class, config)
AGENT_REGISTRY = {}

def register_agent(agent_id: str, agent_class: type, config: Dict):
    """Register an agent class with its config."""
    AGENT_REGISTRY[agent_id] = (agent_class, config)

def get_agent(agent_id: str) -> Optional[ArchangelAgent]:
    """Instantiate and return an agent by ID."""
    if agent_id not in AGENT_REGISTRY:
        return None
    agent_class, config = AGENT_REGISTRY[agent_id]
    return agent_class(agent_id, config)

def list_agents() -> List[Dict]:
    """List all registered agents with their configs."""
    return [
        {"agent_id": aid, "name": cfg.get("name"), "archangel": cfg.get("archangel"), 
         "role": cfg.get("role"), "domain": cfg.get("domain")}
        for aid, (_, cfg) in AGENT_REGISTRY.items()
    ]