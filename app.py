import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ATLAS SMP STOCK EXCHANGE", layout="wide", page_icon="🏛️")

# --- TRADUCCIONES ---
TEXTS = {
    "Español": {
        "welcome": "🏛️ BOLSA DE VALORES ATLAS SMP",
        "top_table": "🏆 TOP EMPRESAS",
        "my_company": "🏢 Mi Empresa",
        "register": "📝 Registrar Empresa",
        "discord_btn": "Discord del Server",
        "login_msg": "Iniciá sesión con tu Gmail para operar.",
        "admin_label": "👑 PANEL SANTI (ADMIN)"
    },
    "English": {
        "welcome": "🏛️ ATLAS SMP STOCK EXCHANGE",
        "top_table": "🏆 TOP COMPANIES",
        "my_company": "🏢 My Company",
        "register": "📝 Register Company",
        "discord_btn": "Server Discord",
        "login_msg": "Sign in with Gmail to operate.",
        "admin_label": "👑 SANTI'S ADMIN PANEL"
    }
}

# --- BASE DE DATOS TEMPORAL ---
if 'empresas' not in st.session_state:
    st.session_state.empresas = {}
if 'discord_link' not in st.session_state:
    st.session_state.discord_link = "https://discord.gg/atlas-smp"

# --- SIDEBAR E IDIOMA ---
st.sidebar.title("ATLAS SMP")
idioma = st.sidebar.selectbox("Idioma", ["Español", "English"])
t = TEXTS[idioma]

# --- LÓGICA DE LOGIN ---
# Usamos el sistema de autenticación de Streamlit
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_email:
    st.title(t["welcome"])
    st.warning(t["login_msg"])
    # Botón de simulación de Google Auth
    if st.button("Log in with Google / Iniciar Sesión con Google"):
        # AQUÍ: Streamlit detectaría tu cuenta. Para la prueba:
        st.session_state.user_email = "acollinet509@gmail.com" # Simulación
        st.rerun()
else:
    st.sidebar.success(f"Usuario: {st.session_state.user_email}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user_email = None
        st.rerun()

    # --- CUERPO DE LA APP ---
    st.title(t["welcome"])
    st.link_button(t["discord_btn"], st.session_state.discord_link)

    tab1, tab2, tab3, tab4 = st.tabs([t["top_table"], t["register"], t["my_company"], "Config"])
    
    with tab1:
        st.subheader(t["top_table"])
        if not st.session_state.empresas:
            st.info("No hay empresas registradas.")
        else:
            tabla_data = []
            for nombre, datos in st.session_state.empresas.items():
                tabla_data.append({
                    "Empresa": nombre,
                    "Precio (💎)": datos['precio'],
                    "Vendidas": datos['vendidas'],
                    "En Venta": datos['stock'],
                    "Contacto (Discord)": datos['discord']
                })
            st.table(pd.DataFrame(tabla_data).sort_values(by="Vendidas", ascending=False))

    with tab2:
        st.subheader(t["register"])
        # Solo una empresa por Gmail
        if st.session_state.user_email in [e['dueño'] for e in st.session_state.empresas.values()]:
            st.error("Este Gmail ya tiene una empresa registrada.")
        else:
            with st.form("crear_empresa"):
                nom = st.text_input("Nombre de la Empresa")
                pre = st.number_input("Precio por acción", min_value=1)
                sto = st.number_input("Acciones a la venta", min_value=1)
                dis = st.text_input("Tu Discord")
                if st.form_submit_button("Lanzar"):
                    st.session_state.empresas[nom] = {
                        'precio': pre, 'stock': sto, 'vendidas': 0, 'dueño': st.session_state.user_email, 'discord': dis
                    }
                    st.success("¡Empresa registrada!")
                    st.rerun()

    with tab3:
        st.subheader(t["my_company"])
        mi_emp = next((k for k, v in st.session_state.empresas.items() if v['dueño'] == st.session_state.user_email), None)
        if mi_emp:
            with st.form("update"):
                st.session_state.empresas[mi_emp]['precio'] = st.number_input("Precio", value=st.session_state.empresas[mi_emp]['precio'])
                st.session_state.empresas[mi_emp]['stock'] = st.number_input("Stock", value=st.session_state.empresas[mi_emp]['stock'])
                if st.form_submit_button("Guardar"):
                    st.success("Actualizado")
        else:
            st.warning("No tenés empresa.")

    with tab4:
        # AQUÍ ESTÁ TU SEGURIDAD:
        if st.session_state.user_email == "acollinet509@gmail.com":
            st.subheader(t["admin_label"])
            st.session_state.discord_link = st.text_input("Link Discord Global", value=st.session_state.discord_link)
            if st.button("Borrar todas las empresas (RESETEO)"):
                st.session_state.empresas = {}
                st.rerun()
        else:
            st.error("Solo acollinet509@gmail.com puede entrar acá.")
