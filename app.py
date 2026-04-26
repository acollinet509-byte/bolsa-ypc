import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Y.P.C. Stock Exchange", layout="wide", page_icon="📈")

# Estilo personalizado para que se vea más pro
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4b5063;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Bolsa de Valores Y.P.C.")
st.write("Bienvenido al centro financiero del servidor. Invertí en el futuro.")
st.divider()

# --- DATOS DEL MERCADO (Simulación inicial) ---
# Después podés conectar esto a un Google Sheets para que sea real
if 'market_data' not in st.session_state:
    st.session_state.market_data = pd.DataFrame([
        {"Empresa": "Y.P.C.", "Compra": 150, "Venta": 165, "Acciones": 100, "Disponibles": 20, "Variación": 5.4},
        {"Empresa": "Krynno Corp", "Compra": 80, "Venta": 95, "Acciones": 50, "Disponibles": 12, "Variación": -1.2},
        {"Empresa": "Alemania Ind.", "Compra": 110, "Venta": 125, "Acciones": 80, "Disponibles": 5, "Variación": 2.8}
    ])

# --- PANEL SUPERIOR: COTIZACIONES EN VIVO ---
st.subheader("📊 Pizarra de Precios")
cols = st.columns(len(st.session_state.market_data))

for i, row in st.session_state.market_data.iterrows():
    with cols[i]:
        st.metric(
            label=row['Empresa'], 
            value=f"{row['Venta']} 💎", 
            delta=f"{row['Variación']}%"
        )
        st.write(f"**Stock:** {row['Disponibles']} / {row['Acciones']}")

st.divider()

# --- GRÁFICO DE TENDENCIAS ---
st.subheader("📈 Rendimiento en Tiempo Real")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Y.P.C.', 'Krynno', 'Alemania']
).cumsum() # Esto simula subidas y bajadas
st.line_chart(chart_data)

# --- SECCIÓN PARA REGISTRAR EMPRESAS ---
st.divider()
col_a, col_b = st.columns([1, 2])

with col_a:
    st.subheader("📝 Registrar Empresa")
    st.write("¿Querés que tu empresa cotice en la bolsa de Y.P.C.?")
    with st.form("registro_empresa"):
        nombre = st.text_input("Nombre de la Empresa")
        p_venta = st.number_input("Precio de Venta inicial", min_value=1)
        acc_total = st.number_input("Total de Acciones", min_value=1)
        submit = st.form_submit_button("Postular a la Bolsa")
        
        if submit:
            st.success(f"Solicitud de {nombre} enviada. El CEO de Y.P.C. la revisará pronto.")

with col_b:
    st.subheader("📋 Información de Mercado")
    st.dataframe(st.session_state.market_data, use_container_width=True)

# --- PIE DE PÁGINA ---
st.markdown("---")
st.caption("Y.P.C. - Logística, Independencia y Progreso. 2026.")
