"""Quick-blueprint workflow prompts for the AI Generator tab."""

WORKFLOW_TEMPLATES: dict[str, dict[str, str]] = {
    "none": {
        "label": "None (Write Custom Prompt)",
        "prompt": "",
    },
    "soc_virustotal": {
        "label": "SOC Alert: Webhook to VirusTotal IP Check & Discord Alert",
        "prompt": (
            "Build a production-ready n8n workflow for a SOC alerting pipeline:\n"
            "1. Webhook trigger that accepts JSON with fields: ip, source, event_type.\n"
            "2. Set node to validate and normalize the IP address.\n"
            "3. HTTP Request node to query VirusTotal API v3 for the IP (GET /ip_addresses/{ip}) "
            "using header x-apikey from credentials placeholder.\n"
            "4. Code node to parse malicious votes, country, ASN, and compute a threat score.\n"
            "5. IF node: if threat score >= 5 OR malicious detections >= 3, route to alert branch.\n"
            "6. Discord node posting a rich alert embed with IP, score, country, ASN, and VT link.\n"
            "7. On clean branch, respond to webhook with 200 and JSON status clean.\n"
            "Use realistic n8n node types, typeVersions, positions left-to-right, and proper connections."
        ),
    },
    "email_triage": {
        "label": "Email Triage: Scan Inbox for Daily Summaries using AI",
        "prompt": (
            "Build a production-ready n8n workflow for daily email triage with AI:\n"
            "1. Schedule Trigger — run every weekday at 8:00 AM.\n"
            "2. Gmail node to fetch all emails from the last 24 hours (inbox, unread optional).\n"
            "3. Set node to extract sender, subject, snippet, and received date per message.\n"
            "4. Aggregate or Loop to batch emails into groups of 10.\n"
            "5. HTTP Request node calling an AI API (OpenAI chat completions or Gemini) with a system "
            "prompt to produce a structured daily briefing: urgent items, follow-ups, FYI, and suggested actions.\n"
            "6. Code node to merge AI summaries into a single markdown report.\n"
            "7. Gmail node or Slack node to deliver the daily summary to the user.\n"
            "Include error handling on the AI HTTP node and use placeholder credential references only."
        ),
    },
}

TEMPLATE_KEYS = list(WORKFLOW_TEMPLATES.keys())
