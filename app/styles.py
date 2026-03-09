# ─────────────────────────────────────────────
#  styles.py — Tokens de tema e CSS dinâmico
# ─────────────────────────────────────────────

DARK = {
    # ── Fundos ──────────────────────────────────────────────────
    "app_bg":           "#0d0f14",
    "sidebar_bg":       "#111318",
    "sidebar_border":   "#4da6ff30",
    "card_bg":          "#161920",
    "card_border":      "#252a38",
    "tab_border":       "#252a38",
    "df_border":        "#252a38",
    "map_container_bg": "#0d0f14",
    "map_container_bd": "#252a38",
    "empty_border":     "#252a38",
    "empty_hex":        "#252a38",
    # ── Textos ──────────────────────────────────────────────────
    "empty_text":       "#8896aa",
    "empty_sub":        "#566070",
    "header_border":    "#4da6ff30",
    "title_color":      "#eef0f5",
    "subtitle_color":   "#8896aa",
    "label_color":      "#8896aa",
    "unit_color":       "#8896aa",
    "section_color":    "#8896aa",
    "body_color":       "#c8d0dc",
    "section_border":   "#252a38",
    "sidebar_label":    "#b0bccb",
    "input_bg":         "#1a1d26",
    "input_border":     "#4da6ff60",
    "grid_color":       "rgba(77,166,255,0.04)",
    # ── Acento ──────────────────────────────────────────────────
    "accent":           "#4da6ff",
    "accent_15":        "#4da6ff18",
    "accent_25":        "#4da6ff30",
    "accent_40":        "#4da6ff50",
    "accent_50":        "#4da6ff65",
    "accent_hover":     "#74bcff",
    "status_bg":        "#0d1525",
    "status_border":    "#1a3560",
    "map_tiles":        "CartoDB positron",
    "toggle_icon":      "☀️",
    "toggle_label":     "Modo Claro",
}

LIGHT = {
    # ── Fundos ──────────────────────────────────────────────────
    "app_bg":           "#f0f2f5",
    "sidebar_bg":       "#ffffff",
    "sidebar_border":   "#1a75d225",
    "card_bg":          "#ffffff",
    "card_border":      "#dce1ea",
    "tab_border":       "#dce1ea",
    "df_border":        "#dce1ea",
    "map_container_bg": "#ffffff",
    "map_container_bd": "#dce1ea",
    "empty_border":     "#d0d6e2",
    "empty_hex":        "#b8c2d4",
    # ── Textos ──────────────────────────────────────────────────
    "empty_text":       "#5a6478",
    "empty_sub":        "#8a95a8",
    "header_border":    "#1a75d220",
    "title_color":      "#111827",
    "subtitle_color":   "#5a6478",
    "label_color":      "#5a6478",
    "unit_color":       "#5a6478",
    "section_color":    "#5a6478",
    "body_color":       "#374151",
    "section_border":   "#dce1ea",
    "sidebar_label":    "#374151",
    "input_bg":         "#f4f6f9",
    "input_border":     "#1a75d250",
    "grid_color":       "rgba(26,117,210,0.04)",
    # ── Acento ──────────────────────────────────────────────────
    "accent":           "#1a75d2",
    "accent_15":        "#1a75d215",
    "accent_25":        "#1a75d225",
    "accent_40":        "#1a75d240",
    "accent_50":        "#1a75d255",
    "accent_hover":     "#1260b0",
    "status_bg":        "#f0f5ff",
    "status_border":    "#a0c0f0",
    "map_tiles":        "CartoDB positron",
    "toggle_icon":      "🌙",
    "toggle_label":     "Modo Escuro",
}


def get_theme(session_state):
    return DARK if session_state.get("tema", "dark") == "dark" else LIGHT


def inject_css(T):
    """Retorna a string CSS completa com os tokens do tema aplicados."""
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;500;600;700&family=Barlow+Condensed:wght@600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Barlow', sans-serif;
}}

/* ── App background ── */
.stApp {{
    background-color: {T['app_bg']};
    background-image:
        linear-gradient({T['grid_color']} 1px, transparent 1px),
        linear-gradient(90deg, {T['grid_color']} 1px, transparent 1px);
    background-size: 40px 40px;
    transition: background-color 0.3s ease;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['sidebar_border']} !important;
    transition: background-color 0.3s ease;
}}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider p,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stSlider > label {{
    color: {T['title_color']} !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    line-height: 1.5 !important;
}}

[data-testid="stSidebar"] .stTextInput input {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['input_border']} !important;
    color: {T['accent']} !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 15px !important;
    border-radius: 4px !important;
}}

/* ── Sliders ── */
[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
    background-color: {T['accent']} !important;
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 4px {T['accent_25']} !important;
}}

:root {{ --primary-color: {T['accent']} !important; }}

[data-testid="stSidebar"] [data-baseweb="slider"] div[style*="background: rgb(255"],
[data-testid="stSidebar"] [data-baseweb="slider"] div[style*="background-color: rgb(255"] {{
    background: {T['accent']} !important;
    background-color: {T['accent']} !important;
}}

[data-testid="stSidebar"] [data-baseweb="slider"] div[data-testid="stSliderTrackFill"],
[data-testid="stSidebar"] [data-baseweb="slider"] > div > div > div:first-child > div,
[data-testid="stSidebar"] .stSlider > div > div > div > div {{
    background: {T['accent']} !important;
}}

[data-testid="stSidebar"] [data-testid="stSlider"] p,
[data-testid="stSidebar"] .stSlider p {{
    color: #ffffff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}}

/* ── Tabs ── */
[data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {T['tab_border']} !important;
    gap: 0 !important;
}}

[data-baseweb="tab"] {{
    background: transparent !important;
    border: none !important;
    color: {T['label_color']} !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 14px 28px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s !important;
    line-height: 1 !important;
}}

[aria-selected="true"][data-baseweb="tab"] {{
    color: {T['accent']} !important;
    border-bottom: 2px solid {T['accent']} !important;
    background: transparent !important;
}}

[data-baseweb="tab"]:hover {{ color: {T['accent_hover']} !important; }}
[data-baseweb="tab-highlight"] {{ background-color: {T['accent']} !important; }}
[data-baseweb="tab-border"] {{ background-color: {T['tab_border']} !important; }}

/* ── Botão toggle sidebar ── */
[data-testid="stSidebar"] .stButton button {{
    background: {T['accent_15']} !important;
    border: 1px solid {T['accent_40']} !important;
    color: {T['accent']} !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    border-radius: 4px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}}

[data-testid="stSidebar"] .stButton button:hover {{
    background: {T['accent_25']} !important;
    border-color: {T['accent']} !important;
}}

/* ── Botão colapso sidebar ── */
button[kind="header"],
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebar"] button[kind="header"] {{
    background: {T['accent_25']} !important;
    border: 1px solid {T['accent_40']} !important;
    border-radius: 6px !important;
    color: {T['accent']} !important;
    width: 36px !important;
    height: 36px !important;
    transition: all 0.2s ease !important;
}}

button[kind="header"]:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {{
    background: {T['accent_40']} !important;
}}

button[kind="header"] svg,
[data-testid="stSidebarCollapsedControl"] button svg {{
    fill: {T['accent']} !important;
    stroke: {T['accent']} !important;
}}

[data-testid="stSidebarCollapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}}

/* ── Header principal ── */
.main-header {{
    padding: 28px 0 20px 0;
    border-bottom: 1px solid {T['header_border']};
    margin-bottom: 28px;
}}

.main-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 44px;
    font-weight: 700;
    color: {T['title_color']};
    letter-spacing: -0.5px;
    line-height: 1.1;
    margin: 0;
}}

.main-title span {{ color: {T['accent']}; }}

.main-subtitle {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: {T['subtitle_color']};
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 6px 0 0 0;
    line-height: 1.6;
}}

.live-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {T['accent_15']};
    border: 1px solid {T['accent_40']};
    border-radius: 4px;
    padding: 5px 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: {T['accent']};
    letter-spacing: 0.1em;
    margin-bottom: 10px;
}}

.live-dot {{
    width: 6px; height: 6px;
    background: {T['accent']};
    border-radius: 50%;
    animation: pulse 1.5s infinite;
    flex-shrink: 0;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50%       {{ opacity: 0.2; }}
}}

/* ── Metric cards ── */
.metric-card {{
    background: {T['card_bg']};
    border: 1px solid {T['card_border']};
    border-top: 2px solid {T['accent']};
    border-radius: 8px;
    padding: 22px 24px 20px;
    position: relative;
    overflow: hidden;
    transition: background-color 0.3s ease;
}}

.metric-card::after {{
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 70px; height: 70px;
    background: radial-gradient(circle at top right, {T['accent_15']}, transparent 70%);
}}

.metric-label {{
    font-family: 'Barlow', sans-serif;
    font-size: 11px;
    font-weight: 700;
    color: {T['label_color']};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
    line-height: 1.4;
}}

.metric-value {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 40px;
    font-weight: 700;
    color: {T['accent']};
    line-height: 1;
    margin-bottom: 6px;
}}

.metric-unit {{
    font-family: 'Barlow', sans-serif;
    font-size: 13px;
    color: {T['unit_color']};
    font-weight: 400;
    line-height: 1.5;
}}

/* ── DataFrame ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {T['df_border']} !important;
    border-radius: 8px !important;
    overflow: hidden;
}}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {{
    background: transparent !important;
    border: 1px solid {T['accent_50']} !important;
    color: {T['accent']} !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    border-radius: 4px !important;
    transition: all 0.2s !important;
}}

[data-testid="stDownloadButton"] button:hover {{
    background: {T['accent_15']} !important;
    border-color: {T['accent']} !important;
}}

/* ── Section title ── */
.section-title {{
    font-family: 'Barlow', sans-serif;
    font-size: 11px;
    font-weight: 700;
    color: {T['section_color']};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid {T['section_border']};
    line-height: 1.4;
}}

/* ── Alert ── */
[data-testid="stAlert"] {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['accent_40']} !important;
    border-left: 3px solid {T['accent']} !important;
    border-radius: 4px !important;
    color: {T['sidebar_label']} !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}}

/* ── Sidebar brand ── */
.sidebar-brand {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: {T['title_color']};
    letter-spacing: 0.3px;
    margin-bottom: 4px;
    line-height: 1.2;
}}

.sidebar-brand span {{ color: {T['accent']}; }}

.sidebar-version {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: {T['section_color']};
    letter-spacing: 0.12em;
    margin-bottom: 28px;
    opacity: 0.6;
    line-height: 1.5;
}}

.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: {T['status_bg']};
    border: 1px solid {T['status_border']};
    border-radius: 3px;
    padding: 6px 12px;
    font-family: 'Barlow', sans-serif;
    font-size: 11px;
    font-weight: 700;
    color: #4ade80;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 12px;
}}

/* ── Mapa ── */
[data-testid="stIFrame"] {{
    display: block !important;
    margin: 0 !important;
    padding: 0 !important;
}}

.map-wrapper {{
    border: 1px solid {T['map_container_bd']};
    border-radius: 10px;
    overflow: hidden;
    background: {T['map_container_bg']};
    line-height: 0;
    font-size: 0;
}}

.map-wrapper > * {{ line-height: normal; font-size: initial; }}

.map-wrapper iframe {{
    display: block !important;
    margin: 0 !important;
    border: none !important;
}}

.element-container:has([data-testid="stIFrame"]) {{
    margin: 0 !important;
    padding: 0 !important;
}}

.map-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: {T['card_bg']};
    border-bottom: 1px solid {T['card_border']};
}}

.map-header-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: {T['title_color']};
    letter-spacing: 0.03em;
    text-transform: uppercase;
}}

.map-header-meta {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: {T['subtitle_color']};
    letter-spacing: 0.1em;
}}

.map-legend-dot {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'Barlow', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: {T['label_color']};
    letter-spacing: 0.04em;
}}

.dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}}

/* ── Utilitários ── */
#MainMenu, footer {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}

.stApp > div {{ padding-top: 0 !important; }}
[data-testid="stAppViewContainer"] {{ padding-top: 0 !important; }}
[data-testid="stAppViewContainer"] > section {{ padding-top: 0 !important; }}
[data-testid="stMain"] {{ padding-top: 0 !important; }}
[data-testid="stMainBlockContainer"] {{ padding-top: 0.5rem !important; }}
[data-testid="block-container"] {{ padding-top: 0.5rem !important; }}
.main .block-container {{ padding-top: 0.5rem !important; }}
</style>
"""