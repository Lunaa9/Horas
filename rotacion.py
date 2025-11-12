import json
from datetime import date, timedelta
import holidays

CO_HOLIDAYS = holidays.Colombia()

CUADRILLAS = [
    {"nombre": "Correctivos 1", "vehiculo": "WFR 538", "horario": "06:00 - 14:00 Lun-Sab"},
    {"nombre": "Correctivos 2", "vehiculo": "LSY 026", "horario": "10:00 - 19:00 Lun-Sab"},
    {"nombre": "Correctivos 3", "vehiculo": "WFR 538", "horario": "13:00 - 22:00 Lun-Sab"},
    {"nombre": "Correctivos 4", "vehiculo": "LQO 596", "horario": "13:30 - 21:00 Lun-Sab"},
    {"nombre": "Correctivos 5", "vehiculo": "LSY 026", "horario": "21:00 - 06:00 Dom-Vie"},
    {"nombre": "Domingo",        "vehiculo": "LSY 026", "horario": "08:00 - 18:00 Domingo"}
]
SUPERVISORES = [
    ["Nathaly Mendivelso"],
    ["Andres Bautista"],
    ["Oscar Roa"]
]

HORARIOS_EHS = [
    {"horario": "Lun - Sab 06:00 - 14:00", "tipo": "rotativo"},
    {"horario": "Lun - Sab 13:00 - 22:00", "tipo": "rotativo"},
    {"horario": "Dom - Vie 21:00 - 06:00", "tipo": "rotativo"},
    {"horario": "Administrativo", "tipo": "fijo", "supervisor": ["Jeimy Pachon"]},
    {"horario": "Domingo 08:00 - 18:00", "tipo": "dinámico"}  # lo hace el del primer turno
]


def cargar_parejas():
    with open("data/parejas.json") as f:
        return json.load(f)

def generar_turnos(fecha_base):
    parejas = cargar_parejas()
    fecha_lunes = normalizar_a_lunes(fecha_base)
    asignaciones = []

    # Detectar si hay lunes festivo en esta semana
    lunes_festivo = lunes_festivo_en_semana(fecha_lunes)
    agregar_festivo = lunes_festivo and fecha_base == fecha_lunes

    # Calcular semana y rotar parejas en cadena
    semanas = semanas_desde_inicio(fecha_lunes)
    offset = semanas % len(parejas)
    parejas_rotadas = parejas[-offset:] + parejas[:-offset]


    # Asignar a cuadrillas 1 a 5
    cuadrillas_rotativas = [c for c in CUADRILLAS if c["nombre"].startswith("Correctivos")]
    inicia_en_martes = fecha_base.weekday() == 1

    for i, cuadrilla in enumerate(cuadrillas_rotativas):
        horario = corregir_horario(cuadrilla["horario"], inicia_en_martes)
        asignaciones.append({
            "cuadrilla": cuadrilla["nombre"],
            "vehiculo": cuadrilla["vehiculo"],
            "horario": horario,
            "tecnicos": parejas_rotadas[i % len(parejas_rotadas)]
        })


    # Asignar Domingo al técnico del Correctivo 2
    correctivo_2 = next((a for a in asignaciones if a["cuadrilla"] == "Correctivos 2"), None)
    if correctivo_2:
        horario_domingo = corregir_horario("08:00 - 18:00 Domingo", inicia_en_martes)
        asignaciones.append({
            "cuadrilla": "Domingo",
            "vehiculo": "LSY 026",
            "horario": horario_domingo,
            "tecnicos": correctivo_2["tecnicos"]
        })

    if lunes_festivo and agregar_festivo and correctivo_2:
        horario_festivo = corregir_horario("Lunes Festivo 08:00 - 18:00", inicia_en_martes)
        asignaciones.insert(0, {
            "cuadrilla": "Correctivos Lunes Festivo",
            "vehiculo": correctivo_2["vehiculo"],
            "horario": horario_festivo,
            "tecnicos": correctivo_2["tecnicos"]
        })



    return asignaciones


def es_lunes_festivo(fecha):
    fecha_lunes = normalizar_a_lunes(fecha)
    return fecha_lunes in CO_HOLIDAYS

def lunes_festivo_en_semana(fecha_lunes):
    for i in range(8):  # incluye el lunes siguiente
        dia = fecha_lunes + timedelta(days=i)
        if dia.weekday() == 0 and es_lunes_festivo(dia):
            return dia
    return None





def guardar_rotacion(fecha, asignaciones):
    try:
        with open("data/rotaciones.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    fecha_lunes = normalizar_a_lunes(fecha)
    clave = fecha_lunes.strftime("%Y-%m-%d")
    data[clave] = asignaciones

    with open("data/rotaciones.json", "w") as f:
        json.dump(data, f, indent=2)


def cargar_rotacion(fecha):
    try:
        with open("data/rotaciones.json") as f:
            data = json.load(f)
            return data.get(fecha.strftime("%Y-%m-%d"))
    except FileNotFoundError:
        return None


def semanas_desde_inicio(fecha, inicio=date(2025, 10, 14)):
    return ((fecha - inicio).days // 7) + 3  # semana del 20 es la 3


def generar_ehs(fecha_base):
    fecha_lunes_real = normalizar_a_lunes(fecha_base)
    lunes_festivo = lunes_festivo_en_semana(fecha_lunes_real)

    # La rotación se calcula desde el lunes real, no desde martes
    semanas_transcurridas = semanas_desde_inicio(fecha_lunes_real)
    asignaciones = []

    
    orden_base = [SUPERVISORES[0], SUPERVISORES[1], SUPERVISORES[2]]  # Nathaly, Andrés, Oscar
    offset = semanas_transcurridas % 3
    rotados = orden_base[-offset:] + orden_base[:-offset]  # rotación izquierda

    supervisor_1 = rotados[0]  # turno 1
    supervisor_2 = rotados[1]  # turno 2
    supervisor_3 = rotados[2]  # turno 3


    # Turnos rotativos
    asignaciones.append({
        "horario": "Lun - Sab 06:00 - 14:00",
        "supervisor": supervisor_1
    })
    asignaciones.append({
        "horario": "Lun - Sab 13:00 - 22:00",
        "supervisor": supervisor_2
    })
    asignaciones.append({
        "horario": "Dom - Vie 21:00 - 06:00",
        "supervisor": supervisor_3
    })

    # Fijo
    asignaciones.append({
        "horario": "Administrativo",
        "supervisor": ["Jeimy Pachon"]
    })

    # Dinámico (domingo) → lo hace el del primer turno
    asignaciones.append({
        "horario": "Domingo 08:00 - 18:00",
        "supervisor": supervisor_1
    })

    # Festivo → también lo hace el del primer turno
    if lunes_festivo and fecha_base == fecha_lunes_real:
        asignaciones.insert(0, {
            "horario": "Lunes Festivo 08:00 - 18:00",
            "supervisor": supervisor_1
        })

    return asignaciones





def guardar_rotacion_ehs(fecha, asignaciones):
    try:
        with open("data/rotacion_ehs.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    fecha_lunes = normalizar_a_lunes(fecha)
    clave = fecha_lunes.strftime("%Y-%m-%d")
    data[clave] = asignaciones

    with open("data/rotacion_ehs.json", "w") as f:
        json.dump(data, f, indent=2)

def cargar_rotacion_ehs(fecha):
    try:
        with open("data/rotacion_ehs.json") as f:
            data = json.load(f)
            return data.get(normalizar_a_lunes(fecha).strftime("%Y-%m-%d"))
    except FileNotFoundError:
        return None


def normalizar_a_lunes(fecha):
    return fecha - timedelta(days=fecha.weekday())


def corregir_horario(horario, inicia_en_martes):
    if not inicia_en_martes:
        return horario

    # Reemplazar rangos de días si la semana empieza en martes
    # Lun - Sab → Mar - Sab
    if "Lun - Sab" in horario:
        horario = horario.replace("Lun - Sab", "Mar - Sab")
    elif "Lun-Sab" in horario:
        horario = horario.replace("Lun-Sab", "Mar-Sab")

    # Dom - Vie → Lun - Vie
    if "Dom - Vie" in horario:
        horario = horario.replace("Dom - Vie", "Lun - Vie")
    elif "Dom-Vie" in horario:
        horario = horario.replace("Dom-Vie", "Lun-Vie")

    return horario













 