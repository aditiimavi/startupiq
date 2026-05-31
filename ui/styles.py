"""Global CSS for StartupIQ dashboard."""

import streamlit as st


def inject_custom_css() -> None:
    """Apply modern dashboard styling across all pages."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        #MainMenu, footer, header { visibility: hidden; }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        /* Brand hero */
        .siq-hero {
            background: linear-gradient(135deg, #312E81 0%, #4F46E5 45%, #7C3AED 100%);
            border-radius: 16px;
            padding: 1.75rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 40px rgba(79, 70, 229, 0.25);
        }
        .siq-hero h1 {
            color: #FFFFFF;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 0.35rem 0;
            letter-spacing: -0.02em;
        }
        .siq-hero p {
            color: rgba(255,255,255,0.85);
            margin: 0;
            font-size: 1rem;
        }
        .siq-badge {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            color: #E0E7FF;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            margin-bottom: 0.75rem;
        }

        /* Metric cards */
        .siq-metric-card {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.1rem 1.25rem;
            height: 100%;
        }
        .siq-metric-label {
            color: #94A3B8;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.35rem;
        }
        .siq-metric-value {
            color: #F8FAFC;
            font-size: 1.75rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .siq-metric-sub {
            color: #64748B;
            font-size: 0.8rem;
            margin-top: 0.25rem;
        }

        /* Health score ring */
        .siq-health-wrap {
            background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        }
        .siq-health-score {
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1;
            background: linear-gradient(135deg, #34D399, #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .siq-health-score.warn {
            background: linear-gradient(135deg, #FBBF24, #F59E0B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .siq-health-score.critical {
            background: linear-gradient(135deg, #F87171, #EF4444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .siq-health-label {
            color: #94A3B8;
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }
        .siq-health-tier {
            display: inline-block;
            margin-top: 0.75rem;
            padding: 0.35rem 1rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            background: rgba(99, 102, 241, 0.2);
            color: #A5B4FC;
        }

        /* Agent status rows */
        .siq-agent-row {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.65rem 0.85rem;
            margin-bottom: 0.5rem;
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 10px;
            font-size: 0.9rem;
        }
        .siq-agent-row.complete { border-color: rgba(52, 211, 153, 0.4); }
        .siq-agent-row.running {
            border-color: rgba(99, 102, 241, 0.6);
            box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.2);
        }
        .siq-agent-row.pending { opacity: 0.55; }
        .siq-agent-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .siq-agent-dot.complete { background: #34D399; }
        .siq-agent-dot.running {
            background: #6366F1;
            animation: siq-pulse 1.2s ease-in-out infinite;
        }
        .siq-agent-dot.pending { background: #475569; }
        .siq-agent-dot.error { background: #EF4444; }

        @keyframes siq-pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.15); }
        }

        .siq-agent-name { color: #E2E8F0; flex: 1; }
        .siq-agent-status {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .siq-agent-status.complete { color: #34D399; }
        .siq-agent-status.running { color: #818CF8; }
        .siq-agent-status.pending { color: #64748B; }
        .siq-agent-status.error { color: #F87171; }

        /* Section panels */
        .siq-panel {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
        }
        .siq-panel-title {
            color: #F1F5F9;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }

        /* Sidebar nav highlight */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
            border-right: 1px solid #334155;
        }
        section[data-testid="stSidebar"] .stRadio label {
            font-weight: 500;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
