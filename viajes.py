import streamlit as st
import pandas as pd
import requests

# Configuración visual de la página
st.set_page_config(page_title="Planificador de Viajes Pro 2027", page_icon="✈️", layout="wide")

# --- CONEXIÓN COMPARTIDA EN LINCE (REEMPLAZA CON TU LINK DE LA BARRA DE DIRECCIONES) ---
LINK_ORIGINAL = "https://docs.google.com/spreadsheets/d/1DO-CSMEZgfRVAzGDhkdcpklNRPd0q7UlObIdT1ZTcoM/edit?gid=244829372#gid=244829372"

try:
    if "/d/" in LINK_ORIGINAL:
        sheet_id = LINK_ORIGINAL.split("/d/")[1].split("/")[0]
        # Formato de lectura CSV nativo de Google
        URL_BASE = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="
    else:
        st.error("El enlace de Google Sheets no parece ser válido.")
        st.stop()

    def leer_pestaña(nombre_pestaña):
        return pd.read_csv(URL_BASE + nombre_pestaña).dropna(how="all")

    # Carga de datos iniciales
    df_itinerario = leer_pestaña("itinerario")
    df_gastos = leer_pestaña("gastos")
    df_cal_rutas = leer_pestaña("rutas")
    df_alojamientos = leer_pestaña("alojamientos")
    df_checklist = leer_pestaña("checklist")

except Exception as e:
    st.error(f"Error cargando los datos de la nube. Asegúrate de que el enlace de Google Sheets esté configurado como 'Cualquier persona con el enlace' en modo Editor.")
    st.stop()

# Estructurar dataframes vacíos
if df_gastos.empty: df_gastos = pd.DataFrame(columns=["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)", "Persona"])
if df_itinerario.empty: df_itinerario = pd.DataFrame(columns=["Fecha", "Hora", "Ciudad", "Actividad", "Lugar / Ubicación", "Reserva / Ticket"])
if df_alojamientos.empty: df_alojamientos = pd.DataFrame(columns=["País / Ciudad", "Nombre del Alojamiento", "Check-In (Entrada)", "Check-Out (Salida)", "Link de Booking / Enlace"])
if df_checklist.empty: df_checklist = pd.DataFrame(columns=["Categoría", "Tarea", "Hecho"])

if not df_gastos.empty and "Costo ($)" in df_gastos.columns:
    df_gastos["Costo ($)"] = pd.to_numeric(df_gastos["Costo ($)"], errors='coerce').fillna(0.0)

# Estilos visuales sencillos
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e9ecef; }
    div[data-testid="stForm"] { background-color: #f8f9fa; border-radius: 12px; padding: 20px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

CATEGORIAS_GASTO = ["Alojamiento", "Vuelos / Trenes", "Comida (Desayuno/Almuerzo/Cena)", "Transporte / Uber / Metro", "Atracciones / Tickets", "Imprevistos / Shopping"]
CIUDADES = ["Santiago (Inicio/Fin)", "París (Francia)", "Venecia (Italia)", "Roma (Italia)", "Otro Destino"]
INTEGRANTES = ["General / Común", "Josue", "Cesia", "Amparo", "Clara", "Ruth", "Milca"]

st.sidebar.markdown("# ✈️ Euro-Tour 2027")
st.sidebar.caption("Sincronizado con Google Sheets")
st.sidebar.markdown("---")

paginas = ["📊 Tablero y Finanzas", "🗓️ Ruta País 2027", "🏨 Alojamientos y Links", "🗺️ Itinerario x Horas", "💰 Gastos Personales", "🎒 Check-list de Maleta"]
seleccion = st.sidebar.radio("Ir a la sección:", paginas)

# Mensaje instructivo de cómo rellenar
st.info("💡 Para ingresar o editar datos, abre directamente tu planilla de Google Sheets desde tu celular o computadora. Los cambios se verán reflejados aquí inmediatamente al cambiar de pestaña.")

def renderizar_pestaña_persona(p_nombre):
    df_p = df_gastos[df_gastos["Persona"] == p_nombre].copy() if not df_gastos.empty else pd.DataFrame()
    gasto_total_p = df_p["Costo ($)"].sum() if not df_p.empty else 0
    st.metric(label=f"Monto Total Acumulado — {p_nombre}", value=f"${gasto_total_p:,.0f}")
    
    if not df_p.empty:
        st.dataframe(df_p[["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)"]], use_container_width=True, hide_index=True)
    else:
        st.caption("Sin transacciones registradas.")

if seleccion == "📊 Tablero y Finanzas":
    st.title("📊 Resumen General del Viaje (2027)")
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        total_viaje = df_gastos["Costo ($)"].sum() if not df_gastos.empty else 0
        st.metric(label="💰 Costo Total Acumulado del Viaje", value=f"${total_viaje:,.0f}")
    with kpi2:
        alojamiento_total = df_gastos[df_gastos["Categoría"] == "Alojamiento"]["Costo ($)"].sum() if not df_gastos.empty else 0
        st.metric(label="🏨 Total en Alojamientos", value=f"${alojamiento_total:,.0f}")
    with kpi3:
        conteo_actividades = len(df_itinerario) if not df_itinerario.empty else 0
        st.metric(label="📍 Eventos en Itinerario", value=f"{conteo_actividades} hitos")

    st.markdown("---")
    st.subheader("👤 Resumen Financiero por Integrante")
    resumen_personas = [{"Integrante": p, "Total Gastado ($)": df_gastos[df_gastos["Persona"] == p]["Costo ($)"].sum() if not df_gastos.empty else 0} for p in INTEGRANTES]
    df_resumen_p = pd.DataFrame(resumen_personas)
    st.dataframe(df_resumen_p, use_container_width=True, hide_index=True)

elif seleccion == "🗓️ Ruta País 2027":
    st.title("🗓️ Calendario de Ubicación Geográfica")
    st.dataframe(df_cal_rutas, use_container_width=True, hide_index=True)

elif seleccion == "🏨 Alojamientos y Links":
    st.title("🏨 Registro de Alojamientos y Reservas")
    st.dataframe(df_alojamientos, use_container_width=True, hide_index=True)

elif seleccion == "🗺️ Itinerario x Horas":
    st.title("🗺️ Cronograma de Actividades por Horas")
    st.dataframe(df_itinerario, use_container_width=True, hide_index=True)

elif seleccion == "💰 Gastos Personales":
    st.title("💰 Control de Cuentas por Integrante")
    p0, p1, p2, p3, p4, p5, p6 = st.tabs([f"👤 {p}" for p in INTEGRANTES])
    with p0: renderizar_pestaña_persona("General / Común")
    with p1: renderizar_pestaña_persona("Josue")
    with p2: renderizar_pestaña_persona("Cesia")
    with p3: renderizar_pestaña_persona("Amparo")
    with p4: renderizar_pestaña_persona("Clara")
    with p5: renderizar_pestaña_persona("Ruth")
    with p6: renderizar_pestaña_persona("Milca")

elif seleccion == "🎒 Check-list de Maleta":
    st.title("🎒 Maleta Virtual Colectiva")
    st.dataframe(df_checklist, use_container_width=True, hide_index=True)
