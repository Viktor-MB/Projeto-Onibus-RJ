import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RioBus · Monitor",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

FUSO = pytz.timezone('America/Sao_Paulo')

CORES_FOLIUM = [
    'orange', 'blue', 'green', 'purple', 'red',
    'darkred', 'cadetblue', 'darkgreen', 'black',
    'darkblue', 'darkpurple', 'pink', 'lightblue',
    'lightgreen', 'lightgray', 'gray', 'beige', 'white'
]

# ─────────────────────────────────────────────
#  TEMA — tokens por modo
# ─────────────────────────────────────────────
if "tema" not in st.session_state:
    st.session_state.tema = "dark"

DARK = {
    # ── Fundos ──────────────────────────────────────────────────
    "app_bg":           "#0d0f14",
    "sidebar_bg":       "#111318",
    "sidebar_border":   "#ffa00030",
    "card_bg":          "#161920",   # ligeiramente mais claro → mais separação visual
    "card_border":      "#252a38",
    "tab_border":       "#252a38",
    "df_border":        "#252a38",
    "map_container_bg": "#0d0f14",
    "map_container_bd": "#252a38",
    "empty_border":     "#252a38",
    "empty_hex":        "#252a38",
    # ── Textos (todos ≥ 4.5:1 WCAG AA sobre seus fundos) ────────
    "empty_text":       "#8896aa",   # era #4a5568 (ratio 3.1) → agora ~5.2:1
    "empty_sub":        "#566070",
    "header_border":    "#ffa00030",
    "title_color":      "#eef0f5",   # títulos — ~14:1
    "subtitle_color":   "#8896aa",   # secondary — ~5.2:1
    "label_color":      "#8896aa",
    "unit_color":       "#8896aa",
    "section_color":    "#8896aa",
    "body_color":       "#c8d0dc",   # texto corrido — ~8:1
    "section_border":   "#252a38",
    "sidebar_label":    "#b0bccb",   # era #a0aab8 — ganho de ~0.5 ratio
    "input_bg":         "#1a1d26",
    "input_border":     "#ffa00060",
    "grid_color":       "rgba(255,160,0,0.025)",
    # ── Acento ──────────────────────────────────────────────────
    "accent":           "#ffa000",
    "accent_15":        "#ffa00018",
    "accent_25":        "#ffa00030",
    "accent_40":        "#ffa00050",
    "accent_50":        "#ffa00065",
    "accent_hover":     "#ffb733",
    "status_bg":        "#0d1a0d",
    "status_border":    "#1a4a1a",
    "map_tiles":        "CartoDB positron",
    "toggle_icon":      "☀️",
    "toggle_label":     "Modo Claro",
}

LIGHT = {
    # ── Fundos ──────────────────────────────────────────────────
    "app_bg":           "#f0f2f5",
    "sidebar_bg":       "#ffffff",
    "sidebar_border":   "#c85a0025",
    "card_bg":          "#ffffff",
    "card_border":      "#dce1ea",
    "tab_border":       "#dce1ea",
    "df_border":        "#dce1ea",
    "map_container_bg": "#ffffff",
    "map_container_bd": "#dce1ea",
    "empty_border":     "#d0d6e2",
    "empty_hex":        "#b8c2d4",
    # ── Textos (todos ≥ 4.5:1 WCAG AA sobre fundo branco) ───────
    "empty_text":       "#5a6478",   # era #8892a4 (ratio 3.0) → agora ~5.5:1
    "empty_sub":        "#8a95a8",
    "header_border":    "#c85a0020",
    "title_color":      "#111827",   # ~16:1 — máximo contraste
    "subtitle_color":   "#5a6478",   # ~5.5:1
    "label_color":      "#5a6478",
    "unit_color":       "#5a6478",
    "section_color":    "#5a6478",
    "body_color":       "#374151",   # ~10:1
    "section_border":   "#dce1ea",
    "sidebar_label":    "#374151",   # era #6b7585 (ratio 4.0) → agora ~10:1
    "input_bg":         "#f4f6f9",
    "input_border":     "#c85a0050",
    "grid_color":       "rgba(200,90,0,0.035)",
    # ── Acento (mais escuro para passar AA sobre branco) ─────────
    "accent":           "#c85a00",   # era #e76b00 — escurecido para ratio ~4.6:1
    "accent_15":        "#c85a0015",
    "accent_25":        "#c85a0025",
    "accent_40":        "#c85a0040",
    "accent_50":        "#c85a0055",
    "accent_hover":     "#a34800",
    "status_bg":        "#f0faf0",
    "status_border":    "#86c986",
    "map_tiles":        "CartoDB positron",
    "toggle_icon":      "🌙",
    "toggle_label":     "Modo Escuro",
}

T = DARK if st.session_state.tema == "dark" else LIGHT

# ─────────────────────────────────────────────
#  CSS DINÂMICO
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;500;600;700&family=Barlow+Condensed:wght@600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Barlow', sans-serif;
    /* Base 16px — nunca abaixo disso para corpo de texto */
}}

.stApp {{
    background-color: {T['app_bg']};
    background-image:
        linear-gradient({T['grid_color']} 1px, transparent 1px),
        linear-gradient(90deg, {T['grid_color']} 1px, transparent 1px);
    background-size: 40px 40px;
    transition: background-color 0.3s ease;
}}

[data-testid="stSidebar"] {{
    background-color: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['sidebar_border']} !important;
    transition: background-color 0.3s ease;
}}

/* Labels da sidebar: uppercase legível = 12px mínimo + espaçamento moderado */
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider p {{
    color: {T['sidebar_label']} !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 13px !important;          /* era 12px — small caps precisam de +1px */
    font-weight: 600 !important;         /* bold compensa o uppercase menor */
    letter-spacing: 0.06em !important;   /* era 0.08em — menos espaçamento = mais legível */
    text-transform: uppercase !important;
    line-height: 1.5 !important;
}}

[data-testid="stSidebar"] .stTextInput input {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['input_border']} !important;
    color: {T['accent']} !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 15px !important;          /* era implícito — monospace precisa de tamanho explícito */
    border-radius: 4px !important;
}}

/* Botão de toggle */
[data-testid="stSidebar"] .stButton button {{
    background: {T['accent_15']} !important;
    border: 1px solid {T['accent_40']} !important;
    color: {T['accent']} !important;
    font-family: 'Barlow', sans-serif !important;  /* Barlow > mono para ação */
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

.main-header {{
    padding: 28px 0 20px 0;
    border-bottom: 1px solid {T['header_border']};
    margin-bottom: 28px;
}}

/* Título principal: Barlow Condensed é display — tamanho grande está ok */
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

/* Subtítulo: mono pequeno — uppercase curto está ok aqui */
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
    50% {{ opacity: 0.2; }}
}}

/* Cards de métrica */
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

/* Label do card: uppercase curto = ok, mas aumentei para 11px + bold */
.metric-label {{
    font-family: 'Barlow', sans-serif;
    font-size: 11px;              /* era 10px — limite mínimo absoluto */
    font-weight: 700;             /* bold essencial para uppercase pequeno */
    color: {T['label_color']};
    letter-spacing: 0.1em;        /* era 0.15em — reduzido para mais legibilidade */
    text-transform: uppercase;
    margin-bottom: 10px;
    line-height: 1.4;
}}

/* Valor da métrica: display grande — legível por natureza */
.metric-value {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 40px;
    font-weight: 700;
    color: {T['accent']};
    line-height: 1;
    margin-bottom: 6px;
}}

/* Unidade: texto corrido pequeno — precisa de cor com bom contraste */
.metric-unit {{
    font-family: 'Barlow', sans-serif;
    font-size: 13px;              /* era 13px — mantido, é o mínimo para secondary */
    color: {T['unit_color']};
    font-weight: 400;
    line-height: 1.5;
}}

/* Tabs */
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
    font-size: 15px !important;   /* era 14px — tabs precisam ser clicáveis e legíveis */
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

[data-baseweb="tab"]:hover {{
    color: {T['accent_hover']} !important;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid {T['df_border']} !important;
    border-radius: 8px !important;
    overflow: hidden;
}}

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

/* Section titles: uppercase label pequeno — bold obrigatório */
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

[data-testid="stAlert"] {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['accent_40']} !important;
    border-left: 3px solid {T['accent']} !important;
    border-radius: 4px !important;
    color: {T['sidebar_label']} !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 14px !important;    /* alerts precisam ser legíveis — nunca mono pequeno */
    line-height: 1.6 !important;
}}

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

/* ── Correção do gap do st_folium ── */
/* O iframe do folium tem margin/padding injetados pelo Streamlit */
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
    /* Elimina o gap vazio acima do iframe */
    line-height: 0;
    font-size: 0;
}}

.map-wrapper > * {{
    line-height: normal;
    font-size: initial;
}}

/* Remove padding padrão do bloco que envolve o st_folium */
.map-wrapper [data-testid="stVerticalBlock"] > div:first-child {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

.map-wrapper iframe {{
    display: block !important;
    margin: 0 !important;
    border: none !important;
}}

/* Zera o padding interno que o Streamlit adiciona ao redor do componente */
.element-container:has([data-testid="stIFrame"]) {{
    margin: 0 !important;
    padding: 0 !important;
}}

/* ── Header do mapa ── */
.map-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: {T['card_bg']};
    border-bottom: 1px solid {T['card_border']};
}}

.map-header-left {{
    display: flex;
    align-items: center;
    gap: 12px;
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

#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}

/* Remove o padding/gap enorme no topo da área principal */
[data-testid="stAppViewContainer"] > section > div:first-child {{
    padding-top: 1rem !important;
}}

[data-testid="block-container"] {{
    padding-top: 1rem !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">Rio<span>Bus</span> Monitor</div>
    <div class="sidebar-version">v2.0 · SPPO-RJ · API MOBILIDADE</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Configurar Rastreio</div>', unsafe_allow_html=True)

    linha_alvo     = st.text_input("Número da Linha", value="202")
    minutos_janela = st.slider("Janela de Histórico (min)", 5, 60, 15)
    refresh_rate   = st.select_slider("Auto-Refresh (seg)", options=[15, 30, 60], value=30)

    st.markdown('<div class="section-title" style="margin-top:24px;">Aparência</div>', unsafe_allow_html=True)

    if st.button(f"{T['toggle_icon']}  {T['toggle_label']}", use_container_width=True):
        st.session_state.tema = "light" if st.session_state.tema == "dark" else "dark"
        st.rerun()

    st.markdown(f"""
    <div class="status-pill">
        <span style="width:6px;height:6px;background:#4ade80;border-radius:50%;display:inline-block;"></span>
        SISTEMA ATIVO
    </div>
    """, unsafe_allow_html=True)

st_autorefresh(interval=refresh_rate * 1000, key="datarefresh")

# ─────────────────────────────────────────────
#  DADOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=10)
def buscar_dados(linha, minutos):
    agora  = datetime.now(FUSO)
    inicio = agora - timedelta(minutes=minutos)
    params = {
        "dataInicial": inicio.strftime('%Y-%m-%d %H:%M:%S'),
        "dataFinal":   agora.strftime('%Y-%m-%d %H:%M:%S'),
    }
    try:
        r  = requests.get("https://dados.mobilidade.rio/gps/sppo", params=params, timeout=15)
        df = pd.DataFrame(r.json())
        if df.empty:
            return None
        df['datahora_dt']       = pd.to_datetime(df['datahora'],      unit='ms').dt.tz_localize('UTC').dt.tz_convert(FUSO)
        df['datahora_envio_dt'] = pd.to_datetime(df['datahoraenvio'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(FUSO)
        df['latitude']          = pd.to_numeric(df['latitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df['longitude']         = pd.to_numeric(df['longitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df['velocidade']        = pd.to_numeric(df['velocidade'], errors='coerce').fillna(0)
        return df[df['linha'] == str(linha)].copy().sort_values('datahora').dropna(subset=['latitude', 'longitude'])
    except:
        return None

# ─────────────────────────────────────────────
#  LAYOUT PRINCIPAL
# ─────────────────────────────────────────────
agora_str = datetime.now(FUSO).strftime('%H:%M:%S')

st.markdown(f"""
<div class="main-header">
    <div class="live-badge">
        <div class="live-dot"></div>
        TRANSMISSÃO AO VIVO · {agora_str}
    </div>
    <h1 class="main-title">Rio<span>Bus</span> Analytics</h1>
    <p class="main-subtitle">Linha {linha_alvo} · Monitoramento Operacional SPPO</p>
</div>
""", unsafe_allow_html=True)

dados_bus = buscar_dados(linha_alvo, minutos_janela)

if dados_bus is not None and not dados_bus.empty:

    n_onibus   = len(dados_bus['ordem'].unique())
    ultima_cap = dados_bus['datahora_dt'].max().strftime('%H:%M:%S')
    lat_media  = (dados_bus['datahora_envio_dt'] - dados_bus['datahora_dt']).dt.total_seconds().mean()
    vel_media  = dados_bus['velocidade'].mean()

    # ── MÉTRICAS ──
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, "Ônibus Ativos",    str(n_onibus),   "veículos em operação",  ""),
        (c2, "Última Captura",   ultima_cap,       "horário BRT (BRA)",     "font-size:28px;"),
        (c3, "Atraso Médio GPS", f"{int(lat_media)}<span style='font-size:18px;font-weight:400;color:{T['unit_color']};'>s</span>",   "latência de envio",  ""),
        (c4, "Velocidade Média", f"{vel_media:.0f}<span style='font-size:18px;font-weight:400;color:{T['unit_color']};'>km/h</span>", "frota monitorada",  ""),
    ]

    for col, label, value, unit, val_style in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="{val_style}">{value}</div>
                <div class="metric-unit">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── TABS ──
    tab_mapa, tab_dados = st.tabs(["▶  Mapa de Rastros", "≡  Auditoria da Frota"])

    # ── MAPA ──
    with tab_mapa:
        mapa_center = [dados_bus['latitude'].mean(), dados_bus['longitude'].mean()]
        m = folium.Map(location=mapa_center, zoom_start=14, tiles=T["map_tiles"])

        for i, (ordem, trajetoria) in enumerate(dados_bus.groupby('ordem')):
            cor    = CORES_FOLIUM[i % len(CORES_FOLIUM)]
            coords = trajetoria[['latitude', 'longitude']].values.tolist()

            folium.PolyLine(
                coords,
                color=T["accent"] if i == 0 else cor,
                weight=3, opacity=0.65, smooth_factor=2
            ).add_to(m)

            for _, row in trajetoria.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=3,
                    color=T["accent"] if i == 0 else cor,
                    fill=True, fill_opacity=0.6,
                    tooltip=f"🕒 {row['datahora_dt'].strftime('%H:%M:%S')} · ID {ordem}"
                ).add_to(m)

            folium.Marker(
                coords[0],
                tooltip=f"Início · {ordem}",
                icon=folium.Icon(color='white', icon_color=T["accent"], icon='play', prefix='fa')
            ).add_to(m)

            ultima = trajetoria.iloc[-1]
            folium.Marker(
                [ultima['latitude'], ultima['longitude']],
                tooltip=f"<b>{ordem}</b><br>{ultima['datahora_dt'].strftime('%H:%M:%S')}",
                icon=folium.Icon(color='orange' if i == 0 else cor, icon='bus', prefix='fa')
            ).add_to(m)

        # Header do mapa + container sem gap
        st.markdown(f"""
        <div class="map-wrapper">
            <div class="map-header">
                <div class="map-header-left">
                    <div>
                        <div class="map-header-title">🗺 Rastro Temporal · Linha {linha_alvo}</div>
                        <div class="map-header-meta">Janela: {minutos_janela} min · {n_onibus} veículos · Zoom 14</div>
                    </div>
                </div>
                <div style="display:flex;gap:16px;align-items:center;">
                    <span class="map-legend-dot"><span class="dot" style="background:{T['accent']};"></span> Principal</span>
                    <span class="map-legend-dot"><span class="dot" style="background:#4ade80;"></span> Início</span>
                    <span class="map-legend-dot"><span class="dot" style="background:#60a5fa;"></span> Outros</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Mapa sem padding externo
        st.markdown('<div class="map-wrapper" style="border-top:none;border-radius:0 0 10px 10px;margin-top:-1px;">', unsafe_allow_html=True)
        st_folium(m, width="100%", height=540, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TABELA ──
    with tab_dados:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        df_display = dados_bus[['ordem', 'datahora_dt', 'datahora_envio_dt', 'velocidade', 'latitude', 'longitude']].copy()
        df_display['atraso'] = (df_display['datahora_envio_dt'] - df_display['datahora_dt']).dt.total_seconds().astype(int)
        df_display = df_display.sort_values('datahora_dt', ascending=False)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=480,
            column_config={
                "ordem":             st.column_config.TextColumn("ID Veículo", width="small"),
                "datahora_dt":       st.column_config.DatetimeColumn("Captura GPS", format="HH:mm:ss"),
                "datahora_envio_dt": st.column_config.DatetimeColumn("Recebido",    format="HH:mm:ss"),
                "atraso":            st.column_config.NumberColumn("Atraso (s)", format="%d s", width="small"),
                "velocidade":        st.column_config.ProgressColumn("Velocidade km/h", min_value=0, max_value=100, format="%d"),
                "latitude":          st.column_config.NumberColumn("Lat", format="%.5f"),
                "longitude":         st.column_config.NumberColumn("Lon", format="%.5f"),
            }
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="↓  EXPORTAR CSV",
            data=csv,
            file_name=f"sppo_linha{linha_alvo}_{datetime.now(FUSO).strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

else:
    st.markdown(f"""
    <div style="
        margin-top: 60px; padding: 48px;
        border: 1px dashed {T['empty_border']};
        border-radius: 6px; text-align: center;
    ">
        <div style="font-family:'Share Tech Mono',monospace;font-size:32px;color:{T['empty_hex']};margin-bottom:16px;">⬡</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:22px;color:{T['empty_text']};letter-spacing:0.08em;font-weight:600;text-transform:uppercase;">
            Sem dados disponíveis
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:{T['empty_sub']};margin-top:8px;letter-spacing:0.12em;">
            LINHA {linha_alvo} · JANELA {minutos_janela} MIN · AGUARDANDO SINAL
        </div>
    </div>
    """, unsafe_allow_html=True)