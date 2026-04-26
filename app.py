import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Esto conecta la app con el link que acabas de pegar en Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def traer_datos():
    try:
        # Esto lee tu Excel en tiempo real
        return conn.read(ttl=0)
    except:
        # Si el Excel está vacío, crea las columnas
        return pd.DataFrame(columns=["Nombre", "Precio", "Stock", "Dueño", "Discord", "Email"])
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

# --- SIDEBAR ---
st.sidebar.title("ATLAS SMP")
idioma = st.sidebar.selectbox("Idioma / Language", ["Español", "English"])

if "user_email" not in st.session_state:
    st.session_state.user_email = None

# SISTEMA DE LOGIN
if not st.session_state.user_email:
    if st.sidebar.button("Log in with Google"):
        # Al loguearte, el sistema reconoce si sos acollinet509@gmail.com
        st.session_state.user_email = "acollinet509@gmail.com" 
        st.rerun()
else:
    st.sidebar.success(f"Sesión: {st.session_state.user_email}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user_email = None
        st.rerun()

    # --- TÍTULO Y DISCORD ---
    st.title("🏛️ BOLSA DE VALORES ATLAS SMP" if idioma == "Español" else "🏛️ ATLAS SMP STOCK EXCHANGE")
    st.link_button("Discord Server", st.session_state.discord_link)

    tabs = ["📈 Mercado", "🛒 Comprar", "📝 Registrar", "🏢 Gestión Empresa", "💼 Mi Cartera", "👑 Admin"]
    t1, t2, t3, t4, t5, t6 = st.tabs(tabs)
    
    # 1. TABLA DE EMPRESAS
    with t1:
        if not st.session_state.empresas:
            st.info("No hay empresas en el mercado.")
        else:
            df = pd.DataFrame([{"Empresa": k, "Precio (💎)": v['precio'], "Stock": v['stock'], "Dueño": v['discord']} 
                               for k, v in st.session_state.empresas.items()])
            st.table(df)

    # 2. COMPRAR ACCIONES (PEDIDO A LA EMPRESA)
    with t2:
        if st.session_state.empresas:
            e_sel = st.selectbox("Elegí empresa para comprar", list(st.session_state.empresas.keys()))
            cant_c = st.number_input("Cantidad a comprar", min_value=1)
            if st.button("Enviar Pedido de Compra"):
                dueño_e = st.session_state.empresas[e_sel]['dueño']
                st.session_state.pedidos_pendientes.append({
                    "tipo": "COMPRA", "usuario": st.session_state.user_email, 
                    "empresa": e_sel, "cantidad": cant_c, "dueño_email": dueño_e
                })
                st.success(f"Pedido enviado a {e_sel}. Esperá a que el dueño confirme.")
        else:
            st.write("No hay empresas registradas.")

    # 3. REGISTRAR EMPRESA
    with t3:
        with st.form("registro_e"):
            n = st.text_input("Nombre de la Empresa")
            p = st.number_input("Valor de cada acción", min_value=1)
            s = st.number_input("Acciones totales a la venta", min_value=1)
            d = st.text_input("Tu Discord")
            if st.form_submit_button("Lanzar a la Bolsa"):
                st.session_state.empresas[n] = {'precio': p, 'stock': s, 'dueño': st.session_state.user_email, 'discord': d}
                st.success("¡Empresa lanzada!")
                st.rerun()

    # 4. GESTIÓN DE LA EMPRESA (NOTIFICACIONES DE COMPRA Y VENTA)
    with t4:
        st.subheader("🔔 Pedidos de Clientes (Compras y Devoluciones)")
        mis_pedidos = [p for p in st.session_state.pedidos_pendientes if p['dueño_email'] == st.session_state.user_email]
        
        if not mis_pedidos:
            st.write("No tenés movimientos pendientes.")
        else:
            for i, p in enumerate(mis_pedidos):
                tipo_txt = "QUIERE COMPRAR" if p['tipo'] == "COMPRA" else "QUIERE DEVOLVER/VENDER"
                st.write(f"📩 **{p['usuario']}** {tipo_txt} **{p['cantidad']}** acciones de **{p['empresa']}**")
                
                if st.button("Aceptar Operación", key=f"op_{i}"):
                    if p['tipo'] == "COMPRA":
                        if st.session_state.empresas[p['empresa']]['stock'] >= p['cantidad']:
                            st.session_state.empresas[p['empresa']]['stock'] -= p['cantidad']
                            if p['usuario'] not in st.session_state.carteras: st.session_state.carteras[p['usuario']] = {}
                            cartera = st.session_state.carteras[p['usuario']]
                            cartera[p['empresa']] = cartera.get(p['empresa'], 0) + p['cantidad']
                            st.session_state.pedidos_pendientes.remove(p)
                            st.success("Venta confirmada.")
                            st.rerun()
                    else:
                        # Reventa a la empresa (Vuelve al stock)
                        st.session_state.carteras[p['usuario']][p['empresa']] -= p['cantidad']
                        st.session_state.empresas[p['empresa']]['stock'] += p['cantidad']
                        st.session_state.pedidos_pendientes.remove(p)
                        st.success("Recompra confirmada.")
                        st.rerun()

    # 5. MI CARTERA (SOLO SE PUEDE VENDER A LA EMPRESA ORIGINAL)
    with t5:
        st.subheader("Tus Acciones")
        mi_c = st.session_state.carteras.get(st.session_state.user_email, {})
        if not mi_c or all(v == 0 for v in mi_c.values()):
            st.info("No tenés acciones confirmadas.")
        else:
            for emp, cant in mi_c.items():
                if cant > 0:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"🔸 **{emp}**: {cant} unidades")
                    cant_v = col2.number_input(f"Cantidad", min_value=1, max_value=cant, key=f"v_{emp}")
                    if col3.button("Vender a Empresa", key=f"btn_v_{emp}"):
                        dueño_orig = st.session_state.empresas[emp]['dueño']
                        st.session_state.pedidos_pendientes.append({
                            "tipo": "VENTA", "usuario": st.session_state.user_email, 
                            "empresa": emp, "cantidad": cant_v, "dueño_email": dueño_orig
                        })
                        st.warning(f"Solicitud de venta enviada al dueño de {emp}.")

    # 6. ADMIN (SOLO acollinet509@gmail.com)
    with t6:
        if st.session_state.user_email == "acollinet509@gmail.com":
            st.subheader("👑 Panel de Santi")
            # Cambiar Discord
            new_discord = st.text_input("Actualizar Link de Discord", value=st.session_state.discord_link)
            if st.button("Guardar Link"):
                st.session_state.discord_link = new_discord
                st.success("Link actualizado.")
            
            st.divider()
            if st.button("RESETEAR BOLSA (BORRAR TODO)"):
                st.session_state.empresas = {}
                st.session_state.pedidos_pendientes = []
                st.session_state.carteras = {}
                st.rerun()
        else:
            st.error("No tenés permisos de Administrador.")
