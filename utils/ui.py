"""Custom CSS and reusable UI components for a polished dashboard look."""

import streamlit as st

CUSTOM_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
  }

  /* Ambient page background */
  .stApp {
    background:
      radial-gradient(ellipse 90% 60% at 10% -10%, rgba(255, 109, 90, 0.09), transparent 55%),
      radial-gradient(ellipse 70% 50% at 95% 5%, rgba(99, 102, 241, 0.06), transparent 50%),
      #0B0F19 !important;
  }

  /* Scrollbars */
  ::-webkit-scrollbar { width: 8px; height: 8px; }
  ::-webkit-scrollbar-track { background: #0B0F19; }
  ::-webkit-scrollbar-thumb { background: #2A3144; border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: #3B4258; }

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
    padding-top: 1.25rem;
    padding-bottom: 2.5rem;
    max-width: 100%;
  }

  /* Context column subtle separation */
  [data-testid="column"]:last-child .block-container {
    border-left: 1px solid rgba(31, 41, 55, 0.6);
    padding-left: 1.25rem;
  }

  /* Right context sidebar */
  .context-sidebar-header {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .context-sidebar-badge {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: #FF8F7A;
    background: rgba(255, 109, 90, 0.12);
    border: 1px solid rgba(255, 109, 90, 0.25);
    border-radius: 6px;
    padding: 2px 6px;
  }
  .automation-status-card {
    background: linear-gradient(160deg, #151C2F 0%, #12182a 100%);
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 0.75rem;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  }
  .context-card-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #8B93A7;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 12px;
  }
  .automation-status-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
  }
  .automation-status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .automation-status-label {
    font-size: 0.72rem;
    color: #8B93A7;
    font-weight: 500;
    margin-bottom: 2px;
  }
  .automation-status-value {
    font-size: 0.95rem;
    font-weight: 700;
  }
  .automation-status-url {
    font-size: 0.72rem;
    color: #6B7280;
    margin-left: 20px;
    margin-bottom: 10px;
    word-break: break-all;
  }
  .automation-status-divider {
    height: 1px;
    background: #1F2937;
    margin: 10px 0;
  }
  .automation-status-workflows {
    margin-top: 4px;
    line-height: 1.4;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1420 0%, #0B0F19 100%);
    border-right: 1px solid #1F2937;
  }
  section[data-testid="stSidebar"] .block-container {
    padding-top: 1.25rem;
  }

  /* Sidebar nav — active page accent strip */
  section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(90deg, rgba(255, 109, 90, 0.18) 0%, rgba(255, 109, 90, 0.04) 100%) !important;
    border: 1px solid rgba(255, 109, 90, 0.35) !important;
    border-left: 3px solid #FF6D5A !important;
    color: #FFFFFF !important;
    box-shadow: none !important;
    transform: none !important;
    font-weight: 600 !important;
  }
  section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    transform: none !important;
    box-shadow: none !important;
    background: linear-gradient(90deg, rgba(255, 109, 90, 0.22) 0%, rgba(255, 109, 90, 0.06) 100%) !important;
  }
  section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #9CA3AF !important;
  }
  section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: rgba(21, 28, 47, 0.8) !important;
    border-color: #2A3144 !important;
    color: #E8EAEF !important;
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

  /* Buttons — main content only (sidebar overrides above) */
  section.main .stButton > button[kind="primary"],
  .main .stButton > button[kind="primary"],
  [data-testid="stAppViewContainer"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF6D5A 0%, #FF8F7A 100%);
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.6rem 1.25rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 2px 12px rgba(255, 109, 90, 0.25);
  }
  [data-testid="stAppViewContainer"] .stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(255, 109, 90, 0.35);
    border: none;
    color: white;
  }
  [data-testid="stAppViewContainer"] .stButton > button[kind="secondary"] {
    background: #151C2F;
    border: 1px solid #2A3144;
    border-radius: 10px;
    font-weight: 500;
    color: #C5CAD6;
  }
  [data-testid="stAppViewContainer"] .stButton > button[kind="secondary"]:hover {
    background: #1A2236;
    border-color: #3B4258;
    color: #FFFFFF;
  }

  /* Legacy button selectors (fallback) */
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

  /* Selectbox, radio, checkbox — match input surfaces */
  .stSelectbox > div > div,
  [data-baseweb="select"] > div {
    background: #111827 !important;
    border-color: #2A3144 !important;
    border-radius: 10px !important;
  }
  .stSelectbox label, .stRadio label, .stCheckbox label {
    color: #C5CAD6 !important;
    font-size: 0.875rem !important;
  }
  .stRadio > div[role="radiogroup"] {
    gap: 0.5rem;
  }
  .stRadio > div[role="radiogroup"] label {
    background: #151C2F;
    border: 1px solid #1F2937;
    border-radius: 10px;
    padding: 0.5rem 0.85rem;
    margin-right: 0.35rem;
  }
  [data-baseweb="popover"] li {
    background: #151C2F !important;
    color: #E8EAEF !important;
  }
  [data-baseweb="popover"] li:hover {
    background: #1A2236 !important;
  }

  /* Toasts — align with alert tones */
  [data-testid="stToast"] {
    background: #151C2F !important;
    border: 1px solid #2A3144 !important;
    border-radius: 10px !important;
    color: #E8EAEF !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
  }
  [data-testid="stToast"] p {
    color: #E8EAEF !important;
    font-size: 0.875rem !important;
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
  .dash-header-wrap {
    background: linear-gradient(135deg, rgba(21, 28, 47, 0.95) 0%, rgba(17, 24, 39, 0.75) 100%);
    border: 1px solid #1F2937;
    border-radius: 16px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  }
  .dash-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px 16px;
    margin-bottom: 0.25rem;
    flex-wrap: wrap;
  }
  .dash-header-main {
    display: flex;
    align-items: center;
    gap: 16px;
    min-width: 0;
    flex: 1 1 240px;
  }
  .dash-header-status {
    flex-shrink: 0;
    margin-left: auto;
  }
  @media (max-width: 720px) {
    .dash-title { font-size: 1.35rem; }
    .dash-subtitle { font-size: 0.82rem; }
    .dash-header-status { width: 100%; margin-left: 0; }
  }
  .dash-logo {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: linear-gradient(135deg, #FF6D5A 0%, #FF9F43 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.05rem;
    color: white;
    box-shadow: 0 4px 24px rgba(255, 109, 90, 0.4);
    flex-shrink: 0;
    letter-spacing: -0.02em;
  }
  .dash-title {
    font-size: 1.65rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    margin: 0;
    line-height: 1.2;
    background: linear-gradient(90deg, #FFFFFF 0%, #C5CAD6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .dash-subtitle {
    font-size: 0.9rem;
    color: #8B93A7;
    margin: 4px 0 0 0;
    font-weight: 400;
  }
  .section-card {
    background: linear-gradient(160deg, #151C2F 0%, #131a2e 100%);
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 1.35rem 1.6rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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
    line-height: 1.45;
  }
  .hub-panel {
    background: #151C2F;
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 1rem 1.25rem 0.75rem 1.25rem;
    margin-bottom: 1.25rem;
  }
  .hub-panel-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #8B93A7;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin: 0 0 0.75rem 0;
  }
  .generator-gemini-section {
    background: linear-gradient(160deg, #151C2F 0%, #12182a 100%);
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 1.35rem 1.5rem 0.25rem 1.5rem;
    margin-bottom: 0.75rem;
    position: relative;
    overflow: hidden;
  }
  .generator-gemini-section::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #FF6D5A, transparent);
    opacity: 0.7;
  }
  .generator-gemini-section .gen-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #FF8F7A;
    background: rgba(255, 109, 90, 0.12);
    border: 1px solid rgba(255, 109, 90, 0.25);
    border-radius: 6px;
    padding: 3px 8px;
    margin-bottom: 0.65rem;
  }
  .generator-gemini-section h3 {
    margin: 0 0 0.35rem 0;
    font-size: 1.15rem;
    font-weight: 600;
    color: #FFFFFF;
  }
  .generator-gemini-section p {
    margin: 0 0 1rem 0;
    font-size: 0.85rem;
    color: #8B93A7;
    line-height: 1.45;
  }

  .template-tile {
    background: linear-gradient(160deg, #151C2F 0%, #12182a 100%);
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 16px 14px 6px 14px;
    margin-bottom: 0.35rem;
    min-height: 96px;
    transition: border-color 0.2s ease, transform 0.15s ease, box-shadow 0.15s ease;
  }
  .template-tile:hover {
    border-color: rgba(255, 109, 90, 0.35);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  }
  .template-tile-icon { font-size: 1.5rem; margin-bottom: 6px; }
  .template-tile-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #FFFFFF;
    line-height: 1.25;
    margin-bottom: 4px;
  }
  .template-tile-desc {
    font-size: 0.72rem;
    color: #8B93A7;
    line-height: 1.3;
    margin-bottom: 0;
  }
  @media (max-width: 900px) {
    .template-tile { min-height: auto; }
  }

  .history-card {
    background: linear-gradient(160deg, #151C2F 0%, #12182a 100%);
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 14px 16px 8px 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s ease;
  }
  .history-card:hover { border-color: #2A3144; }
  .history-item {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    margin-bottom: 0;
  }
  .history-item-actions {
    margin-bottom: 12px;
  }
  .history-item-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 4px;
  }
  .history-item-meta {
    font-size: 0.75rem;
    color: #8B93A7;
    margin-bottom: 8px;
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
  .status-pill.header-status-pill {
    margin-top: 0;
    padding: 6px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    white-space: nowrap;
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
  .status-pill.neutral {
    background: rgba(107, 114, 128, 0.12);
    border: 1px solid rgba(107, 114, 128, 0.22);
    color: #9CA3AF;
  }
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
    flex-shrink: 0;
  }
  .status-dot-pulse {
    animation: docker-pulse 1.5s ease-in-out infinite;
  }
  .empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(160deg, #151C2F 0%, #111827 100%);
    border: 1px solid #1F2937;
    border-radius: 16px;
    margin-top: 0.5rem;
    margin-bottom: 0.75rem;
  }
  .empty-state .icon {
    font-size: 2.75rem;
    margin-bottom: 0.85rem;
    opacity: 0.75;
    filter: grayscale(0.2);
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
  .flow-map-card {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
  }
  .flow-map-card h4 {
    margin: 0 0 0.75rem 0;
    font-size: 0.95rem;
    font-weight: 600;
    color: #E8EAEF;
  }
  .flow-text-path {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #FF6D5A;
    background: #0B0F19;
    border: 1px solid #2A3144;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 1rem;
    overflow-x: auto;
    white-space: nowrap;
  }
  .node-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
  }
  .node-chip {
    background: #151C2F;
    border: 1px solid #2A3144;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.75rem;
    color: #C5CAD6;
  }
  .node-chip strong { color: #FFFFFF; }
  .node-chip span { color: #8B93A7; margin-left: 6px; }

  /* Automation Hub — sidebar */
  .hub-sidebar-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8B93A7;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }
  .hub-sidebar-badge {
    background: linear-gradient(135deg, #FF6D5A, #FF9F43);
    color: #fff;
    font-size: 0.6rem;
    padding: 2px 6px;
    border-radius: 4px;
    letter-spacing: 0.08em;
  }
  .hub-sidebar-sub {
    font-size: 0.75rem;
    color: #6B7280;
    margin: 0 0 12px 0;
  }
  .hub-nav-hint {
    margin-top: 10px;
    padding: 10px 12px;
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 10px;
    font-size: 0.75rem;
    color: #8B93A7;
    line-height: 1.4;
  }
  .hub-nav-hint strong { color: #E8EAEF; font-size: 0.8rem; }

  /* Hub overview cards */
  .hub-card {
    background: linear-gradient(160deg, #151C2F 0%, #12182a 100%);
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 1.35rem 1.15rem;
    text-align: center;
    margin-bottom: 8px;
    min-height: 148px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: border-color 0.2s ease, transform 0.15s ease, box-shadow 0.15s ease;
    position: relative;
    overflow: hidden;
  }
  .hub-card::after {
    content: "";
    position: absolute;
    top: 0; left: 20%; right: 20%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 109, 90, 0.5), transparent);
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  .hub-card:hover {
    border-color: rgba(255, 109, 90, 0.3);
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
  }
  .hub-card:hover::after { opacity: 1; }
  .hub-card-icon { font-size: 1.75rem; margin-bottom: 8px; }
  .hub-card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 4px;
  }
  .hub-card-desc {
    font-size: 0.75rem;
    color: #8B93A7;
    line-height: 1.35;
  }

  .docker-status-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    background: linear-gradient(90deg, rgba(21, 28, 47, 0.95) 0%, rgba(17, 24, 39, 0.8) 100%);
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 0.75rem;
  }
  .docker-status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .docker-status-text {
    font-size: 0.9rem;
    font-weight: 600;
  }
  @keyframes docker-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .docker-log-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }
  .docker-log-panel {
    background: #0D1117;
    border: 1px solid #1F2937;
    border-radius: 12px;
    max-height: 220px;
    overflow-y: auto;
    padding: 8px;
    font-family: "SF Mono", "Cascadia Code", Consolas, monospace;
    font-size: 0.78rem;
  }
  .docker-log-panel:empty::before,
  .docker-log-empty {
    color: #6B7280;
    font-style: italic;
    padding: 12px;
    display: block;
  }
  .docker-log-entry {
    border-left: 3px solid #374151;
    border-radius: 6px;
    padding: 8px 10px;
    margin-bottom: 6px;
    background: #151C2F;
  }
  .docker-log-entry:last-child { margin-bottom: 0; }
  .docker-log-entry.docker-log-success {
    border-left-color: #34D399;
    background: rgba(52, 211, 153, 0.08);
  }
  .docker-log-entry.docker-log-error {
    border-left-color: #F87171;
    background: rgba(248, 113, 113, 0.08);
  }
  .docker-log-entry.docker-log-info {
    border-left-color: #60A5FA;
    background: rgba(96, 165, 250, 0.06);
  }
  .docker-log-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: baseline;
    margin-bottom: 4px;
  }
  .docker-log-time { color: #6B7280; font-size: 0.72rem; }
  .docker-log-cmd { color: #A5B4FC; font-weight: 600; }
  .docker-log-msg-success { color: #34D399; font-weight: 600; }
  .docker-log-msg-error { color: #F87171; font-weight: 600; }
  .docker-log-msg-info { color: #93C5FD; font-weight: 600; }
  .docker-log-detail {
    margin: 4px 0 0 0;
    padding: 6px 8px;
    background: rgba(0, 0, 0, 0.25);
    border-radius: 4px;
    color: #D1D5DB;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: 0.72rem;
    line-height: 1.4;
  }

  .workflow-json-editor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 14px;
    background: #151C2F;
    border: 1px solid #1F2937;
    border-radius: 12px 12px 0 0;
    margin-bottom: 0;
  }
  .workflow-json-editor-header .label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #E8EAEF;
    letter-spacing: 0.02em;
  }
  .workflow-json-editor-header .hint {
    font-size: 0.72rem;
    color: #6B7280;
  }
  .workflow-json-editor-wrap {
    border: 1px solid #1F2937;
    border-top: none;
    border-radius: 0 0 12px 12px;
    overflow: hidden;
    background: #0D1117;
    margin-bottom: 0.5rem;
  }
  .workflow-json-editor-wrap .ace_editor {
    font-family: 'JetBrains Mono', 'SF Mono', Consolas, monospace !important;
  }
  .workflow-json-status {
    font-size: 0.8rem;
    font-weight: 600;
    padding: 6px 10px;
    border-radius: 8px;
    display: inline-block;
  }
  .workflow-json-status.ok {
    color: #34D399;
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.25);
  }
  .workflow-json-status.err {
    color: #F87171;
    background: rgba(248, 113, 113, 0.1);
    border: 1px solid rgba(248, 113, 113, 0.25);
  }

  .push-feedback {
    border-radius: 12px;
    padding: 14px 16px;
    margin: 0.75rem 0 1rem 0;
    font-size: 0.88rem;
    line-height: 1.45;
  }
  .push-feedback.success {
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.3);
    color: #D1FAE5;
  }
  .push-feedback.success strong { color: #34D399; }
  .push-feedback.error {
    background: rgba(248, 113, 113, 0.1);
    border: 1px solid rgba(248, 113, 113, 0.3);
    color: #FECACA;
  }
  .push-feedback.error strong { color: #F87171; }
  .push-feedback-meta {
    color: #9CA3AF;
    font-size: 0.8rem;
    margin-top: 6px;
  }

  .user-feedback-banner {
    border-radius: 12px;
    padding: 12px 14px;
    margin: 0.5rem 0 0.75rem 0;
    font-size: 0.85rem;
    line-height: 1.45;
  }
  .user-feedback-banner.error {
    background: rgba(248, 113, 113, 0.1);
    border: 1px solid rgba(248, 113, 113, 0.3);
    color: #FECACA;
  }
  .user-feedback-banner.error strong { color: #F87171; }
  .user-feedback-banner.success {
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.3);
    color: #D1FAE5;
  }
  .user-feedback-banner.warning {
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid rgba(251, 191, 36, 0.25);
    color: #FDE68A;
  }
  .user-feedback-hint {
    color: #9CA3AF;
    font-size: 0.78rem;
    margin-top: 6px;
    line-height: 1.35;
  }

  /* Floating generator FAB — subtle, matches primary accent */
  .st-key-fab_open_workflow_generator {
    position: fixed !important;
    bottom: 1.5rem !important;
    right: 1.5rem !important;
    z-index: 1000 !important;
    width: auto !important;
  }
  .st-key-fab_open_workflow_generator button {
    border-radius: 999px !important;
    width: 3.25rem !important;
    height: 3.25rem !important;
    min-height: 3.25rem !important;
    padding: 0 !important;
    font-size: 1.25rem !important;
    line-height: 1 !important;
    box-shadow: 0 4px 14px rgba(255, 109, 90, 0.3) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
  }
  .st-key-fab_open_workflow_generator button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(255, 109, 90, 0.38) !important;
  }
  @media (max-width: 720px) {
    .st-key-fab_open_workflow_generator {
      bottom: 1rem !important;
      right: 1rem !important;
    }
    .stat-grid { grid-template-columns: repeat(2, 1fr) !important; }
    .gen-steps { flex-direction: column; }
  }

  /* Page breadcrumb chip */
  .page-chip {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(21, 28, 47, 0.8);
    border: 1px solid #1F2937;
    border-radius: 999px;
    padding: 8px 16px;
    margin-bottom: 1.25rem;
    font-size: 0.85rem;
    color: #8B93A7;
  }
  .page-chip .page-chip-icon { font-size: 1.1rem; line-height: 1; }
  .page-chip strong { color: #E8EAEF; font-weight: 600; }

  /* Section labels */
  .section-label {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    margin: 1.5rem 0 0.85rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1F2937;
  }
  .section-label h4 {
    margin: 0;
    font-size: 0.95rem;
    font-weight: 600;
    color: #E8EAEF;
    letter-spacing: -0.01em;
  }
  .section-label span {
    font-size: 0.75rem;
    color: #6B7280;
  }

  /* Stat grid (hub home) */
  .stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 1rem 0 1.25rem 0;
  }
  .stat-card {
    background: linear-gradient(160deg, #151C2F 0%, #12182a 100%);
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 1rem 1.15rem;
    transition: border-color 0.2s ease;
  }
  .stat-card:hover { border-color: #2A3144; }
  .stat-card .stat-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #8B93A7;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
  }
  .stat-card .stat-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.1;
  }
  .stat-card.accent .stat-value { color: #FF8F7A; }
  .stat-card.green .stat-value { color: #34D399; }
  .stat-card.warn .stat-value { color: #FBBF24; }

  /* Generator flow steps */
  .gen-steps {
    display: flex;
    gap: 10px;
    margin-bottom: 1.25rem;
  }
  .gen-step {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(21, 28, 47, 0.6);
    border: 1px solid #1F2937;
    border-radius: 10px;
    font-size: 0.78rem;
    font-weight: 500;
    color: #6B7280;
  }
  .gen-step-num {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: #111827;
    border: 1px solid #2A3144;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
  }
  .gen-step.active {
    color: #E8EAEF;
    border-color: rgba(255, 109, 90, 0.35);
    background: rgba(255, 109, 90, 0.08);
  }
  .gen-step.active .gen-step-num {
    background: linear-gradient(135deg, #FF6D5A, #FF8F7A);
    border-color: transparent;
    color: #fff;
  }
  .gen-step.done { color: #9CA3AF; }
  .gen-step.done .gen-step-num {
    background: rgba(52, 211, 153, 0.15);
    border-color: rgba(52, 211, 153, 0.3);
    color: #34D399;
  }

  /* Action toolbar */
  .action-toolbar {
    background: linear-gradient(160deg, #151C2F 0%, #12182a 100%);
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 14px 16px 6px 16px;
    margin: 1rem 0;
  }
  .action-toolbar-title {
    font-size: 0.72rem;
    font-weight: 600;
    color: #8B93A7;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
  }

  /* Context tips card */
  .context-tips-card {
    background: rgba(17, 24, 39, 0.8);
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 12px 14px;
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #8B93A7;
    line-height: 1.5;
  }
  .context-tips-card strong { color: #C5CAD6; display: block; margin-bottom: 6px; font-size: 0.78rem; }
  .context-tips-card kbd {
    background: #151C2F;
    border: 1px solid #2A3144;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 0.68rem;
    color: #E8EAEF;
  }
</style>
"""


def inject_styles() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _n8n_status_pill_html(status) -> str:
    """Build HTML for the n8n runtime status pill."""
    import html

    labels = {
        "running": "n8n Running",
        "stopped": "n8n Stopped",
        "starting": "n8n Starting",
        "unknown": "n8n Unavailable",
    }
    levels = {
        "running": "ok",
        "stopped": "neutral",
        "starting": "warn",
        "unknown": "neutral",
    }
    label = labels.get(status.state, "n8n Unknown")
    level = levels.get(status.state, "warn")
    pulse = " status-dot-pulse" if status.state == "starting" else ""
    title = html.escape(status.message or label)

    return (
        f'<div class="status-pill header-status-pill {level}" title="{title}">'
        f'<span class="status-dot{pulse}"></span>{label}</div>'
    )


def render_n8n_status_pill(status=None) -> None:
    """Render a compact n8n running / stopped pill."""
    if status is None:
        from services.docker_service import get_n8n_status

        status = get_n8n_status()

    st.markdown(
        f'<div class="dash-header-status">{_n8n_status_pill_html(status)}</div>',
        unsafe_allow_html=True,
    )


def render_header() -> None:
    from services.docker_service import get_n8n_status

    status = get_n8n_status()
    pill_html = _n8n_status_pill_html(status)

    st.markdown(
        f"""
        <div class="dash-header-wrap">
          <div class="dash-header">
            <div class="dash-header-main">
              <div class="dash-logo">n8</div>
              <div>
                <p class="dash-title">n8n AI Management Dashboard</p>
                <p class="dash-subtitle">Automation Hub — generate, deploy, and monitor n8n workflows</p>
              </div>
            </div>
            <div class="dash-header-status">{pill_html}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_chip(icon: str, label: str, description: str) -> None:
    """Breadcrumb-style current page indicator."""
    st.markdown(
        f"""
        <div class="page-chip">
          <span class="page-chip-icon">{icon}</span>
          <span><strong>{label}</strong> — {description}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(title: str, subtitle: str = "") -> None:
    """Styled section heading with optional subtitle."""
    sub_html = f"<span>{subtitle}</span>" if subtitle else ""
    st.markdown(
        f"""
        <div class="section-label">
          <h4>{title}</h4>
          {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_grid(workflows: int, active: int, executions: int, failed: int) -> None:
    """Hub overview stat cards."""
    st.markdown(
        f"""
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-label">Workflows</div>
            <div class="stat-value">{workflows}</div>
          </div>
          <div class="stat-card green">
            <div class="stat-label">Active</div>
            <div class="stat-value">{active}</div>
          </div>
          <div class="stat-card accent">
            <div class="stat-label">Recent runs</div>
            <div class="stat-value">{executions}</div>
          </div>
          <div class="stat-card warn">
            <div class="stat-label">Failed</div>
            <div class="stat-value">{failed}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_generator_steps(*, has_workflow: bool = False) -> None:
    """Visual 3-step flow for the generator page."""
    step1 = "gen-step active" if not has_workflow else "gen-step done"
    step2 = "gen-step active" if has_workflow else "gen-step"
    step3 = "gen-step"
    st.markdown(
        f"""
        <div class="gen-steps">
          <div class="{step1}">
            <span class="gen-step-num">1</span> Describe automation
          </div>
          <div class="{step2}">
            <span class="gen-step-num">2</span> Generate & edit JSON
          </div>
          <div class="{step3}">
            <span class="gen-step-num">3</span> Push to n8n
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
          <span>Automation Hub</span>
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


def render_flow_map(mermaid_diagram: str, text_flow: str, node_summaries: list) -> None:
    """Render text path, node chips, and Mermaid flowchart for a generated workflow."""
    import html

    import streamlit as st

    st.markdown('<div class="flow-map-card"><h4>📊 Pipeline Preview</h4>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="flow-text-path">{html.escape(text_flow)}</div>',
        unsafe_allow_html=True,
    )

    if node_summaries:
        chips = "".join(
            f'<div class="node-chip"><strong>{html.escape(n["name"])}</strong>'
            f'<span>{html.escape(n["type"])}</span></div>'
            for n in node_summaries
        )
        st.markdown(f'<div class="node-chip-row">{chips}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    safe_diagram = mermaid_diagram.replace("`", "'")

    # Native Streamlit Mermaid (single render — duplicate iframe removed for performance)
    st.markdown(f"```mermaid\n{safe_diagram}\n```")


def render_copy_json_button(
    json_str: str,
    button_key: str = "copy_json",
    *,
    label: str = "Copy JSON",
    compact: bool = False,
) -> None:
    """One-click clipboard copy for workflow JSON."""
    import json

    import streamlit.components.v1 as components

    escaped = json.dumps(json_str)
    padding = "10px 14px" if compact else "10px 20px"
    font_size = "0.8rem" if compact else "0.875rem"
    default_label = label
    components.html(
        f"""
        <button id="btn_{button_key}" style="
          background: linear-gradient(135deg, #151C2F 0%, #1A2236 100%);
          border: 1px solid #2A3144;
          border-radius: 10px;
          color: #E8EAEF;
          font-family: Inter, system-ui, sans-serif;
          font-size: {font_size};
          font-weight: 600;
          padding: {padding};
          cursor: pointer;
          transition: all 0.15s ease;
          width: 100%;
        "
        onmouseover="this.style.borderColor='#FF6D5A'; this.style.color='#FFFFFF';"
        onmouseout="this.style.borderColor='#2A3144'; this.style.color='#E8EAEF';"
        onclick="
          navigator.clipboard.writeText({escaped}).then(() => {{
            const b = document.getElementById('btn_{button_key}');
            b.innerText = '✓ Copied';
            b.style.borderColor = '#10B981';
            b.style.color = '#34D399';
            setTimeout(() => {{
              b.innerText = {json.dumps(default_label)};
              b.style.borderColor = '#2A3144';
              b.style.color = '#E8EAEF';
            }}, 2000);
          }});
        ">
          {label}
        </button>
        """,
        height=44 if compact else 52,
    )


def render_workflow_json_editor(workflow: dict) -> dict:
    """
    Editable JSON preview with syntax highlighting (Ace editor).

    Parses edits on each rerun; returns the current workflow dict (edited or last valid).
    """
    import html
    import json

    from streamlit_ace import st_ace

    from utils.json_utils import normalize_workflow, parse_workflow_json
    from utils.user_feedback import explain_json_error

    if "workflow_json_text" not in st.session_state:
        st.session_state.workflow_json_text = json.dumps(workflow, indent=2)
    if "workflow_editor_nonce" not in st.session_state:
        st.session_state.workflow_editor_nonce = 0
    if "workflow_json_error" not in st.session_state:
        st.session_state.workflow_json_error = None

    toolbar_left, toolbar_right = st.columns([2, 1])
    with toolbar_left:
        st.caption("Changes apply when the JSON is valid. Use **Format JSON** to tidy spacing.")
    with toolbar_right:
        if st.button(
            "Format JSON",
            key="format_workflow_json",
            use_container_width=True,
            type="secondary",
        ):
            try:
                parsed = json.loads(st.session_state.workflow_json_text)
                st.session_state.workflow_json_text = json.dumps(parsed, indent=2)
                st.session_state.workflow_editor_nonce += 1
                st.session_state.workflow_json_error = None
                st.rerun()
            except json.JSONDecodeError as exc:
                fb = explain_json_error(exc)
                st.session_state.workflow_json_error = fb.as_plain()

    st.markdown(
        """
        <div class="workflow-json-editor-header">
          <span class="label">Edit JSON</span>
          <span class="hint">Syntax highlighting · scroll to navigate</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="workflow-json-editor-wrap">', unsafe_allow_html=True)
    edited_json = st_ace(
        value=st.session_state.workflow_json_text,
        language="json",
        theme="tomorrow_night",
        key=f"workflow_json_ace_{st.session_state.workflow_editor_nonce}",
        height=460,
        font_size=13,
        tab_size=2,
        show_gutter=True,
        show_print_margin=False,
        wrap=False,
        auto_update=True,
        readonly=False,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if edited_json is None:
        edited_json = st.session_state.workflow_json_text

    if edited_json != st.session_state.workflow_json_text:
        st.session_state.workflow_json_text = edited_json
        try:
            parsed = normalize_workflow(parse_workflow_json(edited_json))
            st.session_state.generated_workflow = parsed
            st.session_state.workflow_json_error = None
            return parsed
        except ValueError as exc:
            fb = explain_json_error(exc)
            st.session_state.workflow_json_error = fb.as_plain()

    if st.session_state.workflow_json_error:
        st.markdown(
            f'<span class="workflow-json-status err">✕ {html.escape(st.session_state.workflow_json_error)}</span>',
            unsafe_allow_html=True,
        )
        return st.session_state.get("generated_workflow", workflow)

    st.markdown(
        '<span class="workflow-json-status ok">✓ Valid n8n workflow JSON</span>',
        unsafe_allow_html=True,
    )
    return st.session_state.get("generated_workflow", workflow)


def reset_workflow_json_editor(workflow: dict) -> None:
    """Load freshly generated workflow into the editor."""
    import json

    st.session_state.workflow_json_text = json.dumps(workflow, indent=2)
    st.session_state.workflow_json_error = None
    st.session_state.workflow_editor_nonce = st.session_state.get("workflow_editor_nonce", 0) + 1


def render_push_feedback(result: dict | None) -> None:
    """Show success or error banner after a push to n8n."""
    if not result:
        return

    import html

    from utils.user_feedback import (
        explain_n8n_failure,
        feedback_for_session_message,
        render_feedback_banner,
        show_user_feedback,
    )

    if result.get("success"):
        name = html.escape(str(result.get("workflow_name") or "Workflow"))
        wf_id = html.escape(str(result.get("workflow_id") or ""))
        instance = html.escape(str(result.get("instance_url") or ""))
        nodes = result.get("node_count")
        editor_url = result.get("editor_url") or ""
        editor_link = (
            f'<br/><a href="{html.escape(editor_url)}" target="_blank" '
            f'style="color:#34D399;font-weight:600;">Open in n8n editor ↗</a>'
            if editor_url
            else ""
        )
        st.markdown(
            f"""
            <div class="push-feedback success">
              <strong>✓ Pushed to n8n successfully</strong><br/>
              <strong>{name}</strong> is now on your instance.<br/>
              Workflow ID: <code>{wf_id}</code>
              {f" · {nodes} nodes" if nodes is not None else ""}
              {editor_link}
              <div class="push-feedback-meta">Instance: {instance}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if not result.get("status_code"):
        show_user_feedback(feedback_for_session_message(result.get("error") or "Push to n8n failed."))
        return

    fb = explain_n8n_failure(result.get("error"), result.get("status_code"))
    render_feedback_banner(fb, css_class="push-feedback")
    instance = html.escape(str(result.get("instance_url") or ""))
    if instance:
        st.markdown(f'<div class="push-feedback-meta">Instance: {instance}</div>', unsafe_allow_html=True)
