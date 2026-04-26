import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="ATLAS SMP STOCK EXCHANGE", layout="wide", page_icon="🏛️")

# 2. CONEXIÓN AL EXCEL (Usa el link que pegaste en Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

def traer_datos():
    try:
        # Lee el Excel. ttl=0 hace que no use caché y traiga lo nuevo siempre
        data = conn.read(ttl=0)
        # Limpiamos filas vacías por si las dudas
        return data.dropna(how='all')
    except Exception as e:
        # Si el Excel está vacío o falla, devuelve una tabla con las columnas correctas
        return pd.DataFrame(columns=["Nombre", "Precio", "Stock", "Dueño", "Discord", "Email"])

# 3. SESIÓN Y LOGIN
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

    tab1, tab2 = st.tabs(["📈 Mercado", "📝 Registrar Empresa"])

    with tab1:
        st.subheader("Acciones Disponibles")
        df = traer_datos()
        
        if df.empty or len(df) == 0:
            st.info("Todavía no hay empresas en la base de datos. ¡Sé el primero en registrar una!")
        else:
            # Mostramos la tabla del Excel de forma prolija
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Lanzar tu Empresa")
        with st.form("reg_form"):
            nom = st.text_input("Nombre de la Empresa")
            pre = st.number_input("Precio por acción (Diamantes)", min_value=1)
            sto = st.number_input("Cantidad de acciones a la venta", min_value=1)
            dis = st.text_input("Tu usuario de Discord (ej: Santi#1234)")
            
            if st.form_submit_button("Guardar en la Base de Datos"):
                if nom and dis:
                    df_actual = traer_datos()
                    
                    # Creamos la nueva fila
                    nueva_fila = pd.DataFrame([{
                        "Nombre": nom, 
                        "Precio": pre, 
                        "Stock": sto, 
                        "Dueño": dis, 
                        "Discord": dis, 
                        "Email": st.session_state.user_email
                    }])
                    
                    # Juntamos lo viejo con lo nuevo
                    df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    
                    # ¡ESTO ESCRIBE EN EL GOOGLE SHEET!
                    conn.update(data=df_final)
                    
                    st.success(f"¡{nom} ha sido registrada con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor completá el nombre y tu Discord.")
