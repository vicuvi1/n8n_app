"""Ready-made workflow templates for the Gemini generator."""

READY_MADE_TEMPLATES: dict[str, dict[str, str]] = {
    "daily_email_summary": {
        "label": "Daily Email Summary",
        "icon": "📧",
        "description": "Morning digest of inbox highlights via AI",
        "prompt": (
            "Build a production-ready n8n workflow named 'Daily Email Summary':\n"
            "1. Schedule Trigger — weekdays at 8:00 AM.\n"
            "2. Gmail node — fetch emails from the last 24 hours.\n"
            "3. Set node — extract sender, subject, snippet, and received date.\n"
            "4. IF node — skip newsletters/no-reply if subject contains 'unsubscribe'.\n"
            "5. HTTP Request — call Gemini or OpenAI chat API to summarize emails into "
            "sections: Urgent, Follow-up, FYI, with bullet points.\n"
            "6. Code node — merge summaries into a markdown daily briefing.\n"
            "7. Gmail or Slack node — send the briefing to the user.\n"
            "Include error handling and placeholder credentials only."
        ),
    },
    "invoice_processing": {
        "label": "Invoice Processing",
        "icon": "🧾",
        "description": "Extract invoice data and route for approval",
        "prompt": (
            "Build a production-ready n8n workflow named 'Invoice Processing':\n"
            "1. Gmail Trigger — new email with PDF attachment or subject containing 'invoice'.\n"
            "2. Set node — capture sender, subject, attachment metadata.\n"
            "3. HTTP Request or Extract from File — parse invoice fields: vendor, amount, "
            "invoice number, due date (use Code node for parsing logic).\n"
            "4. IF node — if amount > 1000 route to approval branch, else auto-approve branch.\n"
            "5. Google Sheets or Airtable node — log invoice row.\n"
            "6. Slack node — notify #finance with summary and approval link on high-value invoices.\n"
            "7. Gmail node — send confirmation to sender on success.\n"
            "Use realistic node types, connections, and credential placeholders."
        ),
    },
    "content_calendar_generator": {
        "label": "Content Calendar Generator",
        "icon": "📅",
        "description": "AI-generated weekly content plan to a sheet",
        "prompt": (
            "Build a production-ready n8n workflow named 'Content Calendar Generator':\n"
            "1. Webhook or Manual Trigger — accepts topic, audience, and brand voice.\n"
            "2. Set node — normalize inputs.\n"
            "3. HTTP Request — Gemini/OpenAI API to generate a 7-day content calendar "
            "(date, channel, post idea, caption draft, hashtag suggestions) as JSON.\n"
            "4. Code node — parse AI JSON and format rows.\n"
            "5. Google Sheets node — append rows to a 'Content Calendar' sheet.\n"
            "6. Slack node — post summary with link to the sheet.\n"
            "7. Respond to Webhook with the generated calendar JSON.\n"
            "Include error branch if AI response is invalid JSON."
        ),
    },
    "social_media_posting": {
        "label": "Social Media Posting",
        "icon": "📱",
        "description": "Schedule and cross-post approved content",
        "prompt": (
            "Build a production-ready n8n workflow named 'Social Media Posting':\n"
            "1. Google Sheets Trigger or Schedule — poll 'Approved Posts' sheet for rows "
            "where status=ready and scheduled_time <= now.\n"
            "2. Set node — read caption, image URL, platforms.\n"
            "3. Switch node — route by platform (Twitter/X, LinkedIn, Facebook).\n"
            "4. HTTP Request nodes — post to each platform API (use credential placeholders).\n"
            "5. Merge node — collect results.\n"
            "6. Google Sheets node — update row status to 'posted' with timestamp.\n"
            "7. IF node on failure — Slack alert to #marketing with error details.\n"
            "Wire all branches with proper connections."
        ),
    },
    "meeting_notes_to_notion": {
        "label": "Meeting Notes to Notion",
        "icon": "📝",
        "description": "Transcript → structured Notion page",
        "prompt": (
            "Build a production-ready n8n workflow named 'Meeting Notes to Notion':\n"
            "1. Webhook Trigger — receives meeting transcript text, title, and attendees.\n"
            "2. Set node — validate required fields.\n"
            "3. HTTP Request — Gemini/OpenAI to extract: summary, decisions, action items "
            "(owner + due date), and open questions.\n"
            "4. Code node — format output as Notion blocks JSON.\n"
            "5. HTTP Request — Notion API POST /pages to create page in a Meetings database "
            "(use notionApi credential placeholder).\n"
            "6. Slack node — notify attendees with Notion page link.\n"
            "7. Respond to Webhook with page URL.\n"
            "Include error handling on AI and Notion steps."
        ),
    },
    "lead_qualification": {
        "label": "Lead Qualification",
        "icon": "🎯",
        "description": "Score inbound leads and assign owners",
        "prompt": (
            "Build a production-ready n8n workflow named 'Lead Qualification':\n"
            "1. Webhook Trigger — accepts lead JSON: name, email, company, role, source, message.\n"
            "2. Set node — normalize and validate email.\n"
            "3. HTTP Request — enrichment API placeholder (e.g. Clearbit) for company size/industry.\n"
            "4. Code node — compute lead score (0-100) from role, company size, source, message intent.\n"
            "5. IF node — score >= 70 hot lead, 40-69 warm, else cold.\n"
            "6. HubSpot or Pipedrive node — create/update contact with score and tier.\n"
            "7. Slack node — alert #sales for hot leads with lead details.\n"
            "8. Gmail node — send nurture template for cold leads.\n"
            "Respond to webhook with score and tier."
        ),
    },
    "expense_tracking": {
        "label": "Expense Tracking",
        "icon": "💳",
        "description": "Receipt upload → categorized ledger",
        "prompt": (
            "Build a production-ready n8n workflow named 'Expense Tracking':\n"
            "1. Webhook or Form Trigger — receipt image URL, amount, merchant, date, submitter email.\n"
            "2. Set node — validate inputs.\n"
            "3. HTTP Request — OCR/AI API to extract merchant, amount, category, tax from receipt.\n"
            "4. Code node — map category to accounting codes; flag duplicates by amount+date+merchant.\n"
            "5. IF node — if amount > 500 require manager approval via Slack interactive message.\n"
            "6. Google Sheets or QuickBooks node — append expense row.\n"
            "7. Gmail node — confirmation to submitter.\n"
            "Include approval and rejection branches."
        ),
    },
    "customer_support_triage": {
        "label": "Customer Support Triage",
        "icon": "🎧",
        "description": "Classify tickets and route by priority",
        "prompt": (
            "Build a production-ready n8n workflow named 'Customer Support Triage':\n"
            "1. Webhook or Zendesk/Intercom Trigger — new support ticket with subject, body, customer tier.\n"
            "2. Set node — extract ticket fields.\n"
            "3. HTTP Request — Gemini/OpenAI classify: category (billing, technical, account), "
            "priority (P1-P4), sentiment, suggested reply draft.\n"
            "4. Switch node — route by priority: P1 to on-call Slack + PagerDuty placeholder, "
            "P2 to support queue, P3/P4 to async queue.\n"
            "5. Zendesk/Jira node — update ticket labels, priority, and assignee group.\n"
            "6. IF node — if sentiment is angry, escalate to senior agent Slack channel.\n"
            "7. Respond to webhook with classification JSON.\n"
            "Use realistic n8n nodes and credential placeholders."
        ),
    },
}

READY_MADE_TEMPLATE_KEYS = list(READY_MADE_TEMPLATES.keys())

# User-saved templates are stored separately (see utils/template_store.py).
WORKFLOW_TEMPLATES: dict[str, dict[str, str]] = {}
TEMPLATE_KEYS: list[str] = []
