import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Planificador de Viajes Pro 2027", page_icon="✈️", layout="wide")

# Validar configuraciones de Secrets
try:
    LINK_ORIGINAL = st.secrets["general"]["spreadsheet_url"]
    SCRIPT_URL = st.secrets["general"]["script_url"]
    sheet_id = LINK_ORIGINAL.split("/d/")[1].split("/")[0]
    URL_BASE = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="
except Exception:
    st.error("Por favor, asegúrate de configurar 'spreadsheet_url' y 'script_url' en los Secrets de Streamlit Cloud.")
    st.stop()

def leer_pestaña(nombre_pestaña):
    try:
        return pd.read_csv(f"{URL_BASE}{nombre_pestaña}&nocache={pd.Timestamp.now().microsecond}").dropna(how="all")
    except:
        return pd.DataFrame()

# Cargar datos desde la nube
df_itinerario = leer_pestaña("itinerario")
df_gastos = leer_pestaña("gastos")
df_cal_rutas = leer_pestaña("rutas")
df_alojamientos = leer_pestaña("alojamientos")
df_checklist = leer_pestaña("checklist")

# --- MENSAJE DE DIAGNÓSTICO EN VIVO ---
st.sidebar.markdown("### 🔍 Estado de Conexión")
if df_gastos.empty and df_itinerario.empty:
    st.sidebar.warning("⚠️ No se lee ninguna pestaña. Verifica que el enlace público de Google Sheets sea correcto.")
else:
    st.sidebar.success("🟢 Conectado con éxito a Google Sheets")

if df_gastos.empty: df_gastos = pd.DataFrame(columns=["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)", "Persona"])
if df_itinerario.empty: df_itinerario = pd.DataFrame(columns=["Fecha", "Hora", "Ciudad", "Actividad", "Lugar / Ubicación", "Reserva / Ticket"])
if df_alojamientos.empty: df_alojamientos = pd.DataFrame(columns=["País / Ciudad", "Nombre del Alojamiento", "Check-In (Entrada)", "Check-Out (Salida)", "Link de Booking / Enlace"])
if df_checklist.empty: df_checklist = pd.DataFrame(columns=["Categoría", "Tarea", "Hecho"])

if not df_gastos.empty and "Costo ($)" in df_gastos.columns:
    df_gastos["Costo ($)"] = pd.to_numeric(df_gastos["Costo ($)"], errors='coerce').fillna(0.0)

# CONECTOR HTTP OPTIMIZADO
def enviar_a_google(nombre_pestaña, lista_datos):
    payload = {"pestaña": nombre_pestaña, "datos": lista_datos}
    try:
        res = requests.post(SCRIPT_URL, json=payload, timeout=15)
        if res.status_code == 200:
            respuesta_json = res.json()
            if respuesta_json.get("status") == "success":
                st.success("¡Guardado exitosamente en Google Sheets!")
                st.balloons()
                return True
            else:
                st.error(f"Error devuelto por Google Sheets: {respuesta_json.get('message')}")
                st.info(f"💡 Pista: Ve a tu Google Sheets y verifica que la pestaña de abajo se llame exactamente '{nombre_pestaña}' sin mayúsculas ni espacios.")
        else:
            st.error(f"Error de conexión con el servidor (Código {res.status_code}).")
    except Exception as e:
        st.error(f"No se pudo conectar con Google Sheets: {e}")
    return False

# Estilos visuales
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
    div[data-testid="stForm"] { background-color: #ffffff; border-radius: 12px; padding: 18px; border: 1px solid #dee2e6; }
    </style>
""", unsafe_allow_html=True)

CATEGORIAS_GASTO = ["Alojamiento", "Vuelos / Trenes", "Comida (Desayuno/Almuerzo/Cena)", "Transporte / Uber / Metro", "Atracciones / Tickets", "Imprevistos / Shopping"]
CIUDADES = ["Santiago (Inicio/Fin)", "París (Francia)", "Venecia (Italia)", "Roma (Italia)", "Otro Destino"]
INTEGRANTES = ["General / Común", "Josue", "Cesia", "Amparo", "Clara", "Ruth", "Milca"]

st.sidebar.markdown("# ✈️ Euro-Tour 2027")
seleccion = st.sidebar.radio("Ir a la sección:", ["📊 Tablero y Finanzas", "🗓️ Ruta País 2027", "🏨 Alojamientos y Links", "🗺️ Itinerario x Horas", "💰 Gastos Personales", "🎒 Check-list de Maleta"])

def renderizar_pestaña_persona(p_nombre):
    df_p = df_gastos[df_gastos["Persona"] == p_nombre].copy() if not df_gastos.empty else pd.DataFrame()
    st.metric(label=f"Monto Total Acumulado — {p_nombre}", value=f"${df_p['Costo ($)'].sum():,.0f}")
    
    with st.form(f"form_g_{p_nombre}", clear_on_submit=True):
        f_gasto = st.date_input("Fecha Pago")
        concepto = st.text_input("Concepto / Detalle de Gasto").strip()
        cat_g = st.selectbox("Categoría", CATEGORIAS_GASTO)
        ciudad_g = st.selectbox("Ubicación Geográfica", CIUDADES)
        monto_g = st.number_input("Monto en pesos ($)", min_value=0.0, step=1000.0, format="%.0f")
        
        if st.form_submit_button("💾 Guardar Gasto"):
            if concepto and monto_g > 0:
                fila = [f_gasto.strftime("%Y-%m-%d"), concepto, cat_g, ciudad_g, float(monto_g), p_nombre]
                if enviar_a_google("gastos", fila):
                    st.rerun()
            else:
                st.warning("Completa el concepto y un costo mayor a cero.")

    if not df_p.empty:
        st.dataframe(df_p[["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)"]], use_container_width=True, hide_index=True)

if seleccion == "📊 Tablero y Finanzas":
    st.title("📊 Resumen General del Viaje (2027)")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("💰 Costo Total Acumulado", f"${df_gastos['Costo ($)'].sum():,.0f}")
    kpi2.metric("🏨 Total en Alojamientos", f"${df_gastos[df_gastos['Categoría'] == 'Alojamiento']['Costo ($)'].sum():,.0f}")
    kpi3.metric("📍 Eventos en Itinerario", f"{len(df_itinerario)} hitos")
    st.markdown("---")
    resumen_personas = [{"Integrante": p, "Total Gastado ($)": df_gastos[df_gastos["Persona"] == p]["Costo ($)"].sum()} for p in INTEGRANTES]
    st.dataframe(pd.DataFrame(resumen_personas), use_container_width=True, hide_index=True)

elif seleccion == "🗓️ Ruta País 2027":
    st.title("🗓️ Calendario de Ubicación Geográfica")
    st.dataframe(df_cal_rutas, use_container_width=True, hide_index=True)

elif seleccion == "🏨 Alojamientos y Links":
    st.title("🏨 Registro de Alojamientos y Reservas")
    with st.form("form_alojamientos", clear_on_submit=True):
        pais_al = st.selectbox("País / Ciudad", CIUDADES)
        nombre_al = st.text_input("Nombre del Hotel / Depto").strip()
        checkin = st.date_input("Fecha Check-In")
        checkout = st.date_input("Fecha Check-Out")
        link_bk = st.text_input("Link de Booking").strip()
        if st.form_submit_button("💾 Guardar Alojamiento"):
            if nombre_al:
                fila = [pais_al, nombre_al, checkin.strftime("%Y-%m-%d"), checkout.strftime("%Y-%m-%d"), link_bk]
                if enviar_a_google("alojamientos", fila): st.rerun()
    st.dataframe(df_alojamientos, use_container_width=True, hide_index=True)

elif seleccion == "🗺️ Itinerario x Horas":
    st.title("🗺️ Cronograma de Actividades por Horas")
    with st.form("form_itinerario", clear_on_submit=True):
        fecha_ev = st.date_input("Fecha")
        hora_ev = st.time_input("Hora del Evento")
        ciudad_ev = st.selectbox("Ciudad / Destino", CIUDADES)
        actividad = st.text_input("Actividad").strip()
        lugar = st.text_input("Ubicación").strip()
        reserva = st.text_input("Notas / Reserva").strip()
        if st.form_submit_button("💾 Guardar Hito"):
            if actividad:
                fila = [fecha_ev.strftime("%Y-%m-%d"), hora_ev.strftime("%H:%M"), ciudad_ev, actividad, lugar, reserva]
                if enviar_a_google("itinerario", fila): st.rerun()
    st.dataframe(df_itinerario, use_container_width=True, hide_index=True)

elif seleccion == "💰 Gastos Personales":
    st.title("💰 Control de Cuentas por Integrante")
    tabs = st.tabs([f"👤 {p}" for p in INTEGRANTES])
    for idx, p in enumerate(INTEGRANTES):
        with tabs[idx]: renderizar_pestaña_persona(p)

elif seleccion == "🎒 Check-list de Maleta":
    st.title("🎒 Maleta Virtual Colectiva")
    st.dataframe(df_checklist, use_container_width=True, hide_index=True)
