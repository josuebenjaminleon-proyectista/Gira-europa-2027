import streamlit as st
import pandas as pd
import os
import io

# --- CONFIGURACIÓN DE ARCHIVOS LOCALES ---
ITINERARIO_FILE = "itinerario_viaje.csv"
GASTOS_FILE = "gastos_viaje.csv"
CALENDARIO_RUTAS_FILE = "calendario_rutas_2027.csv"
ALOJAMIENTOS_FILE = "alojamientos_viaje.csv"
CHECKLIST_FILE = "checklist_viaje.csv"

CATEGORIAS_GASTO = ["Alojamiento", "Vuelos / Trenes", "Comida (Desayuno/Almuerzo/Cena)", "Transporte / Uber / Metro", "Atracciones / Tickets", "Imprevistos / Shopping"]
CIUDADES = ["Santiago (Inicio/Fin)", "París (Francia)", "Venecia (Italia)", "Roma (Italia)", "Otro Destino"]
INTEGRANTES = ["General / Común", "Josue", "Cesia", "Amparo", "Clara", "Ruth", "Milca"]

# Inicialización segura de las Bases de Datos
if os.path.exists(ITINERARIO_FILE):
    df_itinerario = pd.read_csv(ITINERARIO_FILE)
else:
    df_itinerario = pd.DataFrame(columns=["Fecha", "Hora", "Ciudad", "Actividad", "Lugar / Ubicación", "Reserva / Ticket"])

if os.path.exists(GASTOS_FILE):
    df_gastos = pd.read_csv(GASTOS_FILE)
    if "Persona" not in df_gastos.columns:
        df_gastos["Persona"] = "General / Común"
else:
    df_gastos = pd.DataFrame(columns=["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)", "Persona"])

if os.path.exists(ALOJAMIENTOS_FILE):
    df_alojamientos = pd.read_csv(ALOJAMIENTOS_FILE)
else:
    df_alojamientos = pd.DataFrame(columns=["País / Ciudad", "Nombre del Alojamiento", "Check-In (Entrada)", "Check-Out (Salida)", "Link de Booking / Enlace"])

if os.path.exists(CHECKLIST_FILE):
    df_checklist = pd.read_csv(CHECKLIST_FILE)
    df_checklist["Hecho"] = df_checklist["Hecho"].astype(bool)
else:
    tareas_base = [
        {"Categoría": "📋 Documentación Crítica", "Tarea": "Pasaporte vigente (¡Revisar fechas!)", "Hecho": False},
        {"Categoría": "📋 Documentación Crítica", "Tarea": "Seguro médico internacional con cobertura Europa", "Hecho": False},
        {"Categoría": "📋 Documentación Crítica", "Tarea": "Reservas impresas de Hoteles/Vuelos", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Adaptadores para punches de Italia/Francia", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Baterías portátiles cargadas", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Medicamentos personales", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Zapatillas cómodas para caminar", "Hecho": False}
    ]
    df_checklist = pd.DataFrame(tareas_base)
    df_checklist.to_csv(CHECKLIST_FILE, index=False)

# Rango de fechas estricto del viaje (22 de Junio al 07 de Julio 2027)
rango_fechas_viaje = [
    "2027-06-22", "2027-06-23", "2027-06-24", "2027-06-25", "2027-06-26",
    "2027-06-27", "2027-06-28", "2027-06-29", "2027-06-30", "2027-07-01",
    "2027-07-02", "2027-07-03", "2027-07-04", "2027-07-05", "2027-07-06", "2027-07-07"
]
dias_semana_mapeo = ["Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", "Lunes", "Martes", "Miércoles"]

def obtener_ciudad_por_defecto(fecha):
    if fecha == "2027-06-22" or fecha == "2027-07-07":
        return "Santiago (Inicio/Fin)"
    elif fecha in ["2027-06-23", "2027-06-24", "2027-06-25"]:
        return "París (Francia)"
    elif fecha in ["2027-06-26", "2027-06-27", "2027-06-28"]:
        return "Venecia (Italia)"
    elif fecha in ["2027-06-29", "2027-06-30", "2027-07-01", "2027-07-02", "2027-07-03"]:
        return "Roma (Italia)"
    elif fecha in ["2027-07-04", "2027-07-05", "2027-07-06"]:
        return "París (Francia)"
    return "Por definir"

if os.path.exists(CALENDARIO_RUTAS_FILE):
    df_cal_rutas = pd.read_csv(CALENDARIO_RUTAS_FILE)
    df_cal_rutas = df_cal_rutas[df_cal_rutas["Fecha"].isin(rango_fechas_viaje)].copy()
    df_cal_rutas["Notas del Día"] = df_cal_rutas["Notas del Día"].fillna("").astype(str)
else:
    ciudades_defecto = [obtener_ciudad_por_defecto(f) for f in rango_fechas_viaje]
    df_cal_rutas = pd.DataFrame({"Fecha": rango_fechas_viaje, "Día de la Semana": dias_semana_mapeo, "País / Ciudad donde Estaremos": ciudades_defecto, "Notas del Día": ""})
    df_cal_rutas["Notas del Día"] = df_cal_rutas["Notas del Día"].astype(str)
    df_cal_rutas.to_csv(CALENDARIO_RUTAS_FILE, index=False)

# Configuración visual de la página
st.set_page_config(page_title="Planificador de Viajes Pro 2027", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e9ecef; }
    div[data-testid="stForm"] { background-color: #f8f9fa; border-radius: 12px; padding: 20px; border: 1px solid #e9ecef; }
    div[data-testid="stNotification"] p { font-size: 1.15rem !important; font-weight: 500 !important; }
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
CONFIG_COLUMNA_GASTOS = {"Ciudad": st.column_config.SelectboxColumn("Ubicación", options=CIUDADES, required=True), "Categoría": st.column_config
