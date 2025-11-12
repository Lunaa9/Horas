import streamlit as st
from datetime import date, timedelta
from rotacion import (
    generar_turnos,
    guardar_rotacion,
    cargar_rotacion,
    generar_ehs,
    guardar_rotacion_ehs,
    cargar_rotacion_ehs,
    normalizar_a_lunes,
    es_lunes_festivo,
    lunes_festivo_en_semana,
    semanas_desde_inicio
)
from pdf_generator import generar_pdf, generar_pdf_multiple
from rotacion import corregir_horario

# Configuración de la página
st.set_page_config(page_title="Rotación de Técnicos", layout="wide")
st.title("📅 Rotación de Técnicos por Semana")

# Selección de fecha
fecha = st.date_input("Selecciona una fecha", value=date.today())

# 🔁 Normalizar a lunes
fecha_lunes = normalizar_a_lunes(fecha)
lunes_festivo = lunes_festivo_en_semana(fecha_lunes)

# Caso 1: el día seleccionado es un lunes festivo → mostrar semana anterior
if fecha.weekday() == 0 and es_lunes_festivo(fecha):
    fecha_lunes = fecha_lunes - timedelta(days=7)
    lunes_festivo = lunes_festivo_en_semana(fecha_lunes)

# Caso 2: si el lunes anterior fue festivo y estamos en martes o más → nueva semana desde martes
if fecha.weekday() >= 1 and es_lunes_festivo(fecha_lunes):
    fecha_inicio = fecha_lunes + timedelta(days=1)  # martes
    fecha_fin = fecha_inicio + timedelta(days=5)    # hasta domingo
    clave_rotacion = fecha_inicio
    festivo_texto = ""
else:
    # Semana normal o semana que termina en lunes festivo
    fecha_inicio = fecha_lunes
    fecha_fin = lunes_festivo if lunes_festivo else fecha_lunes + timedelta(days=6)
    clave_rotacion = fecha_lunes
    festivo_texto = f"" if lunes_festivo else ""




# 🔧 Técnicos
rotacion = cargar_rotacion(clave_rotacion)
if rotacion:
    turnos = rotacion
else:
    turnos = generar_turnos(clave_rotacion)
    guardar_rotacion(clave_rotacion, turnos)

# 🔧 Supervisores SST
rotacion_ehs = cargar_rotacion_ehs(clave_rotacion)
if rotacion_ehs:
    supervisores = rotacion_ehs
else:
    supervisores = generar_ehs(clave_rotacion)
    guardar_rotacion_ehs(clave_rotacion, supervisores)

# 🗓️ Encabezado de semana
semana = semanas_desde_inicio(fecha_inicio)
st.markdown(f"### SEMANA {semana}{festivo_texto} — {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}")



inicia_en_martes = clave_rotacion.weekday() == 1

# 👷 Técnicos
st.markdown("### 👷 Rotación de Técnicos")
for asignacion in turnos:
    horario = corregir_horario(asignacion["horario"], inicia_en_martes)
    st.markdown(f"""
    <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px">
      <strong>{asignacion['cuadrilla']}</strong><br>
      <em>{asignacion['vehiculo']}</em> — <span>{horario}</span><br>
      <strong>Personal Técnico:</strong> {', '.join(asignacion['tecnicos'])}
    </div>
    """, unsafe_allow_html=True)



# 🛡️ Supervisores SST

supervisores_festivo = []
supervisores_normales = []

for asignacion in supervisores:
    horario = corregir_horario(asignacion["horario"], inicia_en_martes)
    if "Lunes Festivo" in horario:
        supervisores_festivo.append(asignacion)
    else:
        supervisores_normales.append(asignacion)

inicia_en_martes = clave_rotacion.weekday() == 1

# 🛡️ Supervisores SST
st.markdown("### 🛡️ Supervisión SST")

for asignacion in supervisores_normales:
    horario = corregir_horario(asignacion["horario"], inicia_en_martes)

    st.markdown(f"""
    <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px">
      <strong>{horario}</strong><br>
      <strong>Supervisor SST:</strong> {', '.join(asignacion['supervisor'])}
    </div>
    """, unsafe_allow_html=True)

for asignacion in supervisores_festivo:
    horario = corregir_horario(asignacion["horario"], inicia_en_martes)

    st.markdown(f"""
    <div style="border:2px solid #d9534f; background-color:#f9d6d5; padding:10px; margin-bottom:10px">
      <strong style="color:#d9534f">{horario}</strong><br>
      <strong>Supervisor SST:</strong> {', '.join(asignacion['supervisor'])}
    </div>
    """, unsafe_allow_html=True)



# 📄 PDF con técnicos y EHS
# 📄 Botón para descargar semana actual
if st.button("📄 Descargar semana actual"):
    ruta = generar_pdf(turnos, semana, fecha_inicio, fecha_fin, supervisores)
    st.success(f"PDF guardado en: {ruta}")


if st.button("📆 Descargar programación completa"):
    semanas_data = []
    base = normalizar_a_lunes(fecha)

    for i in range(9):  # 8 semanas ≈ 2 meses
        fecha_lunes = base + timedelta(weeks=i)
        lunes_festivo = lunes_festivo_en_semana(fecha_lunes)

        # ¿Hay festivo en este lunes?
        hay_festivo = es_lunes_festivo(fecha_lunes)

        # ¿La semana debe comenzar en martes?
        comenzar_en_martes = hay_festivo

        if comenzar_en_martes:
            fecha_inicio_semana = fecha_lunes + timedelta(days=1)  # martes
            fecha_fin_semana = fecha_inicio_semana + timedelta(days=5)  # domingo
            clave_rotacion = fecha_inicio_semana
            nota_festivo = ""  # no se marca como festivo
        else:
            fecha_inicio_semana = fecha_lunes
            fecha_fin_semana = fecha_lunes + timedelta(days=7)
            clave_rotacion = fecha_lunes
            nota_festivo = "■ Semana con festivo" if hay_festivo else ""

        semana_num = semanas_desde_inicio(fecha_lunes)
        turnos_semana = generar_turnos(clave_rotacion)
        supervisores_semana = generar_ehs(clave_rotacion)

        semanas_data.append({
            "semana": semana_num,
            "fecha_inicio": fecha_inicio_semana,
            "fecha_fin": fecha_fin_semana,
            "turnos": turnos_semana,
            "supervisores_ehs": supervisores_semana,
            "nota_festivo": nota_festivo
        })

    ruta = generar_pdf_multiple(semanas_data)
    st.success(f"PDF completo guardado en: {ruta}")
