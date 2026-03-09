# 🚌 RioBusTracker-Streamlit

## Link para o app: https://projeto-onibus-rj.streamlit.app/

### 📍 Monitoramento e Visualização Dinâmica da Frota SPPO (Rio de Janeiro)

Este projeto consiste em uma aplicação web interativa desenvolvida em **Streamlit** para o rastreamento em tempo real dos ônibus do Rio de Janeiro. A solução utiliza dados da API pública `dados.mobilidade.rio` para processar trajetórias e identificar padrões de deslocamento urbano através de uma interface geoespacial intuitiva.

---

## 🚀 Funcionalidades Principais

* **Dashboard Interativo:** Controle total sobre a linha monitorada e a janela de tempo do rastro via interface lateral (sidebar).
* **Lógica de Janela Deslizante (Sliding Window):** Visualização focada no deslocamento recente, calculada pela fórmula:
  $$T_{window} = [T_{now} - \Delta t, T_{now}]$$
* **Identificação Visual de Frota:**
    * **Rastro Vetorial:** Polilinhas coloridas (paleta de 18 cores) que conectam o trajeto histórico.
    * **Interação via Hover:** Uso de *tooltips* para exibir o identificador (`ordem`) do veículo sem poluir o mapa.
    * **Marcadores de Estado:** Diferenciação entre o ponto de partida no rastro (▶️) e a posição atual (🚌).
* **Auto-Refresh:** Atualização automática dos dados da API em intervalos configuráveis, garantindo o monitoramento contínuo.

---

## 🛠️ Stack Tecnológica

* **Linguagem:** Python
* **Interface Web:** Streamlit & Streamlit-Folium
* **Processamento de Dados:** Pandas (Normalização de coordenadas e limpeza de telemetria)
* **Mapas Interativos:** Folium (Baseado em Leaflet.js)
* **Time Management:** Pytz & Datetime



---

## 🔍 Insights da Pesquisa (Março 2026)

Durante a fase de testes com a linha **202 (Rio Comprido x Castelo)** e trajetos em **Jacarepaguá**, o projeto revelou padrões operacionais importantes:

1.  **Gargalos de Tráfego:** Através da densidade do rastro em janelas de 10 minutos, foi possível identificar trechos de baixa velocidade média em horários de pico.
2.  **Consistência de API:** Identificação de variações no *ping* dos dispositivos embarcados, o que direcionou o desenvolvimento de técnicas de suavização de trajetórias.
3.  **Logística de Terminais:** Validação da precisão da API ao detectar o agrupamento de veículos em pontos de regulação, como o Terminal Castelo.

---

## ⚙️ Como Executar o Projeto

1.  **Prepare o Ambiente Virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # No Windows: .venv\Scripts\activate
    ```
2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Inicie a Aplicação:**
    ```bash
    cd app
    streamlit run app.py
    ```

---

## 👨‍💻 Autor

**Viktor Mayer Berruezo**
* Discente de **Ciência de Dados e IA** no **Ibmec**.}
* [Relatório do Projeto](https://docs.google.com/document/d/1GUIKU1AaDyPoLxdvRMlCLnGwlwVGoeArYItLC4JwTiY/edit?tab=t.0) 



---


**Dados fornecidos por:** [Escritório de Dados - Prefeitura do Rio de Janeiro](https://dados.mobilidade.rio).
