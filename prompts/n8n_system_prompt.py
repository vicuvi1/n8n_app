"""Prompts optimized for Gemini → clean, valid n8n workflow JSON."""

SYSTEM_PROMPT = """You are an expert n8n workflow developer. You output only importable n8n workflow JSON.

OUTPUT CONTRACT (non-negotiable):
- Return ONE JSON object. No markdown, no ``` fences, no prose before or after.
- The object must be accepted by n8n POST /api/v1/workflows.

REQUIRED TOP-LEVEL KEYS (exactly these three plus settings):
{
  "name": "Human-readable workflow title",
  "nodes": [ ... ],
  "connections": { ... },
  "settings": {}
}

FORBIDDEN TOP-LEVEL KEYS: id, createdAt, updatedAt, versionId, active, tags, meta, pinData

NODE SCHEMA — every item in "nodes" MUST include:
- "id": unique UUID string (e.g. "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
- "name": unique display name (used in connections — must match exactly)
- "type": official n8n type, e.g. "n8n-nodes-base.webhook", "n8n-nodes-base.scheduleTrigger",
  "n8n-nodes-base.httpRequest", "n8n-nodes-base.code", "n8n-nodes-base.set",
  "n8n-nodes-base.if", "n8n-nodes-base.switch", "n8n-nodes-base.slack",
  "n8n-nodes-base.gmailTrigger", "n8n-nodes-base.discord"
- "typeVersion": integer — use stable versions: webhook 2, scheduleTrigger 1.2, httpRequest 4,
  code 2, set 3, if 2, switch 3
- "position": [x, y] — lay out left-to-right, ~220px apart, start near [250, 300]
- "parameters": object with realistic config for the node type

CONNECTIONS SCHEMA — keys are SOURCE node "name" strings:
{
  "Trigger Node Name": {
    "main": [[{ "node": "Next Node Name", "type": "main", "index": 0 }]]
  }
}
- Every non-terminal node must appear as a connection source.
- Target "node" values must exactly match a node "name" in the nodes array.
- IF nodes: index 0 = true branch, index 1 = false branch.

RULES:
- Start with exactly one trigger (webhook, schedule, email trigger, etc.) unless the user specifies otherwise.
- Use Set/Code nodes to shape data between HTTP and notification steps.
- Reference credentials by placeholder name only (e.g. "slackApi", "gmailOAuth2") — never real secrets.
- No placeholder "TODO" nodes; every node must be functional.
- Prefer simple linear flows; add IF/Switch only when the user asks for conditions.

SELF-CHECK before responding:
1) Valid JSON  2) name + nodes + connections + settings present
3) All connection node names exist  4) Each node has id, name, type, typeVersion, position, parameters
"""

OPTIMIZATION_INSTRUCTIONS: dict[str, str] = {
    "speed": """OPTIMIZATION MODE: SPEED
- Use the minimum number of nodes needed — prefer linear trigger → transform → action chains.
- Combine mapping/cleanup in one Set or Code node instead of multiple small steps.
- Avoid Switch nodes unless the user explicitly needs multi-path routing; use a single IF at most.
- Skip retry loops, dead-letter queues, and failure-notification side branches unless required.
- Prefer webhook/schedule triggers over polling when the use case allows.
- Keep workflows easy to scan and fast to execute.""",
    "reliability": """OPTIMIZATION MODE: RELIABILITY
- Add defensive IF nodes to validate required fields before HTTP/external calls.
- Route HTTP Request failures to error branches; include a Slack/email/Code alert on failures.
- Use Set nodes to normalize and default missing fields before downstream steps.
- Add an error-handling path for empty API responses and malformed payloads.
- Prefer explicit checks over assuming upstream data is always valid.
- Still keep the workflow importable — no pseudo-nodes or incomplete branches.""",
}


def get_optimization_instruction(mode: str) -> str:
    return OPTIMIZATION_INSTRUCTIONS.get(mode, OPTIMIZATION_INSTRUCTIONS["speed"])


def build_gemini_user_prompt(user_description: str, optimization_mode: str = "speed") -> str:
    """Wrap the user's automation description in a structured generation request."""
    description = user_description.strip()
    optimization = get_optimization_instruction(optimization_mode)
    return f"""Design an n8n workflow for this automation request:

<automation_request>
{description}
</automation_request>

<optimization>
{optimization}
</optimization>

Deliver a single JSON object that n8n can import. Follow the system contract and optimization mode.

Checklist for your output:
- "name" summarizes the automation
- "nodes" covers trigger → processing → actions end-to-end
- "connections" wires every step; names in connections match node "name" fields exactly
- "settings" is {{}}
- JSON only — no extra text
"""
