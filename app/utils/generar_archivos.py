
from io import BytesIO
from datetime import date, datetime
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


# =====================================================
# CONVERTIR VALORES
# =====================================================

def convertir_valor(valor):
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d/%m/%Y")

    if valor is None:
        return ""

    return str(valor)


# =====================================================
# PIE DE PAGINA DEL PDF
# =====================================================

def agregar_pie_pagina(canvas, documento):
    canvas.saveState()

    ancho, alto = documento.pagesize

    canvas.setStrokeColor(colors.HexColor("#237A45"))
    canvas.setLineWidth(0.8)
    canvas.line(30, 28, ancho - 30, 28)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))

    canvas.drawString(
        30,
        16,
        "Institución Universitaria CUL - Carga Docente y Autoevaluación"
    )

    canvas.drawRightString(
        ancho - 30,
        16,
        f"Página {documento.page}"
    )

    canvas.restoreState()


# =====================================================
# GENERAR PDF
# =====================================================

def generar_pdf(datos, titulo, columnas):

    archivo = BytesIO()

    documento = SimpleDocTemplate(
        archivo,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=35,
        bottomMargin=45
    )

    estilos = getSampleStyleSheet()

    encabezado = ParagraphStyle(
        "EncabezadoCUL",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#237A45"),
        fontSize=16,
        spaceAfter=5
    )

    subtitulo = ParagraphStyle(
        "SubtituloCUL",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor("#555555")
    )

    elementos = []

    # Ruta del logo: app/img/logo_cul.png
    ruta_logo = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "img",
            "logo_cul.png"
        )
    )

    # ENCABEZADO CON LOGO
    if os.path.exists(ruta_logo):

        logo = Image(
            ruta_logo,
            width=2.5 * cm,
            height=2.5 * cm,
            kind="proportional"
        )

        contenido_encabezado = [
            [
                logo,
                Paragraph(
                    "INSTITUCIÓN UNIVERSITARIA CUL<br/>"
                    "CARGA DOCENTE Y EVALUACIÓN DE DESEMPEÑO",
                    encabezado
                )
            ]
        ]

        tabla_encabezado = Table(
            contenido_encabezado,
            colWidths=[3 * cm, 22 * cm]
        )

        tabla_encabezado.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10)
        ]))

        elementos.append(tabla_encabezado)

    else:

        elementos.append(
            Paragraph(
                "INSTITUCIÓN UNIVERSITARIA CUL<br/>"
                "CARGA DOCENTE Y EVALUACIÓN DE DESEMPEÑO",
                encabezado
            )
        )

    elementos.append(Spacer(1, 10))

    # TITULO DEL REPORTE
    elementos.append(
        Paragraph(titulo, estilos["Heading2"])
    )

    # FECHA DE GENERACION
    elementos.append(
        Paragraph(
            f"Fecha de generación: "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
            subtitulo
        )
    )

    elementos.append(Spacer(1, 20))

    # PREPARAR DATOS
    tabla_datos = [columnas]

    for registro in datos:

        fila = [
            convertir_valor(registro.get(columna))
            for columna in columnas
        ]

        tabla_datos.append(fila)

    # MENSAJE SI NO HAY REGISTROS
    if not datos:
        tabla_datos.append(["No se encontraron registros"] + [""] * (len(columnas) - 1))

    # CREAR TABLA
    tabla = Table(
        tabla_datos,
        repeatRows=1,
        hAlign="LEFT"
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#237A45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F0F5F1")
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))

    elementos.append(tabla)

    elementos.append(Spacer(1, 15))

    # TOTAL DE REGISTROS
    elementos.append(
        Paragraph(
            f"Total de registros: {len(datos)}",
            estilos["Normal"]
        )
    )

    # GENERAR PDF CON PIE DE PAGINA
    documento.build(
        elementos,
        onFirstPage=agregar_pie_pagina,
        onLaterPages=agregar_pie_pagina
    )

    archivo.seek(0)

    return archivo


# =====================================================
# GENERAR EXCEL
# =====================================================

def generar_excel(datos, titulo, columnas):

    archivo = BytesIO()

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Reporte"

    # TITULO
    hoja.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=len(columnas)
    )

    titulo_celda = hoja.cell(row=1, column=1)
    titulo_celda.value = titulo
    titulo_celda.font = Font(
        bold=True,
        size=16,
        color="FFFFFF"
    )

    titulo_celda.fill = PatternFill(
        "solid",
        fgColor="237A45"
    )

    titulo_celda.alignment = Alignment(horizontal="center")

    # FECHA DE GENERACION
    hoja.merge_cells(
        start_row=2,
        start_column=1,
        end_row=2,
        end_column=len(columnas)
    )

    hoja.cell(row=2, column=1).value = (
        "Fecha de generación: "
        + datetime.now().strftime("%d/%m/%Y %H:%M")
    )

    # ENCABEZADOS DE COLUMNAS
    for numero, columna in enumerate(columnas, start=1):

        celda = hoja.cell(row=4, column=numero)

        celda.value = columna.replace("_", " ").title()

        celda.font = Font(
            bold=True,
            color="FFFFFF"
        )

        celda.fill = PatternFill(
            "solid",
            fgColor="237A45"
        )

        celda.alignment = Alignment(horizontal="center")

    # DATOS
    for fila_numero, registro in enumerate(datos, start=5):

        for columna_numero, columna in enumerate(columnas, start=1):

            celda = hoja.cell(
                row=fila_numero,
                column=columna_numero
            )

            celda.value = convertir_valor(
                registro.get(columna)
            )

            celda.alignment = Alignment(vertical="center")

    # FILA FINAL
    ultima_fila = 4 + len(datos)

    # FILTROS DE EXCEL
    if datos:

        hoja.auto_filter.ref = (
            f"A4:{get_column_letter(len(columnas))}{ultima_fila}"
        )

    # FIJAR ENCABEZADOS
    hoja.freeze_panes = "A5"

    # AJUSTAR ANCHO DE COLUMNAS
    for numero, columna in enumerate(columnas, start=1):

        valores = [
            str(hoja.cell(row=fila, column=numero).value or "")
            for fila in range(4, ultima_fila + 1)
        ]

        ancho = max([len(valor) for valor in valores] + [12])

        hoja.column_dimensions[
            get_column_letter(numero)
        ].width = min(ancho + 3, 40)

    # TOTAL DE REGISTROS
    hoja.cell(
        row=ultima_fila + 2,
        column=1
    ).value = f"Total de registros: {len(datos)}"

    # GUARDAR ARCHIVO
    libro.save(archivo)

    archivo.seek(0)

    return archivo
