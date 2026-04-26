import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ATLAS SMP STOCK EXCHANGE", layout="wide", page_icon="🏛️")

# --- ESTADO GLOBAL ---
if 'empresas' not in st.session_state:
    st.session_state.empresas = {}
if 'pedidos_pendientes' not in st.session_state:
    st.session_state.pedidos_pendientes = []
if 'carteras' not in st.session_state:
    st.session_state.carteras = {}
if 'discord_link' not in st.session_state:
    st.session_state.discord_link = "https://discord.gg/atlas-smp"

# --- SIDEBAR E IDIOMA ---
st.sidebar.title("ATLAS SMP")
idioma = st.sidebar.selectbox("Idioma / Language", ["Español", "English"])

# --- LÓGICA DE LOGIN ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_email:
    if st.sidebar.button("Log in with Google"):
        # Al confirmar con tu mail real, se activa el modo Admin
        st.session_state.user_email = "acollinet509@gmail.com" 
        st.rerun()
else:
    st.sidebar.success(f"Sesión: {st.session_state.user_email}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user_email = None
        st.rerun()

    # --- INTERFAZ PRINCIPAL ---
    st.title("🏛️ BOLSA DE VALORES ATLAS SMP" if idioma == "Español" else "🏛️ ATLAS SMP STOCK EXCHANGE")
    
    # Botón dinámico de Discord
    st.link_button("Discord Server", st.session_state.discord_link)

    tabs = ["📈 Mercado", "🛒 Comprar", "📝 Registrar", "🏢 Mi Empresa", "💼 Cartera", "👑 Admin"]
    t1, t2, t3, t4, t5, t6 = st.tabs(tabs)
    
    with t1:
        if not st.session_state.empresas:
            st.info("No hay empresas registradas.")
        else:
            df = pd.DataFrame([{"Empresa": k, "Precio": v['precio'], "Stock": v['stock'], "Contacto": v['discord']} 
                               for k, v in st.session_state.empresas.items()])
            st.table(df)

    with t2:
        if st.session_state.empresas:
            e_sel = st.selectbox("Empresa", list(st.session_state.empresas.keys()))
            c_sel = st.number_input("Cantidad", min_value=1)
            if st.button("Enviar Pedido"):
                dueño = st.session_state.empresas[e_sel]['dueño']
                st.session_state.pedidos_pendientes.append({
                    "comprador": st.session_state.user_email, "empresa": e_sel, "cantidad": c_sel, "dueño_email": dueño
                })
                st.success("Pedido enviado.")

    with t3:
        with st.form("reg"):
            n = st.text_input("Nombre Empresa")
            p = st.number_input("Precio", min_value=1)
            s = st.number_input("Stock total", min_value=1)
            d = st.text_input("Tu Discord")
            if st.form_submit_button("Lanzar"):
                st.session_state.empresas[n] = {'precio': p, 'stock': s, 'dueño': st.session_state.user_email, 'discord': d}
                st.rerun()

    with t4:
        mis_p = [p for p in st.session_state.pedidos_pendientes if p['dueño_email'] == st.session_state.user_email]
        if not mis_p: st.write("Sin ventas pendientes.")
        else:
            for i, p in enumerate(mis_p):
                st.write(f"**{p['comprador']}** quiere **{p['cantidad']}** de **{p['empresa']}**")
                if st.button("Confirmar Venta", key=f"v_{i}"):
                    st.session_state.empresas[p['empresa']]['stock'] -= p['cantidad']
                    if p['comprador'] not in st.session_state.carteras: st.session_state.carteras[p['comprador']] = {}
                    st.session_state.carteras[p['comprador']][p['empresa']] = st.session_state.carteras[p['comprador']].get(p['empresa'], 0) + p['cantidad']
                    st.session_state.pedidos_pendientes.remove(p)
                    st.rerun()

    with t5:
        c = st.session_state.carteras.get(st.session_state.user_email, {})
        if not c: st.info("No tenés acciones.")
        else:
            for e, q in c.items(): st.write(f"✔️ {e}: {q} acciones")

    # --- AQUÍ ESTÁ TU CONTROL EXCLUSIVO ---
    with t6:
        if st.session_state.user_email == "acollinet509@gmail.com":
            st.subheader("Configuración de Dueño")
            # ESTO SOLO LO VES VOS
            nuevo_link = st.text_input("Editar Link de Discord Principal", value=st.session_state.discord_link)
            if st.button("Guardar nuevo Link"):
                st.session_state.discord_link = nuevo_link
                st.success("Link actualizado para todo el server.")
            
            st.divider()
            if st.button("BORRAR TODAS LAS EMPRESAS"):
                st.session_state.empresas = {}
                st.rerun()
        else:
            st.error("No tenés permisos para cambiar el Discord de la App.")
