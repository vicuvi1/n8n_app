"""

n8n AI Management Dashboard — Streamlit entry point.



Tabs:

  1. AI Workflow Generator  — Gemini-powered workflow creation

  2. Workflow Control Center — list, activate/deactivate, delete

  3. Live Execution Monitor — SOC-style execution log

"""



import time



import pandas as pd

import streamlit as st



from config.constants import AUTO_REFRESH_INTERVAL, DEBUG

from services.gemini_client import GeminiAPIError, generate_workflow

from services.n8n_client import N8nAPIError, N8nClient

from utils.session import (

    credentials_ready,

    get_gemini_api_key,

    get_n8n_api_key,

    get_n8n_base_url,

    init_session_state,

    n8n_credentials_ready,

)

from utils.ui import (

    empty_state,

    inject_styles,

    kpi_cards,

    render_header,

    render_sidebar_brand,

    section_header,

    status_pill,

)



# ─── Page config ─────────────────────────────────────────────────────────────



st.set_page_config(

    page_title="n8n AI Management Dashboard",

    page_icon="⚡",

    layout="wide",

    initial_sidebar_state="expanded",

)



init_session_state()

inject_styles()





# ─── Sidebar: API credentials ────────────────────────────────────────────────



def render_sidebar() -> None:

    render_sidebar_brand()



    st.sidebar.markdown("##### API Configuration")

    st.sidebar.caption("Stored in session memory only — not persisted to disk.")



    st.session_state.gemini_api_key = st.sidebar.text_input(

        "Google Gemini API Key",

        value=st.session_state.gemini_api_key,

        type="password",

        placeholder="AIza…",

        help="Free key at aistudio.google.com/apikey",

    )

    st.session_state.n8n_url = st.sidebar.text_input(

        "n8n Instance URL",

        value=st.session_state.n8n_url,

        placeholder="http://localhost:5678",

    )

    st.session_state.n8n_api_key = st.sidebar.text_input(

        "n8n API Key",

        value=st.session_state.n8n_api_key,

        type="password",

        placeholder="n8n_api_…",

        help="n8n → Settings → API",

    )



    st.sidebar.markdown("---")

    st.sidebar.markdown("##### Connection Status")



    if credentials_ready():

        status_pill("All systems ready", "ok")

    elif n8n_credentials_ready():

        status_pill("Gemini key required", "warn")

    else:

        status_pill("Credentials needed", "err")





def get_n8n_client() -> N8nClient:

    return N8nClient(get_n8n_base_url(), get_n8n_api_key())





def show_api_error(exc: Exception) -> None:

    st.error(str(exc))

    if DEBUG:

        st.exception(exc)





# ─── Tab 1: AI Workflow Generator ────────────────────────────────────────────



def tab_generator() -> None:

    section_header(

        "AI Workflow Generator",

        "Describe your automation in plain English — Gemini builds production-ready n8n JSON.",

    )



    if not credentials_ready():

        empty_state(

            "🔑",

            "API keys required",

            "Enter your Gemini and n8n credentials in the sidebar to start generating workflows.",

        )

        return



    prompt = st.text_area(

        "Workflow prompt",

        height=160,

        label_visibility="collapsed",

        placeholder=(

            'Example: "Build a workflow that catches a webhook, parses an IP address, '

            'checks it on AbuseIPDB, and sends a Discord alert if the score is above 80."'

        ),

    )



    col_gen, col_push, col_spacer = st.columns([1, 1, 2])



    with col_gen:

        generate_clicked = st.button("✨ Generate Workflow", type="primary", use_container_width=True)



    with col_push:

        push_clicked = st.button(

            "🚀 Push to n8n",

            use_container_width=True,

            disabled=st.session_state.generated_workflow is None,

        )



    if generate_clicked:

        with st.spinner("Gemini is designing your workflow…"):

            try:

                workflow = generate_workflow(get_gemini_api_key(), prompt)

                st.session_state.generated_workflow = workflow

                st.session_state.api_error = None

                st.success(f'Workflow **"{workflow.get("name", "Untitled")}"** generated successfully.')

            except (GeminiAPIError, ValueError) as exc:

                st.session_state.generated_workflow = None

                show_api_error(exc)



    if st.session_state.generated_workflow:

        st.markdown("---")

        st.markdown("##### Generated Workflow Preview")

        with st.container(border=True):

            st.json(st.session_state.generated_workflow)



    if push_clicked and st.session_state.generated_workflow:

        with st.spinner("Installing workflow on your n8n instance…"):

            try:

                client = get_n8n_client()

                result = client.create_workflow(st.session_state.generated_workflow)

                workflow_id = result.get("id", "unknown")

                st.success(f"Workflow installed successfully — ID: `{workflow_id}`")

            except N8nAPIError as exc:

                show_api_error(exc)





# ─── Tab 2: Workflow Control Center ──────────────────────────────────────────



def tab_manager() -> None:

    section_header(

        "Workflow Control Center",

        "View, activate, deactivate, and delete workflows on your n8n server.",

    )



    if not n8n_credentials_ready():

        empty_state(

            "🔗",

            "n8n connection required",

            "Enter your n8n instance URL and API key in the sidebar.",

        )

        return



    _, btn_col = st.columns([4, 1])

    with btn_col:

        refresh = st.button("↻ Refresh", use_container_width=True)



    try:

        if refresh or "workflows_cache" not in st.session_state:

            client = get_n8n_client()

            st.session_state.workflows_cache = client.list_workflows()



        workflows = st.session_state.workflows_cache



        if not workflows:

            empty_state("📋", "No workflows yet", "Create one in the AI Generator tab or in n8n directly.")

            return



        active_count = sum(1 for wf in workflows if wf.get("active"))

        inactive_count = len(workflows) - active_count



        m1, m2, m3 = st.columns(3)

        m1.metric("Total Workflows", len(workflows))

        m2.metric("Active", active_count)

        m3.metric("Inactive", inactive_count)



        rows = [

            {

                "Name": wf.get("name", "Unnamed"),

                "ID": wf.get("id", ""),

                "Status": "🟢 Active" if wf.get("active") else "⚪ Inactive",

            }

            for wf in workflows

        ]

        with st.container(border=True):

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)



        st.markdown("##### Workflow Actions")



        for wf in workflows:

            wf_id = wf.get("id", "")

            wf_name = wf.get("name", "Unnamed")

            is_active = wf.get("active", False)

            status_label = "Active" if is_active else "Inactive"



            with st.expander(f"**{wf_name}**  ·  {status_label}  ·  `{wf_id}`"):

                action_col1, action_col2, action_col3 = st.columns([1, 1, 2])



                with action_col1:

                    toggle_label = "⏸ Deactivate" if is_active else "▶ Activate"

                    if st.button(toggle_label, key=f"toggle_{wf_id}", use_container_width=True):

                        try:

                            client = get_n8n_client()

                            client.toggle_workflow(wf_id, is_active)

                            st.session_state.pop("workflows_cache", None)

                            st.rerun()

                        except N8nAPIError as exc:

                            show_api_error(exc)



                with action_col2:

                    if st.session_state.delete_confirm_id == wf_id:

                        if st.button("🗑 Confirm delete", key=f"confirm_del_{wf_id}", type="primary"):

                            try:

                                client = get_n8n_client()

                                client.delete_workflow(wf_id)

                                st.session_state.delete_confirm_id = None

                                st.session_state.pop("workflows_cache", None)

                                st.rerun()

                            except N8nAPIError as exc:

                                show_api_error(exc)

                        if st.button("Cancel", key=f"cancel_del_{wf_id}"):

                            st.session_state.delete_confirm_id = None

                            st.rerun()

                    else:

                        if st.button("🗑 Delete", key=f"delete_{wf_id}", use_container_width=True):

                            st.session_state.delete_confirm_id = wf_id

                            st.rerun()



    except N8nAPIError as exc:

        show_api_error(exc)





# ─── Tab 3: Live Execution Monitor ───────────────────────────────────────────



def _highlight_failed(row: pd.Series) -> list[str]:

    status = str(row.get("Status", "")).lower()

    if status in ("error", "failed"):

        return ["background-color: #3b1212; color: #fca5a5"] * len(row)

    return [""] * len(row)





def _format_executions_df(executions: list) -> pd.DataFrame:

    rows = []

    for ex in executions:

        rows.append(

            {

                "Execution ID": ex.get("id", ""),

                "Status": ex.get("status", "unknown"),

                "Started At": ex.get("startedAt", ""),

                "Finished At": ex.get("stoppedAt") or ex.get("finishedAt", ""),

                "Workflow ID": ex.get("workflowId", ""),

            }

        )

    df = pd.DataFrame(rows)

    if not df.empty:

        for col in ("Started At", "Finished At"):

            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

    return df





def tab_executions() -> None:

    section_header(

        "Live Execution Monitor",

        "SOC-style log of recent workflow runs — failed executions highlighted in red.",

    )



    if not n8n_credentials_ready():

        empty_state(

            "📡",

            "n8n connection required",

            "Enter your n8n instance URL and API key in the sidebar.",

        )

        return



    ctrl_col, refresh_col = st.columns([3, 1])

    with ctrl_col:

        auto_refresh = st.checkbox(f"Auto-refresh every {AUTO_REFRESH_INTERVAL}s")

    with refresh_col:

        if st.button("↻ Refresh now", use_container_width=True):

            st.rerun()



    try:

        client = get_n8n_client()

        executions = client.list_executions()



        if not executions:

            empty_state("📭", "No executions yet", "Run a workflow in n8n to see execution history here.")

        else:

            failed = sum(

                1 for ex in executions if str(ex.get("status", "")).lower() in ("error", "failed")

            )

            success = sum(1 for ex in executions if str(ex.get("status", "")).lower() == "success")



            kpi_cards(len(executions), success, failed)



            df = _format_executions_df(executions)

            styled = df.style.apply(_highlight_failed, axis=1)

            with st.container(border=True):

                st.dataframe(styled, use_container_width=True, hide_index=True)



    except N8nAPIError as exc:

        show_api_error(exc)



    if auto_refresh:

        time.sleep(AUTO_REFRESH_INTERVAL)

        st.rerun()





# ─── Main ────────────────────────────────────────────────────────────────────



def main() -> None:

    render_sidebar()

    render_header()



    st.markdown("<hr class='divider'>", unsafe_allow_html=True)



    tab1, tab2, tab3 = st.tabs(

        ["✨ AI Generator", "⚙️ Control Center", "📡 Execution Monitor"]

    )



    with tab1:

        tab_generator()

    with tab2:

        tab_manager()

    with tab3:

        tab_executions()





if __name__ == "__main__":

    main()


