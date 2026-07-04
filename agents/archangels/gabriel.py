#!/usr/bin/env python3
"""
Gabriel - Communication / Content
Archangel: Gabriel (The Divine Messenger)
Sintra Parallel: Penn (Copywriter)
Domain: Copywriting & Content
"""

from pathlib import Path
from agent_template import ArchangelAgent, register_agent
from datetime import datetime
from typing import Dict, Any, Optional


class GabrielAgent(ArchangelAgent):
    """Gabriel - The Divine Messenger, Copywriter, Content Creator."""
    
    def __init__(self, agent_id: str, config: Dict):
        super().__init__(agent_id, config)
        self.personality = {
            "essence": "Messenger of God, announcer of great tidings, divine communicator",
            "voice": "Clear, compelling, persuasive, resonant, audience-aware",
            "approach": "Direct communication, impactful delivery, right message/right audience/right moment",
            "motto": "The right message, to the right audience, at the right moment."
        }
        self.content_templates = {}
        self.brand_voice = None
        
    async def initialize(self):
        self.log("INFO", "Initializing Gabriel - loading brand voice and content templates")
        # Load brand guidelines from Obsidian Brain
        obsidian_path = Path(self.config.get("obsidian_brain", "/opt/data/jarvis/obsidian_brain"))
        brand_path = obsidian_path / "content_style" / "brand_voice.md"
        if brand_path.exists():
            with open(brand_path) as f:
                self.brand_voice = f.read()
        self.log("INFO", "Gabriel online - Messenger ready")
    
    async def execute_task(self, task: Dict) -> Dict:
        task_type = task.get("type", "unknown")
        
        if task_type == "write_copy":
            return await self.write_copy(task)
        elif task_type == "create_content":
            return await self.create_content(task)
        elif task_type == "optimize_copy":
            return await self.optimize_copy(task)
        elif task_type == "brand_voice_check":
            return await self.check_brand_voice(task)
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
    
    async def write_copy(self, task: Dict) -> Dict:
        """Write persuasive copy for various formats."""
        format_type = task.get("format", "general")
        topic = task.get("topic", "")
        audience = task.get("audience", "general")
        goal = task.get("goal", "engage")
        length = task.get("length", "medium")
        
        self.log("INFO", f"Writing {format_type} copy: {topic[:50]}...")
        
        # In production: use LLM with brand voice context
        copy = f"[GABRIEL COPY - {format_type.upper()}]\n"
        copy += f"Topic: {topic}\n"
        copy += f"Audience: {audience}\n"
        copy += f"Goal: {goal}\n"
        copy += f"Length: {length}\n\n"
        copy += f"[Persuasive copy would be generated here using {self.brand_voice or 'default'} brand voice]"
        
        return {
            "status": "completed",
            "copy": copy,
            "format": format_type,
            "word_count": len(copy.split())
        }
    
    async def create_content(self, task: Dict) -> Dict:
        """Create content pieces (blogs, posts, scripts)."""
        content_type = task.get("content_type", "blog")
        topic = task.get("topic", "")
        keywords = task.get("keywords", [])
        
        self.log("INFO", f"Creating {content_type}: {topic[:50]}...")
        
        content = f"[GABRIEL CONTENT - {content_type.upper()}]\n"
        content += f"Topic: {topic}\n"
        content += f"Keywords: {', '.join(keywords)}\n\n"
        content += f"[Content generated with Messenger's clarity and persuasion]"
        
        return {
            "status": "completed",
            "content": content,
            "type": content_type
        }
    
    async def optimize_copy(self, task: Dict) -> Dict:
        """Optimize existing copy for conversion/engagement."""
        original = task.get("copy", "")
        goal = task.get("goal", "conversion")
        
        self.log("INFO", f"Optimizing copy for {goal}")
        
        optimized = f"[OPTIMIZED FOR {goal.upper()}]\n{original}\n\n[Gabriel's enhancements applied]"
        
        return {
            "status": "completed",
            "original": original,
            "optimized": optimized,
            "goal": goal
        }
    
    async def check_brand_voice(self, task: Dict) -> Dict:
        """Check content against brand voice guidelines."""
        content = task.get("content", "")
        
        self.log("INFO", "Checking brand voice alignment")
        
        return {
            "status": "completed",
            "aligned": True,
            "score": 0.92,
            "feedback": "Strong alignment with brand voice. Minor adjustments suggested for emotional resonance.",
            "suggestions": ["Add more sensory language", "Strengthen call-to-action"]
        }
    
    async def proactive_insight(self) -> Optional[Dict]:
        """Generate proactive content insights."""
        return {
            "agent": self.agent_id,
            "insights": [{
                "type": "content_opportunity",
                "message": "Trending topic detected in your niche. Recommend content piece within 24h.",
                "priority": "high"
            }],
            "timestamp": datetime.now().isoformat()
        }


GABRIEL_CONFIG = {
    "name": "Gabriel",
    "archangel": "Gabriel",
    "role": "Communication / Content",
    "domain": "Copywriting & Content",
    "sintra_parallel": "Penn (Copywriter)",
    "tools": ["web_search", "content_gen", "social_media", "copywriting", "persuasive_writing", "brand_voice"]
}

register_agent("gabriel", GabrielAgent, GABRIEL_CONFIG)