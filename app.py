import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="ATLAS SMP STOCK EXCHANGE", layout="wide", page_icon="🏛️")

# 2. CONEXIÓN A LA BASE DE DATOS (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def traer_datos():
    try:
        # Lee el Excel en tiempo real (ttl=0 para que no use memoria vieja)
        return conn.read(ttl=0).dropna(how='all')
    except:
        # Si el Excel está vacío o hay error, crea la tabla con las columnas correctas
        return pd.DataFrame(columns=["Nombre", "Precio", "Stock", "Dueño", "Discord", "Email"])

# 3. LÓGICA DE LOGIN
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_email:
    st.title("🏛️ BOLSA DE VALORES ATLAS SMP")
    if st.button("Iniciar Sesión con Google"):
        st.session_state.user_email = "acollinet509@gmail.com" 
        st.rerun()
else:
    st.sidebar.success(f"Conectado: {st.session_state.user_email}")
    st.title("🏛️ BOLSA DE VALORES ATLAS SMP")

    # PESTAÑAS
    tab1, tab2 = st.tabs(["📈 Mercado", "📝 Registrar Empresa"])

    with tab1:
        st.subheader("Acciones en Vivo")
        df = traer_datos()
        if df.empty:
            st.info("No hay empresas registradas todavía.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Registrar tu Nueva Empresa")
        with st.form("registro_form"):
            nombre_e = st.text_input("Nombre de la Empresa")
            precio_e = st.number_input("Precio por acción (Diamantes)", min_value=1)
            stock_e = st.number_input("Cantidad de acciones", min_value=1)
            discord_e = st.text_input("Tu Discord")
            
            if st.form_submit_button("Guardar en la Base de Datos"):
                if nombre_e and discord_e:
                    df_actual = traer_datos()
                    
                    # Creamos la nueva fila
                    nueva_fila = pd.DataFrame([{
                        "Nombre": nombre_e, 
                        "Precio": precio_e, 
                        "Stock": stock_e, 
                        "Dueño": discord_e, 
                        "Discord": discord_e, 
                        "Email": st.session_state.user_email
                    }])
                    
                    # Unimos lo viejo con lo nuevo
                    df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    
                    # ESCRIBE EN TU GOOGLE SHEET
                    conn.update(data=df_final)
                    
                    st.success(f"¡{nombre_e} guardada! Ya aparece en el Mercado.")
                    st.rerun()
                else:
                    st.error("Por favor, completá todos los campos.")
