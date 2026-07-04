#!/usr/bin/env python3
"""
n8n Integration Skill for JARVOS Agents
Provides tools to interact with n8n workflow automation server.
"""

import os
import json
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from openjarvis.tools._stubs import BaseTool, ToolSpec, ToolExecutor
from openjarvis.core.events import EventBus


@dataclass
class N8NConfig:
    """n8n configuration."""
    url: str
    api_key: str
    webhook_base_url: str
    basic_auth_user: Optional[str] = None
    basic_auth_password: Optional[str] = None
    timeout: int = 30


class N8NClient:
    """HTTP client for n8n API."""

    def __init__(self, config: N8NConfig):
        self.config = config
        self.base_url = config.url.rstrip('/')
        self.api_key = config.api_key
        self.timeout = config.timeout
        
        # Build headers
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Add basic auth if configured
        basic_auth_user = config.basic_auth_user
        basic_auth_password = config.basic_auth_password
        if basic_auth_user and basic_auth_password:
            import base64
            creds = f"{basic_auth_user}:{basic_auth_password}"
            encoded = base64.b64encode(creds.encode()).decode()
            self.headers["Authorization"] = f"Basic {encoded}"

    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True,
        )

    async def list_workflows(self) -> List[Dict]:
        """List all workflows."""
        async with self._get_client() as client:
            response = await client.get("/api/v1/workflows")
            response.raise_for_status()
            return response.json().get("data", [])

    async def get_workflow(self, workflow_id: str) -> Dict:
        """Get workflow details."""
        async with self._get_client() as client:
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()
            return response.json()

    async def activate_workflow(self, workflow_id: str) -> Dict:
        """Activate a workflow."""
        async with self._get_client() as client:
            response = await client.post(f"/api/v1/workflows/{workflow_id}/activate")
            response.raise_for_status()
            return response.json()

    async def deactivate_workflow(self, workflow_id: str) -> Dict:
        """Deactivate a workflow."""
        async with self._get_client() as client:
            response = await client.post(f"/api/v1/workflows/{workflow_id}/deactivate")
            response.raise_for_status()
            return response.json()

    async def execute_workflow(
        self, 
        workflow_id: str, 
        data: Optional[Dict] = None,
        run_id: Optional[str] = None
    ) -> Dict:
        """Execute a workflow manually."""
        payload = {}
        if data:
            payload["data"] = data
        if run_id:
            payload["runId"] = run_id
            
        async with self._get_client() as client:
            response = await client.post(
                f"/api/v1/workflows/{workflow_id}/execute",
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def get_execution(self, execution_id: str) -> Dict:
        """Get execution details."""
        async with self._get_client() as client:
            response = await client.get(f"/api/v1/executions/{execution_id}")
            response.raise_for_status()
            return response.json()

    async def list_executions(
        self, 
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """List executions with optional filters."""
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        if status:
            params["status"] = status
            
        async with self._get_client() as client:
            response = await client.get("/api/v1/executions", params=params)
            response.raise_for_status()
            return response.json().get("data", [])

    async def create_webhook(
        self,
        workflow_id: str,
        path: str,
        method: str = "POST",
        response_mode: str = "onReceived"
    ) -> Dict:
        """Create a webhook for a workflow."""
        payload = {
            "workflowId": workflow_id,
            "path": path,
            "method": method.upper(),
            "responseMode": response_mode,
        }
        
        async with self._get_client() as client:
            response = await client.post("/api/v1/webhooks", json=payload)
            response.raise_for_status()
            return response.json()

    async def delete_webhook(self, webhook_id: str) -> Dict:
        """Delete a webhook."""
        async with self._get_client() as client:
            response = await client.delete(f"/api/v1/webhooks/{webhook_id}")
            response.raise_for_status()
            return response.json()

    async def trigger_webhook(
        self,
        webhook_path: str,
        data: Optional[Dict] = None,
        method: str = "POST"
    ) -> Dict:
        """Trigger a webhook endpoint."""
        url = f"{self.config.webhook_base_url.rstrip('/')}/{webhook_path.lstrip('/')}"
        
        # For webhooks, we might not need the API key header
        webhook_headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if method.upper() == "GET":
                response = await client.get(url, params=data, headers=webhook_headers)
            else:
                response = await client.request(
                    method.upper(), url, json=data, headers=webhook_headers
                )
            response.raise_for_status()
            return response.json() if response.content else {"status": "ok"}

    async def list_credentials(self) -> List[Dict]:
        """List credentials (names and types only)."""
        async with self._get_client() as client:
            response = await client.get("/api/v1/credentials")
            response.raise_for_status()
            return response.json().get("data", [])

    async def create_credential(
        self,
        name: str,
        credential_type: str,
        data: Dict
    ) -> Dict:
        """Create a new credential."""
        payload = {
            "name": name,
            "type": credential_type,
            "data": data,
        }
        
        async with self._get_client() as client:
            response = await client.post("/api/v1/credentials", json=payload)
            response.raise_for_status()
            return response.json()


# Global client instance
_n8n_client: Optional[N8NClient] = None


def get_n8n_client() -> N8NClient:
    """Get or create n8n client from config."""
    global _n8n_client
    
    if _n8n_client is not None:
        return _n8n_client
    
    # Load config from integrations.yaml
    config_path = Path("/opt/data/JARVIS_OS/config/integrations.yaml")
    if not config_path.exists():
        raise RuntimeError("integrations.yaml not found")
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    n8n_config = config.get("integrations", {}).get("n8n", {})
    
    if not n8n_config.get("enabled", False):
        raise RuntimeError("n8n integration not enabled in config")
    
    # Resolve environment variables
    def resolve_env(value: str) -> str:
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.environ.get(env_var, value)
        return value
    
    client_config = N8NConfig(
        url=resolve_env(n8n_config.get("url", "")),
        api_key=resolve_env(n8n_config.get("api_key", "")),
        webhook_base_url=resolve_env(n8n_config.get("webhook_base_url", "")),
        basic_auth_user=resolve_env(n8n_config.get("basic_auth", {}).get("user", "")) or None,
        basic_auth_password=resolve_env(n8n_config.get("basic_auth", {}).get("password", "")) or None,
        timeout=n8n_config.get("timeout", 30),
    )
    
    _n8n_client = N8NClient(client_config)
    return _n8n_client


# ─────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────

class N8NListWorkflowsTool(BaseTool):
    """List all n8n workflows."""
    
    spec = ToolSpec(
        name="n8n_list_workflows",
        description="List all workflows on the n8n server",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        workflows = await client.list_workflows()
        return {"workflows": workflows, "count": len(workflows)}


class N8NGetWorkflowTool(BaseTool):
    """Get detailed workflow information."""
    
    spec = ToolSpec(
        name="n8n_get_workflow",
        description="Get detailed information about a specific workflow",
        parameters={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "The workflow ID"}
            },
            "required": ["workflow_id"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        workflow = await client.get_workflow(params["workflow_id"])
        return workflow


class N8NActivateWorkflowTool(BaseTool):
    """Activate a workflow."""
    
    spec = ToolSpec(
        name="n8n_activate_workflow",
        description="Activate a workflow (enable it for execution)",
        parameters={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "The workflow ID"}
            },
            "required": ["workflow_id"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        result = await client.activate_workflow(params["workflow_id"])
        return {"status": "activated", "result": result}


class N8NDeactivateWorkflowTool(BaseTool):
    """Deactivate a workflow."""
    
    spec = ToolSpec(
        name="n8n_deactivate_workflow",
        description="Deactivate a workflow (disable it)",
        parameters={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "The workflow ID"}
            },
            "required": ["workflow_id"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        result = await client.deactivate_workflow(params["workflow_id"])
        return {"status": "deactivated", "result": result}


class N8NExecuteWorkflowTool(BaseTool):
    """Execute a workflow manually."""
    
    spec = ToolSpec(
        name="n8n_execute_workflow",
        description="Execute a workflow manually with optional input data",
        parameters={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "The workflow ID"},
                "data": {"type": "object", "description": "Input data for the workflow"},
                "run_id": {"type": "string", "description": "Custom run ID for tracking"}
            },
            "required": ["workflow_id"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        result = await client.execute_workflow(
            params["workflow_id"],
            data=params.get("data"),
            run_id=params.get("run_id")
        )
        return result


class N8NGetExecutionTool(BaseTool):
    """Get execution details."""
    
    spec = ToolSpec(
        name="n8n_get_execution",
        description="Get details of a workflow execution",
        parameters={
            "type": "object",
            "properties": {
                "execution_id": {"type": "string", "description": "The execution ID"}
            },
            "required": ["execution_id"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        execution = await client.get_execution(params["execution_id"])
        return execution


class N8NListExecutionsTool(BaseTool):
    """List workflow executions."""
    
    spec = ToolSpec(
        name="n8n_list_executions",
        description="List workflow executions with optional filtering",
        parameters={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "Filter by workflow ID"},
                "status": {"type": "string", "description": "Filter by status (success, error, running, waiting)"},
                "limit": {"type": "integer", "description": "Maximum number of executions", "default": 50}
            },
            "required": []
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        executions = await client.list_executions(
            workflow_id=params.get("workflow_id"),
            status=params.get("status"),
            limit=params.get("limit", 50)
        )
        return {"executions": executions, "count": len(executions)}


class N8NCreateWebhookTool(BaseTool):
    """Create a webhook for a workflow."""
    
    spec = ToolSpec(
        name="n8n_create_webhook",
        description="Create a webhook endpoint for a workflow",
        parameters={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "The workflow ID"},
                "path": {"type": "string", "description": "Webhook path (e.g., 'jarvis/trigger')"},
                "method": {"type": "string", "description": "HTTP method (POST, GET, PUT, DELETE)", "default": "POST"},
                "response_mode": {"type": "string", "description": "Response mode (onReceived, lastNode)", "default": "onReceived"}
            },
            "required": ["workflow_id", "path"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        result = await client.create_webhook(
            params["workflow_id"],
            params["path"],
            params.get("method", "POST"),
            params.get("response_mode", "onReceived")
        )
        return result


class N8NDeleteWebhookTool(BaseTool):
    """Delete a webhook."""
    
    spec = ToolSpec(
        name="n8n_delete_webhook",
        description="Delete a webhook endpoint",
        parameters={
            "type": "object",
            "properties": {
                "webhook_id": {"type": "string", "description": "The webhook ID"}
            },
            "required": ["webhook_id"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        result = await client.delete_webhook(params["webhook_id"])
        return {"status": "deleted", "result": result}


class N8NTriggerWebhookTool(BaseTool):
    """Trigger a webhook endpoint."""
    
    spec = ToolSpec(
        name="n8n_trigger_webhook",
        description="Trigger a webhook endpoint with data",
        parameters={
            "type": "object",
            "properties": {
                "webhook_path": {"type": "string", "description": "The webhook path (e.g., 'jarvis/automation/trigger')"},
                "data": {"type": "object", "description": "Data to send to the webhook"},
                "method": {"type": "string", "description": "HTTP method", "default": "POST"}
            },
            "required": ["webhook_path"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        result = await client.trigger_webhook(
            params["webhook_path"],
            data=params.get("data"),
            method=params.get("method", "POST")
        )
        return result


class N8NListCredentialsTool(BaseTool):
    """List credentials."""
    
    spec = ToolSpec(
        name="n8n_list_credentials",
        description="List credentials stored in n8n (names and types only)",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        credentials = await client.list_credentials()
        return {"credentials": credentials, "count": len(credentials)}


class N8NCreateCredentialTool(BaseTool):
    """Create a credential."""
    
    spec = ToolSpec(
        name="n8n_create_credential",
        description="Create a new credential in n8n",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Credential name"},
                "type": {"type": "string", "description": "Credential type (e.g., httpBasicAuth, oAuth2Api, apiKey)"},
                "data": {"type": "object", "description": "Credential data (structure depends on type)"}
            },
            "required": ["name", "type", "data"]
        }
    )

    async def run(self, params: Dict, ctx: Any) -> Dict:
        client = get_n8n_client()
        result = await client.create_credential(
            params["name"],
            params["type"],
            params["data"]
        )
        return result


# ─────────────────────────────────────────────────────────────
# SKILL REGISTRATION
# ─────────────────────────────────────────────────────────────

N8N_TOOLS = [
    N8NListWorkflowsTool,
    N8NGetWorkflowTool,
    N8NActivateWorkflowTool,
    N8NDeactivateWorkflowTool,
    N8NExecuteWorkflowTool,
    N8NGetExecutionTool,
    N8NListExecutionsTool,
    N8NCreateWebhookTool,
    N8NDeleteWebhookTool,
    N8NTriggerWebhookTool,
    N8NListCredentialsTool,
    N8NCreateCredentialTool,
]


def register_n8n_tools(executor: ToolExecutor) -> None:
    """Register all n8n tools with the tool executor."""
    for tool_class in N8N_TOOLS:
        tool = tool_class()
        executor.register_tool(tool)
        print(f"Registered n8n tool: {tool.spec.name}")


def get_n8n_tool_specs() -> List[ToolSpec]:
    """Get all n8n tool specifications."""
    return [tool_class.spec for tool_class in N8N_TOOLS]