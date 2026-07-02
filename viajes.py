import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# Configuración visual de la página
st.set_page_config(page_title="Planificador de Viajes Pro 2027", page_icon="✈️", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
# REEMPLAZA EL LINK DE ABAJO CON EL TUYO DE GOOGLE SHEETS
URL_SHEET = "https://docs.google.com/spreadsheets/d/1DO-CSMEZgfRVAzGDhkdcpklNRPd0q7UlObIdT1ZTcoM/edit?usp=sharing"

CATEGORIAS_GASTO = ["Alojamiento", "Vuelos / Trenes", "Comida (Desayuno/Almuerzo/Cena)", "Transporte / Uber / Metro", "Atracciones / Tickets", "Imprevistos / Shopping"]
CIUDADES = ["Santiago (Inicio/Fin)", "París (Francia)", "Venecia (Italia)", "Roma (Italia)", "Otro Destino"]
INTEGRANTES = ["General / Común", "Josue", "Cesia", "Amparo", "Clara", "Ruth", "Milca"]

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lectura de datos en la nube
    df_itinerario = conn.read(spreadsheet=URL_SHEET, worksheet="itinerario", ttl=0).dropna(how="all")
    df_gastos = conn.read(spreadsheet=URL_SHEET, worksheet="gastos", ttl=0).dropna(how="all")
    df_cal_rutas = conn.read(spreadsheet=URL_SHEET, worksheet="rutas", ttl=0).dropna(how="all")
    df_alojamientos = conn.read(spreadsheet=URL_SHEET, worksheet="alojamientos", ttl=0).dropna(how="all")
    df_checklist = conn.read(spreadsheet=URL_SHEET, worksheet="checklist", ttl=0).dropna(how="all")
except Exception as e:
    st.error(f"Error de conexión con Google Sheets. Verifica el link compartido: {e}")
    st.stop()

# Garantizar estructuras mínimas en caso de planillas vacías
if df_gastos.empty: df_gastos = pd.DataFrame(columns=["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)", "Persona"])
if df_itinerario.empty: df_itinerario = pd.DataFrame(columns=["Fecha", "Hora", "Ciudad", "Actividad", "Lugar / Ubicación", "Reserva / Ticket"])
if df_alojamientos.empty: df_alojamientos = pd.DataFrame(columns=["País / Ciudad", "Nombre del Alojamiento", "Check-In (Entrada)", "Check-Out (Salida)", "Link de Booking / Enlace"])
if df_checklist.empty:
    tareas_base = [
        {"Categoría": "📋 Documentación Crítica", "Tarea": "Pasaporte vigente (¡Revisar fechas!)", "Hecho": False},
        {"Categoría": "📋 Documentación Crítica", "Tarea": "Seguro médico internacional con cobertura Europa", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Adaptadores para punches de Italia/Francia", "Hecho": False},
        {"Categoría": "📦 Cosas de Equipaje", "Tarea": "Baterías portátiles cargadas", "Hecho": False}
    ]
    df_checklist = pd.DataFrame(tareas_base)
    conn.update(spreadsheet=URL_SHEET, worksheet="checklist", data=df_checklist)

if df_cal_rutas.empty:
    rango_fechas_viaje = ["2027-06-22", "2027-06-23", "2027-06-24", "2027-06-25", "2027-06-26", "2027-06-27", "2027-06-28", "2027-06-29", "2027-06-30", "2027-07-01", "2027-07-02", "2027-07-03", "2027-07-04", "2027-07-05", "2027-07-06", "2027-07-07"]
    dias_semana_mapeo = ["Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", "Lunes", "Martes", "Miércoles"]
    df_cal_rutas = pd.DataFrame({"Fecha": rango_fechas_viaje, "Día de la Semana": dias_semana_mapeo, "País / Ciudad donde Estaremos": "Por definir", "Notas del Día": ""})
    conn.update(spreadsheet=URL_SHEET, worksheet="rutas", data=df_cal_rutas)

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
st.sidebar.markdown("**Destino Principal:** Francia / Italia 🌍  \n**Sincronización:** Cloud Activa ☁️")
st.sidebar.markdown("---")

paginas = ["📊 Tablero y Finanzas", "🗓️ Ruta País 2027", "🏨 Alojamientos y Links", "🗺️ Itinerario x Horas", "💰 Gastos Personales", "🎒 Check-list de Maleta"]
seleccion = st.sidebar.radio("Ir a la sección:", paginas)

if not df_gastos.empty:
    df_gastos["Costo ($)"] = pd.to_numeric(df_gastos["Costo ($)"], errors='coerce').fillna(0.0)

def renderizar_pestaña_persona(p_nombre):
    df_p = df_gastos[df_gastos["Persona"] == p_nombre].copy()
    gasto_total_p = df_p["Costo ($)"].sum() if not df_p.empty else 0
    st.metric(label=f"Monto Total Acumulado — {p_nombre}", value=f"${gasto_total_p:,.0f}")
    
    col_f1, col_f2 = st.columns([1.8, 1.2])
    with col_f1:
        st.markdown(f"##### ➕ Registrar nuevo cargo a {p_nombre}")
        with st.form(f"form_v23_{p_nombre}", clear_on_submit=True):
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                f_gasto = st.date_input("Fecha Pago", key=f"f_v23_{p_nombre}")
                concepto = st.text_input("Concepto / Detalle de Gasto", key=f"c_v23_{p_nombre}").strip()
                cat_g = st.selectbox("Categoría", CATEGORIAS_GASTO, key=f"cat_v23_{p_nombre}")
            with c_g2:
                ciudad_g = st.selectbox("Ubicación Geográfica", CIUDADES, key=f"ciudad_v23_{p_nombre}")
                monto_g = st.number_input("Monto total en pesos ($)", min_value=0.0, step=5000.0, format="%.0f", key=f"monto_v23_{p_nombre}")
            
            if st.form_submit_button(f"💾 Guardar Gasto para {p_nombre}"):
                if concepto and monto_g > 0:
                    f_str = f_gasto.strftime("%Y-%m-%d")
                    nuevo_g = pd.DataFrame([[f_str, concepto, cat_g, ciudad_g, monto_g, p_nombre]], columns=["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)", "Persona"])
                    df_global = conn.read(spreadsheet=URL_SHEET, worksheet="gastos", ttl=0).dropna(how="all")
                    df_final = pd.concat([df_global, nuevo_g], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="gastos", data=df_final)
                    st.success(f"¡Gasto añadido a {p_nombre}!")
                    st.rerun()

    with col_f2:
        st.markdown("##### 📋 Clonar / Mover Gastos")
        if not df_p.empty:
            df_p["ID_Combo"] = df_p["Concepto / Ítem"].astype(str) + " ($" + df_p["Costo ($)"].astype(str) + ")"
            gasto_origen = st.selectbox("1. Selecciona el gasto:", df_p["ID_Combo"].values, key=f"src_v23_{p_nombre}")
            opciones_destino = [dest for dest in INTEGRANTES if dest != p_nombre]
            persona_destino = st.selectbox("2. Enviar copia / mover a:", opciones_destino, key=f"dest_v23_{p_nombre}")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("👥 Copiar Gasto", key=f"btn_copy_v23_{p_nombre}", use_container_width=True):
                    df_global = conn.read(spreadsheet=URL_SHEET, worksheet="gastos", ttl=0).dropna(how="all")
                    fila_clonar = df_global[(df_global["Persona"] == p_nombre) & ((df_global["Concepto / Ítem"].astype(str) + " ($" + df_global["Costo ($)"].astype(str) + ")") == gasto_origen)].copy()
                    if not fila_clonar.empty:
                        fila_clonar["Persona"] = persona_destino
                        df_final = pd.concat([df_global, fila_clonar], ignore_index=True)
                        conn.update(spreadsheet=URL_SHEET, worksheet="gastos", data=df_final)
                        st.rerun()
            with c_btn2:
                if st.button("➡️ Mover Gasto", key=f"btn_move_v23_{p_nombre}", use_container_width=True):
                    df_global = conn.read(spreadsheet=URL_SHEET, worksheet="gastos", ttl=0).dropna(how="all")
                    combo_global = df_global["Concepto / Ítem"].astype(str) + " ($" + df_global["Costo ($)"].astype(str) + ")"
                    idx = df_global[(df_global["Persona"] == p_nombre) & (combo_global == gasto_origen)].index[0]
                    df_global.at[idx, "Persona"] = persona_destino
                    conn.update(spreadsheet=URL_SHEET, worksheet="gastos", data=df_global)
                    st.rerun()

    st.markdown("---")
    col_eliminar, col_tabla = st.columns([1, 2])
    with col_eliminar:
        st.markdown("##### 🗑️ Eliminar Registro")
        if not df_p.empty:
            df_p["ID_Combo"] = df_p["Concepto / Ítem"].astype(str) + " ($" + df_p["Costo ($)"].astype(str) + ")"
            gasto_baja = st.selectbox("Seleccione transacción a borrar:", df_p["ID_Combo"].values, key=f"baja_v23_{p_nombre}")
            if st.button("❌ Eliminar Transacción", type="primary", use_container_width=True, key=f"btn_baja_v23_{p_nombre}"):
                df_global = conn.read(spreadsheet=URL_SHEET, worksheet="gastos", ttl=0).dropna(how="all")
                combo_global = df_global["Concepto / Ítem"].astype(str) + " ($" + df_global["Costo ($)"].astype(str) + ")"
                df_global = df_global[~((df_global["Persona"] == p_nombre) & (combo_global == gasto_baja))]
                conn.update(spreadsheet=URL_SHEET, worksheet="gastos", data=df_global)
                st.warning("Gasto borrado.")
                st.rerun()
        else: st.caption("No hay elementos.")

    with col_tabla:
        st.markdown("##### 📋 Tabla de Control")
        if not df_p.empty:
            df_mostrar = df_p[["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)"]]
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        else: st.info("Sin registros.")

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
    resumen_personas = [{"Integrante": p, "Total Gastado ($)": df_gastos[df_gastos["Persona"] == p]["Costo ($)"].sum()} for p in INTEGRANTES]
    df_resumen_p = pd.DataFrame(resumen_personas)
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1: st.dataframe(df_resumen_p, use_container_width=True, hide_index=True)
    with col_t2: st.bar_chart(data=df_resumen_p, x="Integrante", y="Total Gastado ($)", use_container_width=True)

elif seleccion == "🗓️ Ruta País 2027":
    st.title("🗓️ Calendario de Ubicación Geográfica - Verano 2027")
    df_cal_editado = st.data_editor(df_cal_rutas, column_config=CONFIG_COLUMNA_RUTA, use_container_width=True, hide_index=True, key="editor_ruta_pais_v22")
    
    if st.button("💾 Guardar Cambios de la Ruta", type="primary", use_container_width=True):
        conn.update(spreadsheet=URL_SHEET, worksheet="rutas", data=df_cal_editado)
        st.success("¡Calendario sincronizado!")
        st.rerun()

elif seleccion == "🏨 Alojamientos y Links":
    st.title("🏨 Registro de Alojamientos y Reservas")
    c_al1, c_al2 = st.columns([1.2, 1.8])
    with c_al1:
        with st.form("form_alojamientos", clear_on_submit=True):
            pais_al = st.selectbox("País / Ciudad", CIUDADES)
            nombre_al = st.text_input("Nombre del Hotel / Depto").strip()
            checkin = st.date_input("Fecha Check-In")
            checkout = st.date_input("Fecha Check-Out")
            link_bk = st.text_input("Pegar Link de Booking").strip()
            
            if st.form_submit_button("💾 Guardar Alojamiento"):
                if nombre_al:
                    nuevo_al = pd.DataFrame([[pais_al, nombre_al, checkin.strftime("%Y-%m-%d"), checkout.strftime("%Y-%m-%d"), link_bk]], columns=["País / Ciudad", "Nombre del Alojamiento", "Check-In (Entrada)", "Check-Out (Salida)", "Link de Booking / Enlace"])
                    df_global = conn.read(spreadsheet=URL_SHEET, worksheet="alojamientos", ttl=0).dropna(how="all")
                    df_final = pd.concat([df_global, nuevo_al], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="alojamientos", data=df_final)
                    st.success("¡Alojamiento registrado!")
                    st.rerun()
    with c_al2:
        if not df_alojamientos.empty:
            al_borrar = st.selectbox("Selecciona para remover:", df_alojamientos["Nombre del Alojamiento"].values)
            if st.button("❌ Eliminar Alojamiento", type="primary", use_container_width=True):
                df_global = df_alojamientos[df_alojamientos["Nombre del Alojamiento"] != al_borrar]
                conn.update(spreadsheet=URL_SHEET, worksheet="alojamientos", data=df_global)
                st.rerun()
    if not df_alojamientos.empty:
        st.data_editor(df_alojamientos, column_config=CONFIG_COLUMNA_ALOJAMIENTOS, use_container_width=True, hide_index=True)

elif seleccion == "🗺️ Itinerario x Horas":
    st.title("🗺️ Cronograma de Actividades por Horas")
    col_add, col_del = st.columns([1.2, 1.8])
    with col_add:
        with st.form("form_itinerario", clear_on_submit=True):
            fecha_evento = st.date_input("Fecha")
            hora_evento = st.time_input("Hora del Evento")
            ciudad_evento = st.selectbox("Ciudad / Destino", CIUDADES)
            actividad = st.text_input("Actividad / Atracción").strip()
            lugar = st.text_input("Dirección / Barrio").strip()
            reserva = st.text_input("Código de Reserva / Notas").strip()
            
            if st.form_submit_button("💾 Guardar Hito"):
                if actividad:
                    nuevo_evento = pd.DataFrame([[fecha_evento.strftime("%Y-%m-%d"), hora_evento.strftime("%H:%M"), ciudad_evento, actividad, lugar, reserva]], columns=["Fecha", "Hora", "Ciudad", "Actividad", "Lugar / Ubicación", "Reserva / Ticket"])
                    df_global = conn.read(spreadsheet=URL_SHEET, worksheet="itinerario", ttl=0).dropna(how="all")
                    df_final = pd.concat([df_global, nuevo_evento], ignore_index=True)
                    conn.update(spreadsheet=URL_SHEET, worksheet="itinerario", data=df_final)
                    st.success("¡Actividad guardada!")
                    st.rerun()
    with col_del:
        if not df_itinerario.empty:
            df_itinerario["ID_Temp"] = df_itinerario["Fecha"] + " (" + df_itinerario["Hora"] + ") - " + df_itinerario["Actividad"]
            evento_borrar = st.selectbox("Selecciona hito a borrar:", df_itinerario["ID_Temp"].values)
            if st.button("❌ Quitar del Itinerario", type="primary", use_container_width=True):
                df_global = df_itinerario[df_itinerario["ID_Temp"] != evento_borrar].drop(columns=["ID_Temp"], errors="ignore")
                conn.update(spreadsheet=URL_SHEET, worksheet="itinerario", data=df_global)
                st.rerun()
    if not df_itinerario.empty:
        st.data_editor(df_itinerario.sort_values(by=["Fecha", "Hora"]), column_config=CONFIG_COLUMNA_ITINERARIO, use_container_width=True, hide_index=True)

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
    df_check_editado = st.data_editor(df_checklist, column_config=CONFIG_COLUMNA_CHECKLIST, use_container_width=True, hide_index=True, key="editor_check_v5")
    if st.button("💾 Sincronizar Maleta / Tareas", type="primary", use_container_width=True):
        conn.update(spreadsheet=URL_SHEET, worksheet="checklist", data=df_check_editado)
        st.success("¡Checklist guardado en la nube!")
        st.rerun()
