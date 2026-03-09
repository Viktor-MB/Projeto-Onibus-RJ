import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh
import sys, os
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
#  (definidas ANTES da sidebar para evitar NameError)
# ─────────────────────────────────────────────
@st.cache_data(ttl=10)
def buscar_dados(linha, minutos):
    """Busca rastro histórico de uma linha na janela de tempo definida."""
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

    linha_alvo     = st.text_input("Número da Linha", value="202")
    minutos_janela = st.slider("Janela de Histórico (min)", 5, 60, 15)
    refresh_rate   = st.select_slider("Auto-Refresh (seg)", options=[15, 30, 60], value=30)

    # ── Filtro de ordem — selectbox populado da API ──
    st.markdown('<div class="section-title" style="margin-top:20px;">Filtrar Veículo</div>', unsafe_allow_html=True)

    ordens_sidebar = listar_ordens_sidebar(linha_alvo, minutos_janela)

    if ordens_sidebar:
        ordens_selecionadas = st.multiselect(
            "Ordens",
            options=ordens_sidebar,
            default=[],
            placeholder="Todos os veículos",
            label_visibility="collapsed",
        )
        filtro_ordens = ordens_selecionadas  # lista vazia = todos
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
#  HEADER PRINCIPAL
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

# ─────────────────────────────────────────────
#  DADOS PRINCIPAIS
# ─────────────────────────────────────────────
dados_bus = buscar_dados(linha_alvo, minutos_janela)

if dados_bus is not None and not dados_bus.empty:

    # ── Aplica filtro de ordem ─────────────────
    if filtro_ordens:
        dados_filtrados = dados_bus[dados_bus['ordem'].isin(filtro_ordens)].copy()
    else:
        dados_filtrados = dados_bus.copy()

    filtro_ativo = len(filtro_ordens) > 0

    n_onibus  = len(dados_filtrados['ordem'].unique())
    lat_media = (dados_filtrados['datahora_envio_dt'] - dados_filtrados['datahora_dt']).dt.total_seconds().mean()
    vel_media = dados_filtrados['velocidade'].mean()

    # ── MÉTRICAS ──────────────────────────────
    if filtro_ativo:
        ordens_label = ", ".join(filtro_ordens)
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:8px;
                    background:{T['accent_15']};border:1px solid {T['accent_40']};
                    border-left:3px solid {T['accent']};border-radius:4px;
                    padding:6px 14px;margin-bottom:16px;
                    font-family:'Share Tech Mono',monospace;font-size:11px;color:{T['accent']};
                    letter-spacing:0.08em;">
            🎯 FILTRO ATIVO · {len(filtro_ordens)} ORDEM(S) · {ordens_label}
        </div>
        """, unsafe_allow_html=True)

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

    # ── TABS ──────────────────────────────────
    tab_mapa, tab_dados, tab_ordens = st.tabs([
        "▶  Mapa de Rastros",
        "≡  Auditoria da Frota",
        "🔍  Buscar Ordens",
    ])

    # ── TAB 1: MAPA ───────────────────────────
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

            folium.Marker(
                coords[0],
                tooltip=f"Início · {ordem}",
                icon=folium.Icon(color='white', icon_color=T["accent"], icon='play', prefix='fa')
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
                    <div class="map-header-meta">Janela: {minutos_janela} min · {n_onibus} veículos · Zoom 14</div>
                </div>
                <div style="display:flex;gap:16px;align-items:center;">
                    <span class="map-legend-dot"><span class="dot" style="background:{T['accent']};"></span> Principal</span>
                    <span class="map-legend-dot"><span class="dot" style="background:#4ade80;"></span> Início</span>
                    <span class="map-legend-dot"><span class="dot" style="background:#94a3b8;"></span> Outros</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="map-wrapper" style="border-top:none;border-radius:0 0 10px 10px;margin-top:-1px;">', unsafe_allow_html=True)
        st_folium(m, width="100%", height=540, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 2: AUDITORIA ──────────────────────
    with tab_dados:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        df_display = dados_filtrados[[
            'ordem', 'datahora_dt', 'datahora_envio_dt', 'velocidade', 'latitude', 'longitude'
        ]].copy()
        df_display['atraso'] = (
            df_display['datahora_envio_dt'] - df_display['datahora_dt']
        ).dt.total_seconds().astype(int)
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

    # ── TAB 3: BUSCAR ORDENS ──────────────────
    with tab_ordens:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-bottom:20px;">
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:20px;font-weight:700;
                        color:{T['title_color']};letter-spacing:0.02em;margin-bottom:4px;">
                Consulta de Frota por Linha
            </div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:11px;
                        color:{T['subtitle_color']};letter-spacing:0.1em;">
                PESQUISE QUALQUER LINHA SPPO · VEÍCULOS ATIVOS NOS ÚLTIMOS 30 MIN
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_input, col_btn = st.columns([3, 1])
        with col_input:
            linha_busca = st.text_input(
                "Linha",
                placeholder="Ex: 202, 474, 553...",
                label_visibility="collapsed",
                key="busca_ordem_input"
            )
        with col_btn:
            buscar = st.button("🔍  Buscar", use_container_width=True, key="btn_buscar_ordens")

        if buscar and linha_busca.strip():
            with st.spinner(f"Buscando veículos da linha {linha_busca.strip()}..."):
                df_ordens = buscar_ordens(linha_busca.strip())

            if df_ordens is not None and not df_ordens.empty:
                total = len(df_ordens)

                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;
                            background:{T['accent_15']};border:1px solid {T['accent_40']};
                            border-left:3px solid {T['accent']};
                            border-radius:6px;padding:14px 20px;margin:16px 0;">
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:36px;
                                font-weight:700;color:{T['accent']};line-height:1;">{total}</div>
                    <div>
                        <div style="font-family:'Barlow',sans-serif;font-size:14px;font-weight:600;
                                    color:{T['title_color']};">
                            veículos encontrados na linha {linha_busca.strip().upper()}
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;
                                    color:{T['subtitle_color']};letter-spacing:0.1em;margin-top:2px;">
                            ÚLTIMA ATUALIZAÇÃO · {datetime.now(FUSO).strftime('%H:%M:%S')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                ordens_lista = df_ordens['ordem'].tolist()
                for row_i in range(0, len(ordens_lista), 5):
                    cols = st.columns(5)
                    for col_i, ordem in enumerate(ordens_lista[row_i:row_i + 5]):
                        row_data     = df_ordens[df_ordens['ordem'] == ordem].iloc[0]
                        vel          = int(row_data['velocidade'])
                        horario      = row_data['datahora_dt'].strftime('%H:%M:%S')
                        cor_status   = "#4ade80" if vel > 0 else "#f87171"
                        label_status = "EM MOVIMENTO" if vel > 0 else "PARADO"
                        with cols[col_i]:
                            st.markdown(f"""
                            <div style="background:{T['card_bg']};border:1px solid {T['card_border']};
                                        border-top:2px solid {cor_status};border-radius:8px;
                                        padding:14px 16px;margin-bottom:8px;">
                                <div style="font-family:'Share Tech Mono',monospace;font-size:10px;
                                            color:{T['label_color']};letter-spacing:0.1em;margin-bottom:6px;">
                                    ORDEM
                                </div>
                                <div style="font-family:'Barlow Condensed',sans-serif;font-size:22px;
                                            font-weight:700;color:{T['accent']};line-height:1;margin-bottom:8px;">
                                    {ordem}
                                </div>
                                <div style="font-family:'Barlow',sans-serif;font-size:12px;
                                            color:{T['subtitle_color']};margin-bottom:4px;">
                                    🚀 {vel} km/h
                                </div>
                                <div style="font-family:'Share Tech Mono',monospace;font-size:10px;
                                            color:{cor_status};letter-spacing:0.06em;font-weight:700;">
                                    ● {label_status}
                                </div>
                                <div style="font-family:'Share Tech Mono',monospace;font-size:9px;
                                            color:{T['label_color']};margin-top:4px;opacity:0.7;">
                                    {horario}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.markdown(f'<div class="section-title">Lista Completa · {total} veículos</div>', unsafe_allow_html=True)

                df_ordens_display = df_ordens.rename(columns={
                    'ordem':       'ID Veículo',
                    'datahora_dt': 'Última Captura',
                    'velocidade':  'Velocidade (km/h)',
                    'linha':       'Linha',
                })
                st.dataframe(
                    df_ordens_display,
                    use_container_width=True,
                    hide_index=True,
                    height=min(400, 56 + total * 35),
                    column_config={
                        "ID Veículo":        st.column_config.TextColumn(width="small"),
                        "Última Captura":    st.column_config.DatetimeColumn(format="HH:mm:ss"),
                        "Velocidade (km/h)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
                        "Linha":             st.column_config.TextColumn(width="small"),
                    }
                )

                csv_ordens = df_ordens_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="↓  EXPORTAR ORDENS CSV",
                    data=csv_ordens,
                    file_name=f"ordens_linha{linha_busca.strip()}_{datetime.now(FUSO).strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    key="dl_ordens"
                )

            else:
                st.markdown(f"""
                <div style="margin-top:24px;padding:40px;text-align:center;
                            border:1px dashed {T['empty_border']};border-radius:8px;">
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:20px;
                                color:{T['empty_text']};font-weight:600;text-transform:uppercase;
                                letter-spacing:0.08em;">
                        Nenhum veículo encontrado
                    </div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:11px;
                                color:{T['empty_sub']};margin-top:8px;letter-spacing:0.1em;">
                        LINHA {linha_busca.strip().upper()} · SEM DADOS NOS ÚLTIMOS 30 MIN
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div style="margin-top:24px;padding:48px;text-align:center;
                        border:1px dashed {T['empty_border']};border-radius:8px;">
                <div style="font-family:'Share Tech Mono',monospace;font-size:28px;
                            color:{T['empty_hex']};margin-bottom:14px;">🔍</div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:20px;
                            color:{T['empty_text']};font-weight:600;text-transform:uppercase;
                            letter-spacing:0.08em;">
                    Digite uma linha e clique em Buscar
                </div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:11px;
                            color:{T['empty_sub']};margin-top:8px;letter-spacing:0.1em;">
                    CONSULTA INDEPENDENTE DO MONITORAMENTO PRINCIPAL
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ESTADO VAZIO (sem dados para a linha)
# ─────────────────────────────────────────────
else:
    st.markdown(f"""
    <div style="margin-top:60px;padding:48px;text-align:center;
                border:1px dashed {T['empty_border']};border-radius:6px;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:32px;
                    color:{T['empty_hex']};margin-bottom:16px;">⬡</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:22px;
                    color:{T['empty_text']};letter-spacing:0.08em;font-weight:600;text-transform:uppercase;">
            Sem dados disponíveis
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:11px;
                    color:{T['empty_sub']};margin-top:8px;letter-spacing:0.12em;">
            LINHA {linha_alvo} · JANELA {minutos_janela} MIN · AGUARDANDO SINAL
        </div>
    </div>
    """, unsafe_allow_html=True)