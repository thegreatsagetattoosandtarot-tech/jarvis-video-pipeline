---
name: n8n-integration
version: 1.0.0
description: "n8n workflow automation integration for JARVIS agents"
category: automation
author: JARVIS OS
tags:
  - n8n
  - workflow
  - automation
  - api
  - webhook
dependencies:
  - python: ">=3.10"
  - packages:
      - httpx>=0.28.0
      - pydantic>=2.9.0
      - pyyaml>=6.0.0
config_schema:
  n8n_url:
    type: string
    description: "n8n server URL (e.g., https://n8n.yourdomain.com)"
    required: true
  api_key:
    type: string
    description: "n8n API key for authentication"
    required: true
    secret: true
  webhook_base_url:
    type: string
    description: "Base URL for webhooks (e.g., https://n8n.yourdomain.com/webhook)"
    required: true
  basic_auth_user:
    type: string
    description: "Basic auth username for n8n UI"
    required: false
  basic_auth_password:
    type: string
    description: "Basic auth password for n8n UI"
    required: false
    secret: true
  timeout:
    type: integer
    description: "Request timeout in seconds"
    default: 30
    required: false
---

# n8n Integration Skill

This skill provides JARVIS agents with the ability to interact with n8n workflow automation server.

## Tools Provided

### 1. n8n_list_workflows
List all workflows on the n8n server.

**Parameters:** None

**Returns:** List of workflows with id, name, active status, tags, created/updated timestamps.

### 2. n8n_get_workflow
Get detailed information about a specific workflow.

**Parameters:**
- `workflow_id` (string, required): The workflow ID

**Returns:** Full workflow definition including nodes, connections, and settings.

### 3. n8n_activate_workflow
Activate a workflow (enable it for execution).

**Parameters:**
- `workflow_id` (string, required): The workflow ID

**Returns:** Activation status.

### 4. n8n_deactivate_workflow
Deactivate a workflow (disable it).

**Parameters:**
- `workflow_id` (string, required): The workflow ID

**Returns:** Deactivation status.

### 5. n8n_execute_workflow
Execute a workflow manually (trigger it).

**Parameters:**
- `workflow_id` (string, required): The workflow ID
- `data` (object, optional): Input data for the workflow
- `run_id` (string, optional): Custom run ID for tracking

**Returns:** Execution ID and status.

### 6. n8n_get_execution
Get details of a workflow execution.

**Parameters:**
- `execution_id` (string, required): The execution ID

**Returns:** Execution details including status, data, started/finished times, and node execution data.

### 7. n8n_list_executions
List workflow executions with optional filtering.

**Parameters:**
- `workflow_id` (string, optional): Filter by workflow ID
- `status` (string, optional): Filter by status (success, error, running, waiting)
- `limit` (integer, optional): Maximum number of executions to return (default: 50)

**Returns:** List of executions.

### 8. n8n_create_webhook
Create a webhook endpoint for a workflow.

**Parameters:**
- `workflow_id` (string, required): The workflow ID
- `path` (string, required): Webhook path (e.g., "jarvis/trigger")
- `method` (string, optional): HTTP method (POST, GET, PUT, DELETE) - default: POST
- `response_mode` (string, optional): Response mode (onReceived, lastNode) - default: onReceived

**Returns:** Webhook URL and configuration.

### 9. n8n_delete_webhook
Delete a webhook endpoint.

**Parameters:**
- `webhook_id` (string, required): The webhook ID

**Returns:** Deletion status.

### 10. n8n_trigger_webhook
Trigger a webhook endpoint with data.

**Parameters:**
- `webhook_path` (string, required): The webhook path (e.g., "jarvis/trigger")
- `data` (object, optional): Data to send to the webhook
- `method` (string, optional): HTTP method - default: POST

**Returns:** Webhook response.

### 11. n8n_get_credentials
List credentials stored in n8n (names and types only, not secrets).

**Parameters:** None

**Returns:** List of credential names and types.

### 12. n8n_create_credential
Create a new credential in n8n.

**Parameters:**
- `name` (string, required): Credential name
- `type` (string, required): Credential type (e.g., "httpBasicAuth", "oAuth2Api", "apiKey")
- `data` (object, required): Credential data (structure depends on type)

**Returns:** Created credential info.

## Example Usage

```python
# List all workflows
result = await n8n_list_workflows()

# Execute a workflow
result = await n8n_execute_workflow(
    workflow_id="abc123",
    data={"message": "Hello from JARVIS!", "priority": "high"}
)

# Trigger a webhook
result = await n8n_trigger_webhook(
    webhook_path="jarvis/automation/trigger",
    data={"task": "backup", "target": "obsidian_brain"}
)

# Get execution status
result = await n8n_get_execution(execution_id="exec_456")
```

## Configuration

Add to your `integrations.yaml`:

```yaml
n8n:
  enabled: true
  url: "https://n8n.yourdomain.com"
  api_key: "${N8N_API_KEY}"
  webhook_base_url: "https://n8n.yourdomain.com/webhook"
  basic_auth_user: "${N8N_BASIC_AUTH_USER}"
  basic_auth_password: "${N8N_BASIC_AUTH_PASSWORD}"
```

## Security Notes

- API key should be stored in environment variables, never in code
- Webhook endpoints should be secured with authentication
- Use HTTPS in production
- Limit webhook access with IP whitelisting if possible
- Rotate API keys periodically

## Architecture

```
JARVIS Agent
     │
     ▼
n8n Integration Skill (HTTP Client)
     │
     ├── REST API ──▶ n8n Server (Workflows, Executions, Credentials)
     │
     └── Webhooks ──▶ n8n Webhook Endpoints (Real-time triggers)
```

## Integration with JARVIS Agents

The n8n skill can be used by any JARVIS agent:

- **Metatron** (Brain AI): Trigger knowledge sync workflows
- **Gabriel** (Communications): Send notifications via webhook
- **Uriel** (Research): Execute research workflows
- **Michael** (Strategy): Trigger strategic planning workflows
- **Azrael** (Archival): Run cleanup/archive workflows
- **Tattoo Business Agent**: Automate booking, client management, marketing

## Workflow Templates

Common workflow templates for JARVIS:

1. **Daily Report Generation** - Triggered by cron, generates daily summary
2. **Brain Sync** - Syncs Obsidian → Holographic → Vector DB
3. **Backup Automation** - Triggers backup to Hostinger
4. **Security Scan** - Runs security audit and reports
5. **Client Onboarding** - Tattoo business client intake
6. **Appointment Reminders** - Sends SMS/email reminders
7. **Social Media Posting** - Queues and posts content
8. **Invoice Generation** - Creates and sends invoices