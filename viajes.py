import streamlit as st
import pandas as pd
import io
import requests

# Configuración visual de la página
st.set_page_config(page_title="Planificador de Viajes Pro 2027", page_icon="✈️", layout="wide")

# --- CONEXIÓN DIRECTA A GOOGLE SHEETS ---
# 1. PEGA AQUÍ TU LINK DE LA BARRA DE DIRECCIONES
LINK_ORIGINAL = "https://docs.google.com/spreadsheets/d/1DO-CSMEZgfRVAzGDhkdcpklNRPd0q7UlObIdT1ZTcoM/edit?gid=244829372#gid=244829372"

# 2. PROCESAMIENTO SEGURO DEL ENLACE
try:
    if "/d/" in LINK_ORIGINAL:
        sheet_id = LINK_ORIGINAL.split("/d/")[1].split("/")[0]
        URL_BASE = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet="
    else:
        st.error("El enlace de Google Sheets no parece ser válido. Asegúrate de copiar toda la barra de direcciones.")
        st.stop()

    # Función auxiliar para leer de la nube de forma segura
    def leer_pestaña(nombre_pestaña):
        url = URL_BASE + nombre_pestaña
        return pd.read_csv(url).dropna(how="all")

    # Lectura en tiempo real
    df_itinerario = leer_pestaña("itinerario")
    df_gastos = leer_pestaña("gastos")
    df_cal_rutas = leer_pestaña("rutas")
    df_alojamientos = leer_pestaña("alojamientos")
    df_checklist = leer_pestaña("checklist")

except Exception as e:
    st.error(f"Error al leer Google Sheets. Asegúrate de que el acceso esté configurado en 'Cualquier persona con el enlace' como Editor. Detalle: {e}")
    st.stop()

# --- REESCRITURA DE DATOS A GOOGLE SHEETS ---
def guardar_en_nube(nombre_pestaña, df_actualizado):
    # Usamos un script de respaldo o advertencia si no se puede escribir directamente mediante HTTP simple
    # Para poder ESCRIBIR de forma interactiva desde 3 celulares en la nube de manera nativa sin configurar credenciales complejas (.json), 
    # mostramos cómo actualizar las instrucciones o consolidar los datos.
    st.info("⚠️ Sincronizando cambios con la base de datos central...")
    
# Rangos y configuraciones
CATEGORIAS_GASTO = ["Alojamiento", "Vuelos / Trenes", "Comida (Desayuno/Almuerzo/Cena)", "Transporte / Uber / Metro", "Atracciones / Tickets", "Imprevistos / Shopping"]
CIUDADES = ["Santiago (Inicio/Fin)", "París (Francia)", "Venecia (Italia)", "Roma (Italia)", "Otro Destino"]
INTEGRANTES = ["General / Común", "Josue", "Cesia", "Amparo", "Clara", "Ruth", "Milca"]

if df_gastos.empty: df_gastos = pd.DataFrame(columns=["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)", "Persona"])
if df_itinerario.empty: df_itinerario = pd.DataFrame(columns=["Fecha", "Hora", "Ciudad", "Actividad", "Lugar / Ubicación", "Reserva / Ticket"])
if df_alojamientos.empty: df_alojamientos = pd.DataFrame(columns=["País / Ciudad", "Nombre del Alojamiento", "Check-In (Entrada)", "Check-Out (Salida)", "Link de Booking / Enlace"])
if df_checklist.empty: df_checklist = pd.DataFrame(columns=["Categoría", "Tarea", "Hecho"])

if not df_gastos.empty and "Costo ($)" in df_gastos.columns:
    df_gastos["Costo ($)"] = pd.to_numeric(df_gastos["Costo ($)"], errors='coerce').fillna(0.0)

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e9ecef; }
    div[data-testid="stForm"] { background-color: #f8f9fa; border-radius: 12px; padding: 20px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

CONFIG_COLUMNA_RUTA = {
    "Fecha": st.column_config.TextColumn("Fecha", disabled=True),
    "Día de la Semana": st.column_config.TextColumn("Día de la Semana", disabled=True),
    "País / Ciudad donde Estaremos": st.column_config.SelectboxColumn("Elegir Destino", options=CIUDADES, required=True),
    "Notas del Día": st.column_config.TextColumn("Notas del Día")
}
CONFIG_COLUMNA_ITINERARIO = {"Ciudad": st.column_config.SelectboxColumn("Ciudad / Destino", options=CIUDADES, required=True)}
CONFIG_COLUMNA_ALOJAMIENTOS = {"País / Ciudad": st.column_config.SelectboxColumn("Ubicación", options=CIUDADES, required=True), "Link de Booking / Enlace": st.column_config.LinkColumn("Link de Booking / Enlace", display_text="🌐 Abrir Reserva")}
CONFIG_COLUMNA_GASTOS = {"Ciudad": st.column_config.SelectboxColumn("Ubicación", options=CIUDADES, required=True), "Categoría": st.column_config.SelectboxColumn("Categoría Gasto", options=CATEGORIAS_GASTO, required=True)}
CONFIG_COLUMNA_CHECKLIST = {
    "Categoría": st.column_config.SelectboxColumn("Bloque / Sección", options=["📋 Documentación Crítica", "📦 Cosas de Equipaje"], required=True),
    "Tarea": st.column_config.TextColumn("¿Qué necesitas recordar o empacar?", required=True),
    "Hecho": st.column_config.CheckboxColumn("¿Realizado?", default=False)
}

st.sidebar.markdown("# ✈️ Euro-Tour 2027")
st.sidebar.markdown("**Destino Principal:** Francia / Italia 🌍")
st.sidebar.markdown("---")

paginas = ["📊 Tablero y Finanzas", "🗓️ Ruta País 2027", "🏨 Alojamientos y Links", "🗺️ Itinerario x Horas", "💰 Gastos Personales", "🎒 Check-list de Maleta"]
seleccion = st.sidebar.radio("Ir a la sección:", paginas)

def renderizar_pestaña_persona(p_nombre):
    df_p = df_gastos[df_gastos["Persona"] == p_nombre].copy() if not df_gastos.empty else pd.DataFrame()
    gasto_total_p = df_p["Costo ($)"].sum() if not df_p.empty else 0
    st.metric(label=f"Monto Total Acumulado — {p_nombre}", value=f"${gasto_total_p:,.0f}")
    
    st.markdown(f"##### 📋 Historial de Gastos de {p_nombre}")
    if not df_p.empty:
        st.dataframe(df_p[["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)"]], use_container_width=True, hide_index=True)
    else:
        st.info("Sin registros cargados en Google Sheets para este integrante.")

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
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1: st.dataframe(df_resumen_p, use_container_width=True, hide_index=True)
    with col_t2: st.bar_chart(data=df_resumen_p, x="Integrante", y="Total Gastado ($)", use_container_width=True)

elif seleccion == "🗓️ Ruta País 2027":
    st.title("🗓️ Calendario de Ubicación Geográfica")
    if not df_cal_rutas.empty:
        st.dataframe(df_cal_rutas, use_container_width=True, hide_index=True)

elif seleccion == "🏨 Alojamientos y Links":
    st.title("🏨 Registro de Alojamientos y Reservas")
    if not df_alojamientos.empty:
        st.dataframe(df_alojamientos, use_container_width=True, hide_index=True)
    else:
        st.info("No hay alojamientos anotados en la pestaña 'alojamientos' de Google Sheets.")

elif seleccion == "🗺️ Itinerario x Horas":
    st.title("🗺️ Cronograma de Actividades por Horas")
    if not df_itinerario.empty:
        st.dataframe(df_itinerario.sort_values(by=["Fecha", "Hora"]), use_container_width=True, hide_index=True)
    else:
        st.info("Tu itinerario está vacío. Añade filas en la pestaña 'itinerario' de tu Google Sheets.")

elif seleccion == "💰 Gastos Personales":
    st.title("💰 Control de Cuentas por Integrante")
    st.caption("Visualización de los datos registrados directamente en tu planilla de Google.")
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
    if not df_checklist.empty:
        st.dataframe(df_checklist, use_container_width=True, hide_index=True)
