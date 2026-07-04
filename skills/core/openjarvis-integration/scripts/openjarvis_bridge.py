#!/usr/bin/env python3
"""
OpenJarvis Bridge for J.A.R.V.I.S.
Connects OpenJarvis agents, skills, memory, and speech to J.A.R.V.I.S. system.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

OPENJARVIS_ROOT = Path("/opt/data/jarvis/OpenJarvis")
JARVIS_ROOT = Path("/opt/data/jarvis")

# Add OpenJarvis to path
sys.path.insert(0, str(OPENJARVIS_ROOT / "src"))
sys.path.insert(0, str(OPENJARVIS_ROOT / ".venv" / "lib" / "python3.13" / "site-packages"))


class OpenJarvisBridge:
    """Bridge between J.A.R.V.I.S. and OpenJarvis components."""
    
    def __init__(self):
        self.openjarvis_root = OPENJARVIS_ROOT
        self.venv_python = OPENJARVIS_ROOT / ".venv" / "bin" / "python"
        self.uv_path = OPENJARVIS_ROOT / ".venv" / "bin" / "uv"
        
        # Verify OpenJarvis is available
        self.available = self.venv_python.exists()
        
    def run_openjarvis(self, args: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
        """Run OpenJarvis CLI command."""
        if not self.available:
            raise RuntimeError("OpenJarvis not available - run uv sync first")
        
        # Use the correct OPENJARVIS_HOME (outside source tree)
        env = os.environ.copy()
        env["OPENJARVIS_HOME"] = "/opt/data/jarvis/.openjarvis"
        env["OPENJARVIS_CONFIG"] = "/opt/data/jarvis/.openjarvis/config.toml"
        
        cmd = [str(self.venv_python), "-m", "openjarvis.cli"] + args
        return subprocess.run(cmd, cwd=cwd or self.openjarvis_root, capture_output=True, text=True, env=env)
    
    def run_uv(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run uv command in OpenJarvis context."""
        if not self.available:
            raise RuntimeError("OpenJarvis not available")
        
        cmd = [str(self.uv_path)] + args
        return subprocess.run(cmd, cwd=self.openjarvis_root, capture_output=True, text=True)
    
    # ==================== AGENTS ====================
    
    def init_agent(self, preset: str) -> Dict:
        """Initialize an OpenJarvis agent preset."""
        result = self.run_openjarvis(["init", "--preset", preset])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def list_agents(self) -> List[str]:
        """List available OpenJarvis agents."""
        return [
            "morning_digest",
            "deep_research", 
            "monitor_operative",
            "orchestrator",
            "native_react",
            "operative",
            "native_openhands",
            "simple"
        ]
    
    def run_agent(self, agent: str, query: str) -> Dict:
        """Run a query against an OpenJarvis agent."""
        result = self.run_openjarvis(["ask", "--agent", agent, query])
        return {
            "success": result.returncode == 0,
            "response": result.stdout,
            "stderr": result.stderr
        }
    
    # ==================== SKILLS ====================
    
    def install_skill(self, skill_ref: str) -> Dict:
        """Install a skill (e.g., 'hermes:arxiv')."""
        result = self.run_openjarvis(["skill", "install", skill_ref])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def sync_skills(self, source: str = "hermes", category: str = None) -> Dict:
        """Sync skills from a source."""
        args = ["skill", "sync", source]
        if category:
            args.extend(["--category", category])
        result = self.run_openjarvis(args)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def list_skills(self) -> Dict:
        """List installed skills."""
        result = self.run_openjarvis(["skill", "list"])
        return {
            "success": result.returncode == 0,
            "skills": result.stdout
        }
    
    def optimize_skills(self, policy: str = "dspy") -> Dict:
        """Optimize skills from trace history."""
        result = self.run_openjarvis(["optimize", "skills", "--policy", policy])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    # ==================== CONNECTIONS ====================
    
    def connect_service(self, service: str) -> Dict:
        """Connect to a service (gdrive, gmail, etc.)."""
        result = self.run_openjarvis(["connect", service])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    # ==================== SPEECH ====================
    
    def generate_speech(self, text: str, engine: str = "kokoro") -> Dict:
        """Generate TTS audio using OpenJarvis speech engines."""
        # This would use the OpenJarvis speech module directly
        # For now, delegate to CLI
        return {"success": False, "error": "Use OpenJarvis speech module directly"}
    
    def transcribe_audio(self, audio_path: str, engine: str = "faster_whisper") -> Dict:
        """Transcribe audio using OpenJarvis STT."""
        return {"success": False, "error": "Use OpenJarvis speech module directly"}
    
    # ==================== MEMORY ====================
    
    def extract_memory(self, conversation: str) -> Dict:
        """Extract memory from conversation using OpenJarvis extractor."""
        return {"success": False, "error": "Use OpenJarvis memory module directly"}
    
    def query_memory(self, query: str) -> Dict:
        """Query OpenJarvis memory store."""
        return {"success": False, "error": "Use OpenJarvis memory module directly"}
    
    # ==================== SCHEDULER ====================
    
    def schedule_task(self, cron_expr: str, agent: str, query: str) -> Dict:
        """Schedule a recurring task using OpenJarvis scheduler."""
        # This would integrate with OpenJarvis scheduler
        return {"success": False, "error": "Use OpenJarvis scheduler module directly"}
    
    # ==================== DIAGNOSTICS ====================
    
    def doctor(self) -> Dict:
        """Run OpenJarvis doctor check."""
        result = self.run_openjarvis(["doctor"])
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def install_extras(self, extras: List[str]) -> Dict:
        """Install optional dependencies."""
        args = ["sync"] + [f"--extra={e}" for e in extras]
        result = self.run_uv(args)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def get_status(self) -> Dict:
        """Get OpenJarvis system status."""
        return {
            "available": self.available,
            "root": str(self.openjarvis_root),
            "venv_python": str(self.venv_python),
            "uv": str(self.uv_path),
            "agents": self.list_agents()
        }


# Convenience functions for integration
_bridge = None

def get_bridge() -> OpenJarvisBridge:
    """Get or create the OpenJarvis bridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = OpenJarvisBridge()
    return _bridge

def run_openjarvis_agent(agent: str, query: str) -> Dict:
    """Quick function to run an OpenJarvis agent query."""
    return get_bridge().run_agent(agent, query)

def install_openjarvis_skill(skill: str) -> Dict:
    """Quick function to install an OpenJarvis skill."""
    return get_bridge().install_skill(skill)

def sync_openjarvis_skills(source: str = "hermes", category: str = None) -> Dict:
    """Quick function to sync OpenJarvis skills."""
    return get_bridge().sync_skills(source, category)

def openjarvis_doctor() -> Dict:
    """Quick function to run OpenJarvis doctor."""
    return get_bridge().doctor()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenJarvis Bridge for J.A.R.V.I.S.")
    parser.add_argument("--status", action="store_true", help="Show OpenJarvis status")
    parser.add_argument("--doctor", action="store_true", help="Run OpenJarvis doctor")
    parser.add_argument("--agent", help="Run agent query (with --query)")
    parser.add_argument("--query", help="Query for agent")
    parser.add_argument("--install-skill", help="Install skill (e.g., hermes:arxiv)")
    parser.add_argument("--sync-skills", action="store_true", help="Sync skills from Hermes")
    parser.add_argument("--list-skills", action="store_true", help="List installed skills")
    parser.add_argument("--install-extras", nargs="+", help="Install extra dependencies")
    
    args = parser.parse_args()
    
    bridge = OpenJarvisBridge()
    
    if args.status:
        print(bridge.get_status())
    elif args.doctor:
        print(bridge.doctor())
    elif args.agent and args.query:
        print(bridge.run_agent(args.agent, args.query))
    elif args.install_skill:
        print(bridge.install_skill(args.install_skill))
    elif args.sync_skills:
        print(bridge.sync_skills())
    elif args.list_skills:
        print(bridge.list_skills())
    elif args.install_extras:
        print(bridge.install_extras(args.install_extras))
    else:
        parser.print_help()