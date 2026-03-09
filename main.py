import pandas as pd
import requests
import folium
from datetime import datetime, timedelta
import pytz

# Configurações fixas para a automação
FUSO = pytz.timezone('America/Sao_Paulo')
CORES = ['blue', 'green', 'purple', 'orange', 'red', 'darkred', 'cadetblue', 'darkgreen', 'black']
LINHA_ALVO = "202" # Linha padrão para o site
MINUTOS_JANELA = 15

def buscar_e_salvar():
    agora = datetime.now(FUSO)
    inicio = agora - timedelta(minutes=MINUTOS_JANELA)
    
    params = {
        "dataInicial": inicio.strftime('%Y-%m-%d %H:%M:%S'),
        "dataFinal": agora.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        r = requests.get("https://dados.mobilidade.rio/gps/sppo", params=params, timeout=15)
        df = pd.DataFrame(r.json())
        
        if not df.empty:
            df['latitude'] = pd.to_numeric(df['latitude'].astype(str).str.replace(',', '.'), errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'].astype(str).str.replace(',', '.'), errors='coerce')
            df_f = df[df['linha'] == str(LINHA_ALVO)].copy().sort_values('datahora').dropna(subset=['latitude', 'longitude'])

            # Criar Mapa
            m = folium.Map(location=[df_f['latitude'].mean(), df_f['longitude'].mean()], zoom_start=14)
            
            for i, (ordem, trajetoria) in enumerate(df_f.groupby('ordem')):
                cor = CORES[i % len(CORES)]
                coords = trajetoria[['latitude', 'longitude']].values.tolist()
                folium.PolyLine(coords, color=cor, weight=4, opacity=0.6).add_to(m)
                folium.Marker(coords[0], tooltip=f"Início - ID: {ordem}", icon=folium.Icon(color='white', icon_color=cor, icon='play', prefix='fa')).add_to(m)
                folium.Marker(coords[-1], tooltip=f"Atual - ID: {ordem}", icon=folium.Icon(color=cor, icon='bus', prefix='fa')).add_to(m)
            
            # SALVAR O ARQUIVO QUE O GITHUB PAGES VAI LER
            m.save("index.html")
            print("Mapa index.html atualizado com sucesso.")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    buscar_e_salvar()