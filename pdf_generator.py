from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import os
from datetime import timedelta
from rotacion import corregir_horario


def generar_pdf_multiple(semanas_data, nombre_archivo="programacion_completa.pdf"):
    ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads", nombre_archivo)
    doc = SimpleDocTemplate(ruta_descargas, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    for semana_info in semanas_data:
        semana = semana_info["semana"]
        fecha_inicio = semana_info["fecha_inicio"]
        fecha_fin = semana_info["fecha_fin"]
        turnos = semana_info["turnos"]
        supervisores_ehs = semana_info["supervisores_ehs"]
        nota_festivo = semana_info.get("nota_festivo", "")
        inicia_en_martes = fecha_inicio.weekday() == 1

        # 🗓️ Título
        titulo = Paragraph(
            f"<b>SEMANA {semana}</b><br/>{fecha_inicio.strftime('%d/%m/%Y')} – {fecha_fin.strftime('%d/%m/%Y')}"
            + (f"<br/><i>{nota_festivo}</i>" if nota_festivo else ""),
            estilos["Title"]
        )
        elementos.append(titulo)
        elementos.append(Spacer(1, 20))

        # 👷 Técnicos
        elementos.append(Paragraph("👷 Rotación de Técnicos", estilos["Heading2"]))
        datos_tecnicos = [["Cuadrilla", "Horario", "Personal Técnico"]]
        turno_festivo = None
        turnos_normales = []

        for asignacion in turnos:
            if asignacion["cuadrilla"] == "Correctivos Lunes Festivo":
                turno_festivo = asignacion
            else:
                turnos_normales.append(asignacion)

        for asignacion in turnos_normales:
            horario = asignacion["horario"]
            horario = corregir_horario(horario, inicia_en_martes)

            datos_tecnicos.append([
                f"{asignacion['cuadrilla']}\n{asignacion['vehiculo']}",
                horario,
                ", ".join(asignacion["tecnicos"])
            ])

        if turno_festivo:
            horario = turno_festivo["horario"]
            horario = corregir_horario(horario, inicia_en_martes)

            datos_tecnicos.append([
                f"{turno_festivo['cuadrilla']}\n{turno_festivo['vehiculo']}",
                horario,
                ", ".join(turno_festivo["tecnicos"])
            ])

        tabla_tecnicos = Table(datos_tecnicos, colWidths=[150, 180, 170])
        tabla_tecnicos.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elementos.append(tabla_tecnicos)
        elementos.append(Spacer(1, 30))

        # 🛡️ Supervisores SST
        elementos.append(Paragraph("🛡️ Supervisión SST", estilos["Heading2"]))
        datos_ehs = [["Horario", "Supervisor SST"]]
        turno_festivo_ehs = None
        supervisores_ehs_normales = []

        for asignacion in supervisores_ehs:
            if "Lunes Festivo" in asignacion["horario"]:
                turno_festivo_ehs = asignacion
            else:
                supervisores_ehs_normales.append(asignacion)

        for asignacion in supervisores_ehs_normales:
            horario = asignacion["horario"]
            horario = corregir_horario(horario, inicia_en_martes)

            datos_ehs.append([
                horario,
                ", ".join(asignacion["supervisor"])
            ])

        if turno_festivo_ehs:
            horario = turno_festivo_ehs["horario"]
            horario = corregir_horario(horario, inicia_en_martes)

            datos_ehs.append([
                horario,
                ", ".join(turno_festivo_ehs["supervisor"])
            ])

        tabla_ehs = Table(datos_ehs, colWidths=[200, 300])
        tabla_ehs.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2 if turno_festivo_ehs else -1), [colors.beige, colors.lightgrey]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        if turno_festivo_ehs:
            tabla_ehs.setStyle(TableStyle([
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightcoral),
                ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]))

        elementos.append(tabla_ehs)
        elementos.append(PageBreak())

    doc.build(elementos)
    return ruta_descargas




def generar_pdf(turnos, semana, fecha_inicio, fecha_fin, supervisores_ehs, nota_festivo=""):
   
    nombre_archivo = f"turnos_semana_{semana}_{fecha_inicio.strftime('%Y-%m-%d')}.pdf"
    ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads", nombre_archivo)
    doc = SimpleDocTemplate(ruta_descargas, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()
    inicia_en_martes = fecha_inicio.weekday() == 1

    # 🗓️ Título
    titulo = Paragraph(
        f"<b>SEMANA {semana}</b><br/>{fecha_inicio.strftime('%d/%m/%Y')} – {fecha_fin.strftime('%d/%m/%Y')}"
        + (f"<br/><i>{nota_festivo}</i>" if nota_festivo else ""),
        estilos["Title"]
    )
    elementos.append(titulo)
    elementos.append(Spacer(1, 20))

    # 👷 Técnicos
    elementos.append(Paragraph("👷 Rotación de Técnicos", estilos["Heading2"]))
    datos_tecnicos = [["Cuadrilla", "Horario", "Personal Técnico"]]
    turno_festivo = None
    turnos_normales = []

    for asignacion in turnos:
        if asignacion["cuadrilla"] == "Correctivos Lunes Festivo":
            turno_festivo = asignacion
        else:
            turnos_normales.append(asignacion)

    for asignacion in turnos_normales:
        horario = asignacion["horario"]
        horario = corregir_horario(horario, inicia_en_martes)

        datos_tecnicos.append([
            f"{asignacion['cuadrilla']}\n{asignacion['vehiculo']}",
            horario,
            ", ".join(asignacion["tecnicos"])
        ])

    if turno_festivo:
        horario = turno_festivo["horario"]
        horario = corregir_horario(horario, inicia_en_martes)

        datos_tecnicos.append([
            f"{turno_festivo['cuadrilla']}\n{turno_festivo['vehiculo']}",
            horario,
            ", ".join(turno_festivo["tecnicos"])
        ])

    tabla_tecnicos = Table(datos_tecnicos, colWidths=[150, 180, 170])
    tabla_tecnicos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elementos.append(tabla_tecnicos)
    elementos.append(Spacer(1, 30))

    # 🛡️ Supervisores SST
    elementos.append(Paragraph("🛡️ Supervisión SST", estilos["Heading2"]))
    datos_ehs = [["Horario", "Supervisor SST"]]
    turno_festivo_ehs = None
    supervisores_ehs_normales = []

    for asignacion in supervisores_ehs:
        if "Lunes Festivo" in asignacion["horario"]:
            turno_festivo_ehs = asignacion
        else:
            supervisores_ehs_normales.append(asignacion)

    for asignacion in supervisores_ehs_normales:
        horario = asignacion["horario"]
        horario = corregir_horario(horario, inicia_en_martes)

        datos_ehs.append([
            horario,
            ", ".join(asignacion["supervisor"])
        ])

    if turno_festivo_ehs:
        horario = turno_festivo_ehs["horario"]
        horario = corregir_horario(horario, inicia_en_martes)

        datos_ehs.append([
            horario,
            ", ".join(turno_festivo_ehs["supervisor"])
        ])

    tabla_ehs = Table(datos_ehs, colWidths=[200, 300])
    tabla_ehs.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2 if turno_festivo_ehs else -1), [colors.beige, colors.lightgrey]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    if turno_festivo_ehs:
        tabla_ehs.setStyle(TableStyle([
            ("BACKGROUND", (0, -1), (-1, -1), colors.lightcoral),
            ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ]))

    elementos.append(tabla_ehs)
    doc.build(elementos)
    return ruta_descargas
