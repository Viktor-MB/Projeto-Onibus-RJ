import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh
import sys, os

# Ajuste de caminhos para estilos locais
sys.path.insert(0, os.path.dirname(__file__))
from styles import get_theme, inject_css

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
#  TEMA
# ─────────────────────────────────────────────
if "tema" not in st.session_state:
    st.session_state.tema = "dark"

T = get_theme(st.session_state)
st.markdown(inject_css(T), unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FUNÇÕES DE DADOS
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def buscar_todas_as_linhas():
    """Busca todas as linhas ativas nos últimos 15 min para o seletor."""
    agora = datetime.now(FUSO)
    inicio = agora - timedelta(minutes=15)
    params = {
        "dataInicial": inicio.strftime('%Y-%m-%d %H:%M:%S'),
        "dataFinal": agora.strftime('%Y-%m-%d %H:%M:%S')
    }
    try:
        r = requests.get("https://dados.mobilidade.rio/gps/sppo", params=params, timeout=15)
        df = pd.DataFrame(r.json())
        if df.empty: return []
        # Ordenação numérica inteligente (converte para int se possível)
        linhas = sorted(df['linha'].unique().tolist(), key=lambda x: int(x) if str(x).isdigit() else 999)
        return [str(l) for l in linhas]
    except:
        return []

@st.cache_data(ttl=10)
def buscar_dados(linha, minutos):
    """Busca rastro histórico de uma linha na janela de tempo definida."""
    if not linha or "Selecione" in str(linha): return None
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

@st.cache_data(ttl=30)
def buscar_ordens(linha):
    """Busca todas as ordens ativas de uma linha nos últimos 30 min."""
    if not linha or "Selecione" in str(linha): return None
    agora  = datetime.now(FUSO)
    inicio = agora - timedelta(minutes=30)
    params = {
        "dataInicial": inicio.strftime('%Y-%m-%d %H:%M:%S'),
        "dataFinal":   agora.strftime('%Y-%m-%d %H:%M:%S'),
    }
    try:
        r  = requests.get("https://dados.mobilidade.rio/gps/sppo", params=params, timeout=15)
        df = pd.DataFrame(r.json())
        if df.empty:
            return None
        df['datahora_dt'] = pd.to_datetime(df['datahora'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(FUSO)
        df['velocidade']  = pd.to_numeric(df['velocidade'], errors='coerce').fillna(0)
        df_linha = df[df['linha'] == str(linha)].copy()
        if df_linha.empty:
            return None
        return (
            df_linha.sort_values('datahora_dt', ascending=False)
            .drop_duplicates(subset='ordem')
            [['ordem', 'datahora_dt', 'velocidade', 'linha']]
            .reset_index(drop=True)
        )
    except:
        return None

@st.cache_data(ttl=15)
def listar_ordens_sidebar(linha, minutos):
    """Retorna lista de ordens únicas da linha para o selectbox da sidebar."""
    if not linha or "Selecione" in str(linha): return []
    dados = buscar_dados(linha, minutos)
    if dados is None or dados.empty:
        return []
    return sorted(dados['ordem'].unique().tolist())


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">Rio<span>Bus</span> Monitor</div>
    <div class="sidebar-version">v2.0 · SPPO-RJ · API MOBILIDADE</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Configurar Rastreio</div>', unsafe_allow_html=True)

    # 🛠️ FUNCIONALIDADE: DROPDOWN COM OPÇÃO INICIAL VAZIA
    lista_linhas = buscar_todas_as_linhas()
    opcoes_dropdown = ["🔍 Selecione uma linha..."] + lista_linhas

    linha_alvo = st.selectbox(
        "Selecione ou Digite a Linha",
        options=opcoes_dropdown,
        index=0,
        help="As linhas são carregadas em tempo real conforme a operação ativa."
    )

    minutos_janela = st.slider("Janela de Histórico (min)", 5, 60, 15)
    refresh_rate   = st.select_slider("Auto-Refresh (seg)", options=[15, 30, 60], value=30)

    st.markdown('<div class="section-title" style="margin-top:20px;">Filtrar Veículo</div>', unsafe_allow_html=True)

    # Só tenta listar ordens se uma linha válida for escolhida
    if linha_alvo != "🔍 Selecione uma linha...":
        ordens_sidebar = listar_ordens_sidebar(linha_alvo, minutos_janela)
        if ordens_sidebar:
            ordens_selecionadas = st.multiselect(
                "Ordens",
                options=ordens_sidebar,
                default=[],
                placeholder="Todos os veículos",
                label_visibility="collapsed",
            )
            filtro_ordens = ordens_selecionadas  
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;'
                f'color:{T["subtitle_color"]};letter-spacing:0.08em;margin-top:-8px;">'
                f'{len(ordens_sidebar)} ORDEM(S) ATIVAS</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;'
                f'color:{T["subtitle_color"]};letter-spacing:0.08em;">SEM DADOS AINDA</div>',
                unsafe_allow_html=True
            )
            filtro_ordens = []
    else:
        st.info("Escolha uma linha acima.")
        filtro_ordens = []

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
#  LOGICA DE BLOQUEIO / ESTADO INICIAL
# ─────────────────────────────────────────────
if linha_alvo == "🔍 Selecione uma linha...":
    st.markdown(f"""
    <div style="margin-top:100px; padding:60px; text-align:center; border:1px dashed {T['empty_border']}; border-radius:12px; background:{T['card_bg']}30;">
        <div style="font-family:'Share Tech Mono',monospace; font-size:50px; color:{T['accent']}; margin-bottom:20px;">⚡</div>
        <h2 style="font-family:'Barlow Condensed',sans-serif; color:{T['title_color']}; text-transform:uppercase; letter-spacing:0.05em;">
            Pronto para monitorar
        </h2>
        <p style="font-family:'Barlow',sans-serif; color:{T['subtitle_color']}; font-size:16px;">
            Utilize o seletor na <b>barra lateral esquerda</b> para escolher uma linha ativa no sistema SPPO-RJ.
        </p>
        <div style="font-family:'Share Tech Mono',monospace; font-size:10px; color:{T['accent']}; margin-top:30px; letter-spacing:0.2em; opacity:0.6;">
            SISTEMA AGUARDANDO COMANDO · RIOBUS v2.0
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop() # Interrompe a execução aqui

# ─────────────────────────────────────────────
#  PROCESSAMENTO DE DADOS (Só roda se linha for selecionada)
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

dados_bus_full = buscar_dados(linha_alvo, minutos_janela)

if dados_bus_full is not None and not dados_bus_full.empty:

    if filtro_ordens:
        dados_filtrados = dados_bus_full[dados_bus_full['ordem'].isin(filtro_ordens)].copy()
    else:
        dados_filtrados = dados_bus_full.copy()

    filtro_ativo = len(filtro_ordens) > 0

    n_onibus  = len(dados_filtrados['ordem'].unique())
    lat_media = (dados_filtrados['datahora_envio_dt'] - dados_filtrados['datahora_dt']).dt.total_seconds().mean()
    vel_media = dados_filtrados['velocidade'].mean()

    # Badge de filtro
    if filtro_ativo:
        ordens_label = ", ".join(filtro_ordens)
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:8px;
                    background:{T['accent_15']};border:1px solid {T['accent_40']};
                    border-left:3px solid {T['accent']};border-radius:4px;
                    padding:6px 14px;margin-bottom:16px;
                    font-family:'Share Tech Mono',monospace;font-size:11px;color:{T['accent']};
                    letter-spacing:0.08em;">
            🎯 FILTRO ATIVO · {len(filtro_ordens)} ORDEM(S) SELECIONADA(S)
        </div>
        """, unsafe_allow_html=True)

    # Métricas
    c1, c2, c3 = st.columns(3)
    metrics = [
        (c1, "Ônibus Ativos",    str(n_onibus),   "veículos em operação"),
        (c2, "Atraso Médio GPS", f"{int(lat_media)}<span style='font-size:20px;font-weight:400;color:{T['unit_color']};'>s</span>",   "latência de envio"),
        (c3, "Velocidade Média", f"{vel_media:.0f}<span style='font-size:20px;font-weight:400;color:{T['unit_color']};'>km/h</span>", "frota monitorada"),
    ]

    for col, label, value, unit in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-unit">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    tab_mapa, tab_dados, tab_ordens = st.tabs([
        "▶  Mapa de Rastros",
        "≡  Auditoria da Frota",
        "🔍  Buscar Ordens",
    ])

    with tab_mapa:
        mapa_center = [dados_filtrados['latitude'].mean(), dados_filtrados['longitude'].mean()]
        m = folium.Map(location=mapa_center, zoom_start=14, tiles=T["map_tiles"])

        for i, (ordem, trajetoria) in enumerate(dados_filtrados.groupby('ordem')):
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

            ultima = trajetoria.iloc[-1]
            folium.Marker(
                [ultima['latitude'], ultima['longitude']],
                tooltip=f"<b>{ordem}</b><br>{ultima['datahora_dt'].strftime('%H:%M:%S')}",
                icon=folium.Icon(color='blue' if i == 0 else cor, icon='bus', prefix='fa')
            ).add_to(m)

        st.markdown(f"""
        <div class="map-wrapper">
            <div class="map-header">
                <div>
                    <div class="map-header-title">🗺 Rastro Temporal · Linha {linha_alvo}</div>
                    <div class="map-header-meta">Janela: {minutos_janela} min · {n_onibus} veículos</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="map-wrapper" style="border-top:none;border-radius:0 0 10px 10px;margin-top:-1px;">', unsafe_allow_html=True)
        st_folium(m, width="100%", height=540, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_dados:
        df_display = dados_filtrados.sort_values('datahora_dt', ascending=False)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    with tab_ordens:
        st.markdown(f'<div class="section-title">Busca de Ordens Ativas</div>', unsafe_allow_html=True)
        linha_busca = st.text_input("Digite uma linha para consulta instantânea", key="busca_ordem_input")
        if st.button("Buscar Frota"):
            df_ordens = buscar_ordens(linha_busca)
            if df_ordens is not None:
                st.table(df_ordens)
            else:
                st.error("Nenhum dado encontrado para esta linha.")

else:
    st.markdown(f"""
    <div style="margin-top:60px;padding:48px;text-align:center;
                border:1px dashed {T['empty_border']};border-radius:6px;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:32px;
                    color:{T['empty_hex']};margin-bottom:16px;">⬡</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:22px;
                    color:{T['empty_text']};letter-spacing:0.08em;font-weight:600;text-transform:uppercase;">
            Sem sinal de GPS no momento
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:11px;
                    color:{T['empty_sub']};margin-top:8px;letter-spacing:0.12em;">
            LINHA {linha_alvo} · JANELA {minutos_janela} MIN · AGUARDANDO TRANSMISSÃO
        </div>
    </div>
    """, unsafe_allow_html=True)