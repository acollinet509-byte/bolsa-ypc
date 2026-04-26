import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ATLAS SMP STOCK EXCHANGE", layout="wide", page_icon="🏛️")

# --- TRADUCCIONES ---
TEXTS = {
    "Español": {
        "welcome": "🏛️ BOLSA DE VALORES ATLAS SMP",
        "top_table": "🏆 TOP EMPRESAS",
        "my_company": "🏢 Mi Empresa / Ventas",
        "register": "📝 Registrar Empresa",
        "portfolio": "💼 Mi Cartera",
        "buy_section": "🛒 Mercado",
        "admin_label": "👑 PANEL SANTI (ADMIN)"
    },
    "English": {
        "welcome": "🏛️ ATLAS SMP STOCK EXCHANGE",
        "top_table": "🏆 TOP COMPANIES",
        "my_company": "🏢 My Company / Sales",
        "register": "📝 Register Company",
        "portfolio": "💼 My Portfolio",
        "buy_section": "🛒 Market",
        "admin_label": "👑 SANTI'S ADMIN PANEL"
    }
}

# --- ESTADO GLOBAL ---
if 'empresas' not in st.session_state:
    st.session_state.empresas = {}
if 'pedidos_pendientes' not in st.session_state:
    st.session_state.pedidos_pendientes = [] # [{comprador, empresa, cantidad, dueño}]
if 'carteras' not in st.session_state:
    st.session_state.carteras = {}
if 'discord_link' not in st.session_state:
    st.session_state.discord_link = "https://discord.gg/atlas-smp"

# --- SIDEBAR ---
st.sidebar.title("ATLAS SMP")
idioma = st.sidebar.selectbox("Idioma", ["Español", "English"])
t = TEXTS[idioma]

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_email:
    if st.button("Log in with Google"):
        st.session_state.user_email = "acollinet509@gmail.com"
        st.rerun()
else:
    st.sidebar.success(f"Sesión: {st.session_state.user_email}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user_email = None
        st.rerun()

    st.title(t["welcome"])
    st.link_button("Discord Server", st.session_state.discord_link)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([t["top_table"], t["buy_section"], t["register"], t["my_company"], t["portfolio"]])
    
    # --- TAB 1: MERCADO ---
    with tab1:
        st.subheader(t["top_table"])
        if not st.session_state.empresas:
            st.info("No hay empresas.")
        else:
            df_mostrar = pd.DataFrame([
                {"Empresa": k, "Precio": v['precio'], "Stock": v['stock'], "Dueño": v['discord']} 
                for k, v in st.session_state.empresas.items()
            ])
            st.table(df_mostrar)

    # --- TAB 2: COMPRAR (GENERA PEDIDO) ---
    with tab2:
        st.subheader(t["buy_section"])
        if st.session_state.empresas:
            emp_sel = st.selectbox("Seleccionar Empresa para comprar", list(st.session_state.empresas.keys()))
            cant = st.number_input("Cantidad de acciones", min_value=1)
            if st.button("Enviar Pedido de Compra"):
                dueño_objetivo = st.session_state.empresas[emp_sel]['dueño']
                nuevo_pedido = {
                    "comprador": st.session_state.user_email,
                    "empresa": emp_sel,
                    "cantidad": cant,
                    "dueño_email": dueño_objetivo
                }
                st.session_state.pedidos_pendientes.append(nuevo_pedido)
                st.success("✅ Pedido enviado. El dueño de la empresa debe confirmarlo.")
        else:
            st.write("No hay empresas disponibles.")

    # --- TAB 3: REGISTRO ---
    with tab3:
        st.subheader(t["register"])
        with st.form("reg"):
            n = st.text_input("Nombre")
            p = st.number_input("Precio", min_value=1)
            s = st.number_input("Stock", min_value=1)
            d = st.text_input("Discord")
            if st.form_submit_button("Lanzar"):
                st.session_state.empresas[n] = {'precio': p, 'stock': s, 'dueño': st.session_state.user_email, 'discord': d}
                st.rerun()

    # --- TAB 4: PANEL DEL DUEÑO (NOTIFICACIONES) ---
    with tab4:
        st.subheader("🔔 Pedidos para mi empresa")
        mis_pedidos = [p for p in st.session_state.pedidos_pendientes if p['dueño_email'] == st.session_state.user_email]
        
        if not mis_pedidos:
            st.write("No tenés pedidos pendientes.")
        else:
            for i, p in enumerate(mis_pedidos):
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{p['comprador']}** quiere comprar **{p['cantidad']}** acciones de **{p['empresa']}**")
                if col2.button("Confirmar Venta", key=f"btn_{i}"):
                    # Validar stock
                    if st.session_state.empresas[p['empresa']]['stock'] >= p['cantidad']:
                        # Descontar stock
                        st.session_state.empresas[p['empresa']]['stock'] -= p['cantidad']
                        # Agregar a cartera del comprador
                        if p['comprador'] not in st.session_state.carteras:
                            st.session_state.carteras[p['comprador']] = {}
                        
                        cartera = st.session_state.carteras[p['comprador']]
                        cartera[p['empresa']] = cartera.get(p['empresa'], 0) + p['cantidad']
                        
                        # Eliminar de pendientes
                        st.session_state.pedidos_pendientes.remove(p)
                        st.success("¡Venta confirmada!")
                        st.rerun()
                    else:
                        st.error("No tenés suficiente stock para esta venta.")

    # --- TAB 5: CARTERA DEL USUARIO ---
    with tab5:
        st.subheader(t["portfolio"])
        mi_cartera = st.session_state.carteras.get(st.session_state.user_email, {})
        if not mi_cartera:
            st.info("No tenés acciones confirmadas.")
        else:
            for emp, cant in mi_cartera.items():
                st.write(f"✔️ **{emp}**: {cant} acciones")

    # PANEL SANTI
    if st.session_state.user_email == "acollinet509@gmail.com":
        st.divider()
        if st.button("BORRAR TODO (ADMIN)"):
            st.session_state.empresas = {}
            st.session_state.pedidos_pendientes = []
            st.session_state.carteras = {}
            st.rerun()
