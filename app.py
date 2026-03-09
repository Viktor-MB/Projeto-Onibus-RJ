import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import pytz
import time

# Configurações de Página
st.set_page_config(page_title="RioBusTracker", layout="wide")
FUSO = pytz.timezone('America/Sao_Paulo')
CORES = ['blue', 'green', 'purple', 'orange', 'red', 'darkred', 'cadetblue', 'darkgreen', 'black']

st.title("🚌 Monitoramento em Tempo Real - SPPO RJ")

# Sidebar para Configurações
st.sidebar.header("Configurações de Rastreio")
linha_alvo = st.sidebar.text_input("Linha do Ônibus", value="202")
minutos_janela = st.sidebar.slider("Minutos de rastro retroativo", 5, 60, 10)
refresh_rate = st.sidebar.slider("Atualizar a cada (segundos)", 15, 60, 30)

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
        
        df['latitude'] = pd.to_numeric(df['latitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'].astype(str).str.replace(',', '.'), errors='coerce')
        df_f = df[df['linha'] == str(linha)].copy().sort_values('datahora').dropna(subset=['latitude', 'longitude'])
        return df_f
    except:
        return None

# Loop de Atualização Automática
placeholder = st.empty()

while True:
    with placeholder.container():
        dados_bus = buscar_dados(linha_alvo, minutos_janela)
        
        if dados_bus is not None and not dados_bus.empty:
            st.write(f"📡 Exibindo **{len(dados_bus['ordem'].unique())}** ônibus da linha **{linha_alvo}**")
            
            # Criar Mapa
            m = folium.Map(location=[dados_bus['latitude'].mean(), dados_bus['longitude'].mean()], zoom_start=14)
            
            for i, (ordem, trajetoria) in enumerate(dados_bus.groupby('ordem')):
                cor = CORES[i % len(CORES)]
                coords = trajetoria[['latitude', 'longitude']].values.tolist()
                
                # Rastro e Marcadores com Tooltip (Hover) conforme solicitado
                folium.PolyLine(coords, color=cor, weight=4, opacity=0.6).add_to(m)
                folium.Marker(coords[0], tooltip=f"Início - ID: {ordem}", 
                              icon=folium.Icon(color='white', icon_color=cor, icon='play', prefix='fa')).add_to(m)
                folium.Marker(coords[-1], tooltip=f"Atual - ID: {ordem}", 
                              icon=folium.Icon(color=cor, icon='bus', prefix='fa')).add_to(m)
            
            # Renderizar no Streamlit
            st_folium(m, width=1200, height=600, returned_objects=[])
        else:
            st.warning(f"Aguardando dados da linha {linha_alvo}...")
            
    time.sleep(refresh_rate)