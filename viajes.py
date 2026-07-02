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

# --- INICIALIZACIÓN BLINDADA DE BASES DE DATOS (EVITA FILE NOT FOUND) ---

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
    df_cal_rutas = pd.DataFrame({"Fecha": rango_fechas_viaje, "Día de la Semana": dias_semana_mapeo, "País / Ciudad donde Estaremos": ciudades_defecto, "Notas del Día": ""})
    df_cal_rutas["Notas del Día"] = df_cal_rutas["Notas del Día"].astype(str)
    df_cal_rutas.to_csv(CALENDARIO_RUTAS_FILE, index=False)
else:
    df_cal_rutas = pd.read_csv(CALENDARIO_RUTAS_FILE)
    df_cal_rutas = df_cal_rutas[df_cal_rutas["Fecha"].isin(rango_fechas_viaje)].copy()
    df_cal_rutas["Notas del Día"] = df_cal_rutas["Notas del Día"].fillna("").astype(str)

# --- CONFIGURACIÓN DE ESTILOS ---
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

# --- MENÚ LATERAL ---
st.sidebar.markdown("# ✈️ Euro-Tour 2027")
seleccion = st.sidebar.radio("Ir a la sección:", ["📊 Tablero y Finanzas", "🗓️ Ruta País 2027", "🏨 Alojamientos y Links", "🗺️ Itinerario x Horas", "💰 Gastos Personales", "🎒 Check-list de Maleta"])

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
                    df_global = pd.read_csv(GASTOS_FILE)
                    df_final = pd.concat([df_global, nuevo_g], ignore_index=True)
                    df_final.to_csv(GASTOS_FILE, index=False)
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
                    df_global = pd.read_csv(GASTOS_FILE)
                    fila_clonar = df_global[(df_global["Persona"] == p_nombre) & ((df_global["Concepto / Ítem"].astype(str) + " ($" + df_global["Costo ($)"].astype(str) + ")") == gasto_origen)].copy()
                    if not fila_clonar.empty:
                        fila_clonar["Persona"] = persona_destino
                        df_final = pd.concat([df_global, fila_clonar], ignore_index=True)
                        df_final.to_csv(GASTOS_FILE, index=False)
                        st.success(f"¡Gasto copiado!")
                        st.rerun()
            with c_btn2:
                if st.button("➡️ Mover Gasto", key=f"btn_move_v23_{p_nombre}", use_container_width=True):
                    df_global = pd.read_csv(GASTOS_FILE)
                    indices = df_global[(df_global["Persona"] == p_nombre) & ((df_global["Concepto / Ítem"].astype(str) + " ($" + df_global["Costo ($)"].astype(str) + ")") == gasto_origen)].index
                    if len(indices) > 0:
                        df_global.at[indices[0], "Persona"] = persona_destino
                        df_global.to_csv(GASTOS_FILE, index=False)
                        st.warning(f"¡Gasto movido!")
                        st.rerun()
        else:
            st.info("Sin gastos que transferir.")

    st.markdown("---")
    col_eliminar, col_tabla = st.columns([1, 2])
    with col_eliminar:
        st.markdown("##### 🗑️ Eliminar Registro")
        if not df_p.empty:
            df_p["ID_Combo"] = df_p["Concepto / Ítem"].astype(str) + " ($" + df_p["Costo ($)"].astype(str) + ")"
            gasto_baja = st.selectbox("Seleccione transacción a borrar:", df_p["ID_Combo"].values, key=f"baja_v23_{p_nombre}")
            if st.button("❌ Eliminar Transacción", type="primary", use_container_width=True, key=f"btn_baja_v23_{p_nombre}"):
                df_global = pd.read_csv(GASTOS_FILE)
                df_global = df_global[~((df_global["Persona"] == p_nombre) & ((df_global["Concepto / Ítem"].astype(str) + " ($" + df_global["Costo ($)"].astype(str) + ")") == gasto_baja))]
                df_global.to_csv(GASTOS_FILE, index=False)
                st.warning("Gasto borrado.")
                st.rerun()
        else:
            st.caption("No hay elementos para eliminar.")

    with col_tabla:
        st.markdown("##### 📋 Tabla de Modificación Rápida")
        if not df_p.empty:
            df_mostrar_p = df_p[["Fecha", "Concepto / Ítem", "Categoría", "Ciudad", "Costo ($)"]].copy()
            df_editado_persona = st.data_editor(df_mostrar_p, column_config=CONFIG_COLUMNA_GASTOS, num_rows="dynamic", use_container_width=True, hide_index=True, key=f"tabla_v23_{p_nombre}")
            
            if st.button("💾 Guardar Cambios Manuales", key=f"btn_save_v23_{p_nombre}", use_container_width=True):
                df_editado_persona["Persona"] = p_nombre
                df_global = pd.read_csv(GASTOS_FILE)
                df_otros = df_global[df_global["Persona"] != p_nombre]
                df_final = pd.concat([df_otros, df_editado_persona], ignore_index=True)
                df_final.to_csv(GASTOS_FILE, index=False)
                st.success("¡Datos actualizados!")
                st.rerun()

# --- RECTAS DE RENDERIZADO POR PÁGINA ---
if seleccion == "📊 Tablero y Finanzas":
    st.title("📊 Resumen General del Viaje (2027)")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("💰 Costo Total Acumulado del Viaje", f"${df_gastos['Costo ($)'].sum():,.0f}" if not df_gastos.empty else "$0")
    kpi2.metric("🏨 Total en Alojamientos", f"${df_gastos[df_gastos['Categoría'] == 'Alojamiento']['Costo ($)'].sum():,.0f}" if not df_gastos.empty else "$0")
    kpi3.metric("📍 Eventos en Itinerario", f"{len(df_itinerario)} hitos")
    
    st.markdown("---")
    st.subheader("👤 Resumen Financiero por Integrante")
    resumen_personas = [{"Integrante": p, "Total Gastado ($)": df_gastos[df_gastos["Persona"] == p]["Costo ($)"].sum() if not df_gastos.empty else 0} for p in INTEGRANTES]
    df_resumen_p = pd.DataFrame(resumen_personas)
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1: st.dataframe(df_resumen_p, use_container_width=True, hide_index=True)
    with col_t2: st.bar_chart(data=df_resumen_p, x="Integrante", y="Total Gastado ($)", use_container_width=True)

elif seleccion == "🗓️ Ruta País 2027":
    st.title("🗓️ Calendario de Ubicación Geográfica - Verano 2027")
    col_izq, col_der = st.columns([4, 5])
    with col_izq:
        df_cal_editado = st.data_editor(df_cal_rutas, column_config=CONFIG_COLUMNA_RUTA, use_container_width=True, hide_index=True, key="editor_ruta_pais_v22")
        if st.button("💾 Sincronizar e Imprimir Cambios", type="primary", use_container_width=True):
            df_cal_editado.to_csv(CALENDARIO_RUTAS_FILE, index=False)
            st.success("¡Calendario actualizado!")
            st.rerun()
    with col_der:
        for fila in df_cal_rutas.itertuples(index=False):
            notas_limpias = f" — {fila[3]}" if str(fila[3]).strip() and str(fila[3]) != "nan" else ""
            etiqueta = f"📅 {fila[0]} ({fila[1]}) ➔ {fila[2]}{notas_limpias}"
            if "Santiago" in str(fila[2]): st.info(etiqueta)
            elif "París" in str(fila[2]) or "Paris" in str(fila[2]): st.error(etiqueta)
            elif "Venecia" in str(fila[2]): st.success(etiqueta)
            elif "Roma" in str(fila[2]): st.warning(etiqueta)
            else: st.info(etiqueta)

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
                    nuevo_al = pd.DataFrame([[pais_al, nombre_al, checkin.strftime("%Y-%m-%d"), checkout.strftime("%Y-%m-%d"), link_bk]], columns=df_alojamientos.columns)
                    pd.concat([df_alojamientos, nuevo_al], ignore_index=True).to_csv(ALOJAMIENTOS_FILE, index=False)
                    st.success("¡Guardado!")
                    st.rerun()
    with c_al2:
        if not df_alojamientos.empty:
            al_borrar = st.selectbox("Selecciona para remover:", df_alojamientos["Nombre del Alojamiento"].values)
            if st.button("❌ Eliminar Alojamiento", type="primary", use_container_width=True):
                df_alojamientos[df_alojamientos["Nombre del Alojamiento"] != al_borrar].to_csv(ALOJAMIENTOS_FILE, index=False)
                st.rerun()
    if not df_alojamientos.empty: st.data_editor(df_alojamientos, column_config=CONFIG_COLUMNA_ALOJAMIENTOS, use_container_width=True, hide_index=True)

elif seleccion == "🗺️ Itinerario x Horas":
    st.title("🗺️ Cronograma de Actividades por Horas")
    col_add, col_del = st.columns([1.2, 1.8])
    with col_add:
        with st.form("form_itinerario", clear_on_submit=True):
            fecha_evento = st.date_input("Fecha")
            hora_evento = st.time_input("Hora")
            ciudad_evento = st.selectbox("Ciudad", CIUDADES)
            actividad = st.text_input("Actividad").strip()
            lugar = st.text_input("Dirección").strip()
            reserva = st.text_input("Notas / Reserva").strip()
            if st.form_submit_button("💾 Guardar Hito"):
                if actividad:
                    f_str = fecha_evento.strftime("%Y-%m-%d")
                    nuevo_evento = pd.DataFrame([[f_str, hora_evento.strftime("%H:%M"), ciudad_evento, actividad, lugar, reserva]], columns=df_itinerario.columns)
                    pd.concat([df_itinerario, nuevo_evento], ignore_index=True).to_csv(ITINERARIO_FILE, index=False)
                    st.success("¡Hito guardado!")
                    st.rerun()
    with col_del:
        if not df_itinerario.empty:
            df_itinerario["ID_Temp"] = df_itinerario["Fecha"] + " (" + df_itinerario["Hora"] + ") - " + df_itinerario["Actividad"]
            evento_borrar = st.selectbox("Selecciona hito a borrar:", df_itinerario["ID_Temp"].values)
            if st.button("❌ Quitar de la Lista", type="primary", use_container_width=True):
                df_itinerario[df_itinerario["ID_Temp"] != evento_borrar].drop(columns=["ID_Temp"], errors="ignore").to_csv(ITINERARIO_FILE, index=False)
                st.rerun()
    if not df_itinerario.empty:
        df_itinerario = df_itinerario.sort_values(by=["Fecha", "Hora"])
        st.data_editor(df_itinerario, column_config=CONFIG_COLUMNA_ITINERARIO, use_container_width=True, hide_index=True)

elif seleccion == "💰 Gastos Personales":
    st.title("💰 Control de Cuentas por Integrante")
    tabs = st.tabs([f"👤 {p}" for p in INTEGRANTES])
    for idx, p in enumerate(INTEGRANTES):
        with tabs[idx]: renderizar_pestaña_persona(p)
    if not df_gastos.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_gastos.to_excel(writer, index=False, sheet_name='Cuentas')
        st.download_button(label="📥 Descargar Reporte en Excel (.xlsx)", data=output.getvalue(), file_name="Presupuesto_Viaje_2027.xlsx", type="primary")

elif seleccion == "🎒 Check-list de Maleta":
    st.title("🎒 Maleta Virtual Colectiva y Tareas")
    col_ins, col_rem = st.columns([2, 1])
    with col_ins:
        with st.form("form_nueva_tarea_v22", clear_on_submit=True):
            cat_nueva = st.selectbox("Bloque / Sección", ["📋 Documentación Crítica", "📦 Cosas de Equipaje"])
            texto_nuevo = st.text_input("¿Qué necesitas recordar o empacar?").strip()
            if st.form_submit_button("零部件 Registrar Tarea"):
                if texto_nuevo:
                    pd.concat([df_checklist, pd.DataFrame([{"Categoría": cat_nueva, "Tarea": texto_nuevo, "Hecho": False}])], ignore_index=True).to_csv(CHECKLIST_FILE, index=False)
                    st.rerun()
    with col_rem:
        if not df_checklist.empty:
            tarea_a_borrar = st.selectbox("Selecciona qué quitar:", df_checklist["Tarea"].values)
            if st.button("❌ Borrar Definitivamente", type="primary", use_container_width=True):
                df_checklist[df_checklist["Tarea"] != tarea_a_borrar].to_csv(CHECKLIST_FILE, index=False)
                st.rerun()
    if not df_checklist.empty:
        df_checklist_editado = st.data_editor(df_checklist, column_config=CONFIG_COLUMNA_CHECKLIST, use_container_width=True, hide_index=True, key="editor_checklist_maestro_v22")
        if df_checklist_editado is not None: df_checklist_editado.to_csv(CHECKLIST_FILE, index=False)
