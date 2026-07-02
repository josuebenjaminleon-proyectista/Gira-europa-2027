import streamlit as st
import pandas as pd
import os
import io

# Configuración visual de la página (DEBE SER LO PRIMERO)
st.set_page_config(page_title="Planificador de Viajes Pro 2027", page_icon="✈️", layout="wide")

# --- CONFIGURACIÓN DE ARCHIVOS LOCALES ---
ITINERARIO_FILE = "itinerario_viaje.csv"
GASTOS_FILE = "gastos_viaje.csv"
CALENDARIO_RUTAS_FILE = "calendario_rutas_2027.csv"
ALOJAMIENTOS_FILE = "alojamientos_viaje.csv"
CHECKLIST_FILE = "checklist_viaje.csv"

CATEGORIAS_GASTO = ["Alojamiento", "Vuelos / Trenes", "Comida (Desayuno/Almuerzo/Cena)", "Transporte / Uber / Metro", "Atracciones / Tickets", "Imprevistos / Shopping"]
CIUDADES = ["Santiago (Inicio/Fin)", "París (Francia)", "Venecia (Italia)", "Roma (Italia)", "Otro Destino"]
INTEGRANTES = ["General / Común", "Josue", "Cesia", "Amparo", "Clara", "Ruth", "Milca"]

# --- INICIALIZACIÓN Y CARGA GLOBAL DE DATOS ---

# 1. Itinerario
if not os.path.exists(ITINERARIO_FILE):
    df_itinerario = pd.DataFrame(columns=["Fecha", "Hora", "Ciudad", "Actividad", "Lugar / Ubicación", "Reserva / Ticket"])
    df_itinerario.to_csv(ITINERARIO_FILE, index=False)
else:
    df_itinerario = pd.read_csv(ITINERARIO_FILE)

# 2. Gastos
if not os.path.exists(GASTOS_FILE):
    df_gastos = pd.DataFrame(columns=["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)", "Persona"])
    df_gastos.to_csv(GASTOS_FILE, index=False)
else:
    df_gastos = pd.read_csv(GASTOS_FILE)
    if "Persona" not in df_gastos.columns:
        df_gastos["Persona"] = "General / Común"

# 3. Alojamientos
if not os.path.exists(ALOJAMIENTOS_FILE):
    df_alojamientos = pd.DataFrame(columns=["País / Ciudad", "Nombre del Alojamiento", "Check-In (Entrada)", "Check-Out (Salida)", "Link de Booking / Enlace"])
    df_alojamientos.to_csv(ALOJAMIENTOS_FILE, index=False)
else:
    df_alojamientos = pd.read_csv(ALOJAMIENTOS_FILE)

# 4. Checklist (Maleta)
if not os.path.exists(CHECKLIST_FILE):
    tareas_base = [
        {"Categoría": "📋 Documentación Crítica", "Tarea": "Pasaporte vigente (¡Revisar fechas!)", "Hecho": False},
        {"Categoría": "📋 Documentación Crítica", "Tarea": "Seguro médico internacional con cobertura Europa", "Hecho": False},
        {"Categoría": "📋 Documentación Crítica", "Tarea": "Reservas impresas de Hoteles/Vuelos", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Adaptadores para enchufes de Italia/Francia", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Baterías portátiles cargadas", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Medicamentos personales", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Zapatillas cómodas para caminar", "Hecho": False}
    ]
    df_checklist = pd.DataFrame(tareas_base)
    df_checklist.to_csv(CHECKLIST_FILE, index=False)
else:
    df_checklist = pd.read_csv(CHECKLIST_FILE)

df_checklist["Hecho"] = df_checklist["Hecho"].astype(bool)

# 5. Calendario de Rutas
rango_fechas_viaje = [
    "2027-06-22", "2027-06-23", "2027-06-24", "2027-06-25", "2027-06-26",
    "2027-06-27", "2027-06-28", "2027-06-29", "2027-06-30", "2027-07-01",
    "2027-07-02", "2027-07-03", "2027-07-04", "2027-07-05", "2027-07-06", "2027-07-07"
]
dias_semana_mapeo = ["Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", "Lunes", "Martes", "Miércoles"]

def obtener_ciudad_por_defecto(fecha):
    if fecha in ["2027-06-22", "2027-07-07"]: return "Santiago (Inicio/Fin)"
    elif fecha in ["2027-06-23", "2027-06-24", "2027-06-25", "2027-07-04", "2027-07-05", "2027-07-06"]: return "París (Francia)"
    elif fecha in ["2027-06-26", "2027-06-27", "2027-06-28"]: return "Venecia (Italia)"
    elif fecha in ["2027-06-29", "2027-06-30", "2027-07-01", "2027-07-02", "2027-07-03"]: return "Roma (Italia)"
    return "Por definir"

if not os.path.exists(CALENDARIO_RUTAS_FILE):
    ciudades_defecto = [obtener_ciudad_por_defecto(f) for f in rango_fechas_viaje]
    df_cal_rutas = pd.DataFrame({"Fecha": rango_fechas_viaje, "Día de la Semana": dias_semana_mapeo, "País / Ciudad donde Estaremos
