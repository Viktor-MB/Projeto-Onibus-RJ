import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import pytz
# Adicione esta biblioteca ao seu requirements.txt: streamlit-autorefresh
from streamlit_autorefresh import st_autorefresh

# Configurações de Página
st.set_page_config(page_title="RioBusTracker", layout="wide")
FUSO = pytz.timezone('America/Sao_Paulo')
CORES = ['blue', 'green', 'purple', 'orange', 'red', 'darkred', 'cadetblue', 'darkgreen', 'black']

st.title("🚌 Monitoramento em Tempo Real - SPPO RJ")

# Sidebar para Configurações
st.sidebar.header("Configurações de Rastreio")
linha_alvo = st.sidebar.text_input("Linha do Ônibus", value="202")
minutos_janela = st.sidebar.slider("Minutos de rastro retroativo", 5, 60, 15)
refresh_rate = st.sidebar.slider("Atualizar a cada (segundos)", 15, 60, 30)

# O segredo para o Cloud: Atualização automática sem loop infinito
st_autorefresh(interval=refresh_rate * 1000, key="datarefresh")

def buscar_dados(linha, minutos):
    agora = datetime.now(FUSO)
    inicio = agora - timedelta(minutes=minutos)
    
    params = {
        "dataInicial": inicio.strftime('%Y-%m-%d %H:%M:%S'),
        "dataFinal": agora.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        r = requests.get("https://dados.mobilidade.rio/gps/sppo", params=params, timeout=15)
        df = pd.DataFrame(r.json())
        if df.empty: return None
        
        # Conversão de Unix para Datetime (Brasil/RJ)
        df['datahora_dt'] = pd.to_datetime(df['datahora'], unit='s').dt.tz_localize('UTC').dt.tz_convert(FUSO)
        df['datahora_envio_dt'] = pd.to_datetime(df['datahoraenvio'], unit='s').dt.tz_localize('UTC').dt.tz_convert(FUSO)
        
        # Tratamento de coordenadas
        df['latitude'] = pd.to_numeric(df['latitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'].astype(str).str.replace(',', '.'), errors='coerce')
        
        df_f = df[df['linha'] == str(linha)].copy().sort_values('datahora').dropna(subset=['latitude', 'longitude'])
        return df_f
    except Exception as e:
        st.error(f"Erro na API: {e}")
        return None

# Execução do Dashboard
dados_bus = buscar_dados(linha_alvo, minutos_janela)

if dados_bus is not None and not dados_bus.empty:
    st.write(f"📡 Última atualização: **{datetime.now(FUSO).strftime('%H:%M:%S')}** | Ônibus ativos: **{len(dados_bus['ordem'].unique())}**")
    
    # Criar Mapa centralizado
    m = folium.Map(location=[dados_bus['latitude'].mean(), dados_bus['longitude'].mean()], zoom_start=14)
    
    for i, (ordem, trajetoria) in enumerate(dados_bus.groupby('ordem')):
        cor = CORES[i % len(CORES)]
        coords = trajetoria[['latitude', 'longitude']].values.tolist()
        
        # Pegar dados da última posição para o Tooltip
        ultima_pos = trajetoria.iloc[-1]
        h_captura = ultima_pos['datahora_dt'].strftime('%H:%M:%S')
        h_envio = ultima_pos['datahora_envio_dt'].strftime('%H:%M:%S')
        latencia = (ultima_pos['datahora_envio_dt'] - ultima_pos['datahora_dt']).total_seconds()

        # Rastro
        folium.PolyLine(coords, color=cor, weight=4, opacity=0.4).add_to(m)
        
        # Tooltip com HTML para ficar organizado
        tooltip_html = f"""
            <div style="font-family: sans-serif; font-size: 12px;">
                <b>Bus ID:</b> {ordem}<br>
                <b>Captura GPS:</b> {h_captura}<br>
                <b>Recebido em:</b> {h_envio}<br>
                <b>Latência:</b> {int(latencia)} segundos
            </div>
        """

        folium.Marker(
            coords[-1], 
            tooltip=folium.Tooltip(tooltip_html),
            icon=folium.Icon(color=cor, icon='bus', prefix='fa')
        ).add_to(m)
    
    st_folium(m, width=1200, height=600, returned_objects=[])
else:
    st.info(f"Nenhum ônibus da linha {linha_alvo} detectado nos últimos {minutos_janela} minutos.")