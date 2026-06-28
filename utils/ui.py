"""Custom CSS and reusable UI components for a polished dashboard look."""

import streamlit as st

CUSTOM_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
  }

  /* Hide Streamlit chrome */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header[data-testid="stHeader"] {
    background: rgba(11, 15, 25, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #1F2937;
  }

  /* Main area */
  .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1420 0%, #0B0F19 100%);
    border-right: 1px solid #1F2937;
  }
  section[data-testid="stSidebar"] .block-container {
    padding-top: 1.25rem;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 500;
    font-size: 0.875rem;
    color: #8B93A7;
    background: transparent;
    border: none;
  }
  .stTabs [aria-selected="true"] {
    background: #151C2F !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 0 1px #2A3144, 0 2px 8px rgba(0,0,0,0.25);
  }
  .stTabs [data-baseweb="tab-highlight"] {
    display: none;
  }
  .stTabs [data-baseweb="tab-border"] {
    display: none;
  }

  /* Buttons */
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF6D5A 0%, #FF8F7A 100%);
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.6rem 1.25rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 2px 12px rgba(255, 109, 90, 0.25);
  }
  .stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(255, 109, 90, 0.35);
    border: none;
    color: white;
  }
  .stButton > button[kind="secondary"] {
    background: #151C2F;
    border: 1px solid #2A3144;
    border-radius: 10px;
    font-weight: 500;
    color: #C5CAD6;
  }
  .stButton > button[kind="secondary"]:hover {
    background: #1A2236;
    border-color: #3B4258;
    color: #FFFFFF;
  }

  /* Inputs */
  .stTextInput input, .stTextArea textarea {
    background: #111827 !important;
    border: 1px solid #2A3144 !important;
    border-radius: 10px !important;
    color: #E8EAEF !important;
    font-size: 0.9rem !important;
  }
  .stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(255, 109, 90, 0.5) !important;
    box-shadow: 0 0 0 2px rgba(255, 109, 90, 0.12) !important;
  }

  /* Metrics */
  [data-testid="stMetric"] {
    background: #151C2F;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }
  [data-testid="stMetricLabel"] {
    color: #8B93A7 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
  }
  [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-weight: 700 !important;
  }

  /* Dataframes */
  [data-testid="stDataFrame"] {
    border: 1px solid #1F2937;
    border-radius: 12px;
    overflow: hidden;
  }

  /* Expanders */
  .streamlit-expanderHeader {
    background: #151C2F !important;
    border: 1px solid #1F2937 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
  }

  /* Alerts — softer tones */
  .stAlert {
    border-radius: 10px;
    border: 1px solid transparent;
  }

  /* Custom component classes */
  .dash-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0.25rem;
  }
  .dash-logo {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: linear-gradient(135deg, #FF6D5A 0%, #FF9F43 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1rem;
    color: white;
    box-shadow: 0 4px 20px rgba(255, 109, 90, 0.35);
    flex-shrink: 0;
  }
  .dash-title {
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    margin: 0;
    line-height: 1.2;
  }
  .dash-subtitle {
    font-size: 0.9rem;
    color: #8B93A7;
    margin: 4px 0 0 0;
    font-weight: 400;
  }
  .section-card {
    background: #151C2F;
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
  }
  .section-card h3 {
    margin: 0 0 0.35rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #FFFFFF;
  }
  .section-card p {
    margin: 0;
    font-size: 0.85rem;
    color: #8B93A7;
  }
  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    margin-top: 12px;
  }
  .status-pill.ok {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34D399;
  }
  .status-pill.warn {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.25);
    color: #FBBF24;
  }
  .status-pill.err {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #F87171;
  }
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
  }
  .empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: #111827;
    border: 1px dashed #2A3144;
    border-radius: 14px;
    margin-top: 1rem;
  }
  .empty-state .icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
    opacity: 0.6;
  }
  .empty-state h4 {
    color: #E8EAEF;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
  }
  .empty-state p {
    color: #6B7280;
    font-size: 0.875rem;
    margin: 0;
  }
  .sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 1rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #1F2937;
  }
  .sidebar-brand .logo-sm {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    background: linear-gradient(135deg, #FF6D5A, #FF9F43);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.7rem;
    color: white;
  }
  .sidebar-brand span {
    font-weight: 600;
    font-size: 0.95rem;
    color: #E8EAEF;
  }
  .kpi-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 1.25rem;
  }
  .kpi-card {
    background: #151C2F;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 1rem 1.25rem;
  }
  .kpi-card .label {
    font-size: 0.75rem;
    color: #8B93A7;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .kpi-card .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-top: 4px;
  }
  .kpi-card.accent .value { color: #FF6D5A; }
  .kpi-card.green .value { color: #34D399; }
  .kpi-card.red .value { color: #F87171; }
  hr.divider {
    border: none;
    border-top: 1px solid #1F2937;
    margin: 1.5rem 0;
  }
</style>
"""


def inject_styles() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """
        <div class="dash-header">
          <div class="dash-logo">n8</div>
          <div>
            <p class="dash-title">n8n AI Management Dashboard</p>
            <p class="dash-subtitle">Manage, generate, and monitor workflows powered by Google Gemini</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
          <div class="logo-sm">n8</div>
          <span>Command Center</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(label: str, level: str = "ok") -> None:
    """Render a colored status pill. level: ok | warn | err"""
    st.markdown(
        f'<div class="status-pill {level}"><span class="status-dot"></span>{label}</div>',
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-card">
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, message: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state">
          <div class="icon">{icon}</div>
          <h4>{title}</h4>
          <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_cards(total: int, success: int, failed: int) -> None:
    st.markdown(
        f"""
        <div class="kpi-row">
          <div class="kpi-card accent">
            <div class="label">Total Runs</div>
            <div class="value">{total}</div>
          </div>
          <div class="kpi-card green">
            <div class="label">Success</div>
            <div class="value">{success}</div>
          </div>
          <div class="kpi-card red">
            <div class="label">Failed</div>
            <div class="value">{failed}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
