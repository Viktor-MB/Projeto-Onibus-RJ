import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh
import sys, os

# Configuração de caminhos para estilos
sys.path.insert(0, os.path.dirname(__file__))
from styles import get_theme, inject_css

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RioBus Monitoramento",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

FUSO = pytz.timezone('America/Sao_Paulo')

# Lista de cores padrão do Folium (Icon não aceita Hexadecimal para o fundo do pin)
CORES_FOLIUM = [
    'red', 'blue', 'green', 'purple', 'orange', 'darkred', 
    'lightred', 'darkblue', 'darkgreen', 'cadetblue', 
    'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black'
]

# ─────────────────────────────────────────────
#  TEMA
# ─────────────────────────────────────────────
if "tema" not in st.session_state:
    st.session_state.tema = "dark"

T = get_theme(st.session_state)
st.markdown(inject_css(T), unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FUNÇÕES DE ENGENHARIA DE DADOS
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def buscar_todas_as_linhas():
    """Busca todas as linhas operantes nos últimos 15 min para o seletor."""
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
        # Ordenação numérica inteligente
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
    params = {"dataInicial": inicio.strftime('%Y-%m-%d %H:%M:%S'), "dataFinal": agora.strftime('%Y-%m-%d %H:%M:%S')}
    try:
        r  = requests.get("https://dados.mobilidade.rio/gps/sppo", params=params, timeout=15)
        df = pd.DataFrame(r.json())
        if df.empty: return None
        df['datahora_dt']       = pd.to_datetime(df['datahora'],      unit='ms').dt.tz_localize('UTC').dt.tz_convert(FUSO)
        df['datahora_envio_dt'] = pd.to_datetime(df['datahoraenvio'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(FUSO)
        df['latitude']          = pd.to_numeric(df['latitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df['longitude']         = pd.to_numeric(df['longitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df['velocidade']        = pd.to_numeric(df['velocidade'], errors='coerce').fillna(0)
        return df[df['linha'] == str(linha)].copy().sort_values('datahora').dropna(subset=['latitude', 'longitude'])
    except: return None

@st.cache_data(ttl=30)
def buscar_ordens(linha):
    """Busca todas as ordens ativas de uma linha nos últimos 30 min."""
    if not linha or "Selecione" in str(linha): return None
    agora  = datetime.now(FUSO)
    inicio = agora - timedelta(minutes=30)
    params = {"dataInicial": inicio.strftime('%Y-%m-%d %H:%M:%S'), "dataFinal": agora.strftime('%Y-%m-%d %H:%M:%S')}
    try:
        r  = requests.get("https://dados.mobilidade.rio/gps/sppo", params=params, timeout=15)
        df = pd.DataFrame(r.json())
        if df.empty: return None
        df['datahora_dt'] = pd.to_datetime(df['datahora'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(FUSO)
        df['velocidade']  = pd.to_numeric(df['velocidade'], errors='coerce').fillna(0)
        df_linha = df[df['linha'] == str(linha)].copy()
        if df_linha.empty: return None
        return df_linha.sort_values('datahora_dt', ascending=False).drop_duplicates(subset='ordem').reset_index(drop=True)
    except: return None

@st.cache_data(ttl=15)
def listar_ordens_sidebar(linha, minutos):
    """Popula o filtro de IDs na barra lateral."""
    if not linha or "Selecione" in str(linha): return []
    dados = buscar_dados(linha, minutos)
    if dados is None or dados.empty: return []
    return sorted(dados['ordem'].unique().tolist())

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Rio<span>Bus</span> Monitoramento</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Configurar Rastreio</div>', unsafe_allow_html=True)

    linhas_ativas = buscar_todas_as_linhas()
    opcoes_dropdown = ["🔍 Selecione uma linha..."] + linhas_ativas

    linha_alvo = st.selectbox("Selecione ou Digite a Linha", options=opcoes_dropdown, index=0)
    minutos_janela = st.slider("Janela de Histórico (min)", 5, 60, 15)
    refresh_rate   = st.select_slider("Atualização (seg)", options=[15, 30, 60], value=30)

    st.markdown('<div class="section-title" style="margin-top:20px;">Filtrar Veículo</div>', unsafe_allow_html=True)

    if linha_alvo != "🔍 Selecione uma linha...":
        ordens_sidebar = listar_ordens_sidebar(linha_alvo, minutos_janela)
        if ordens_sidebar:
            ordens_selecionadas = st.multiselect("Ordens", options=ordens_sidebar, default=[], placeholder="Todos os veículos", label_visibility="collapsed")
            filtro_ordens = ordens_selecionadas
            st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace; font-size:10px; color:{T["subtitle_color"]}; margin-top:-8px;">{len(ordens_sidebar)} VEÍCULOS ATIVOS</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:10px; opacity:0.6;">BUSCANDO TRANSMISSÃO...</div>', unsafe_allow_html=True)
            filtro_ordens = []
    else:
        st.caption("Escolha uma linha para filtrar veículos.")
        filtro_ordens = []

    st.markdown('<div class="section-title" style="margin-top:24px;">Aparência</div>', unsafe_allow_html=True)
    if st.button(f"{T['toggle_icon']}  {T['toggle_label']}", use_container_width=True):
        st.session_state.tema = "light" if st.session_state.tema == "dark" else "dark"
        st.rerun()

st_autorefresh(interval=refresh_rate * 1000, key="datarefresh")

# ─────────────────────────────────────────────
#  LOGICA DE BLOQUEIO / TELA INICIAL
# ─────────────────────────────────────────────
if linha_alvo == "🔍 Selecione uma linha...":
    st.markdown(f"""
    <div style="margin-top:100px; padding:60px; text-align:center; border:1px dashed {T['empty_border']}; border-radius:12px; background:{T['card_bg']}30;">
        <div style="font-family:'Share Tech Mono',monospace; font-size:50px; color:{T['accent']}; margin-bottom:20px;">⚡</div>
        <h2 style="font-family:'Barlow Condensed',sans-serif; color:{T['title_color']}; text-transform:uppercase; letter-spacing:0.05em;">
            Pronto para monitorar
        </h2>
        <p style="font-family:'Barlow',sans-serif; color:{T['subtitle_color']}; font-size:16px;">
            Utilize o seletor na <b>barra lateral esquerda</b> para escolher uma linha ativa no Rio de Janeiro.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
#  HEADER E DADOS PRINCIPAIS
# ─────────────────────────────────────────────
agora_str = datetime.now(FUSO).strftime('%H:%M:%S')
st.markdown(f"""
<div class="main-header">
    <div class="live-badge"><div class="live-dot"></div> TRANSMISSÃO AO VIVO · {agora_str}</div>
    <h1 class="main-title">Rio<span>Bus</span> Monitoramento</h1>
    <p class="main-subtitle">Linha {linha_alvo} · Operação em Tempo Real SPPO</p>
</div>
""", unsafe_allow_html=True)

dados_full = buscar_dados(linha_alvo, minutos_janela)

if dados_full is not None and not dados_full.empty:
    dados_bus = dados_full[dados_full['ordem'].isin(filtro_ordens)].copy() if filtro_ordens else dados_full.copy()
    
    n_onibus = len(dados_bus['ordem'].unique())
    lat_media = (dados_bus['datahora_envio_dt'] - dados_bus['datahora_dt']).dt.total_seconds().mean()
    vel_media = dados_bus['velocidade'].mean()

    # Métricas principais
    c1, c2, c3 = st.columns(3)
    metrics = [(c1, "Veículos Ativos", str(n_onibus)), (c2, "Latência GPS", f"{int(lat_media)}s"), (c3, "Velocidade Média", f"{vel_media:.0f} km/h")]
    for col, label, value in metrics:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

    tab_mapa, tab_dados, tab_ordens = st.tabs(["▶ Mapa de Rastros", "≡ Auditoria", "🔍 Buscar Ordens"])

    # ── ABA 1: MAPA (FUNCIONALIDADE DE CORES E MARKERS) ──
    with tab_mapa:
        m = folium.Map(location=[dados_bus['latitude'].mean(), dados_bus['longitude'].mean()], zoom_start=14, tiles=T["map_tiles"])
        
        for i, (ordem, trajetoria) in enumerate(dados_bus.groupby('ordem')):
            cor = CORES_FOLIUM[i % len(CORES_FOLIUM)]
            coords = trajetoria[['latitude', 'longitude']].values.tolist()

            # Rastro
            folium.PolyLine(coords, color=cor, weight=3, opacity=0.8).add_to(m)

            # Pontos do rastro
            for _, row in trajetoria.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']], radius=2.5,
                    color=cor, fill=True, tooltip=f"🕒 {row['datahora_dt'].strftime('%H:%M:%S')}"
                ).add_to(m)

            # Marcador de INÍCIO (Sincronizado)
            folium.Marker(
                coords[0], 
                icon=folium.Icon(color='white', icon_color=cor, icon='play', prefix='fa'),
                tooltip=f"Início do Rastro (ID: {ordem})"
            ).add_to(m)

            # Marcador de POSIÇÃO ATUAL (Sincronizado)
            ultima = trajetoria.iloc[-1]
            folium.Marker(
                [ultima['latitude'], ultima['longitude']],
                icon=folium.Icon(color=cor, icon='bus', prefix='fa'),
                tooltip=f"<b>Atual: {ordem}</b>"
            ).add_to(m)

        st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
        st_folium(m, width="100%", height=540, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_dados:
        st.dataframe(dados_bus.sort_values('datahora_dt', ascending=False), use_container_width=True, hide_index=True)

    with tab_ordens:
        linha_busca = st.text_input("Consulta Instantânea de Linha", placeholder="Digite uma linha...")
        if st.button("Buscar"):
            df_res = buscar_ordens(linha_busca)
            if df_res is not None: st.table(df_res)
            else: st.error("Nenhum dado encontrado.")

else:
    st.markdown(f'<div style="text-align:center; padding:40px; border:1px dashed {T["empty_border"]};">Sem sinal de GPS para a linha {linha_alvo} no momento.</div>', unsafe_allow_html=True)