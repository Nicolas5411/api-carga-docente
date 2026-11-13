
from datetime import date
import smtplib

from typing import Literal

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Body
)

from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.models.reportes import FiltrosReporte
from app.services.reportes_service import ReportesService
from app.services.correo_service import correo_service


router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)

service = ReportesService()


# ==========================================
# MODELO PARA ENVIO DE REPORTES POR CORREO
# ==========================================

class SolicitudEnvioReporte(BaseModel):

    destinatario: str = Field(
        min_length=5,
        max_length=254
    )

    tipo_reporte: Literal[
        "CARGA_DOCENTE",
        "EVALUACIONES"
    ]

    formato: Literal[
        "PDF",
        "EXCEL"
    ]

    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    programa: str | None = None
    apellido: str | None = None
    tipo_evaluacion: str | None = None


# ==========================================
# RESPUESTA DE DESCARGA
# ==========================================

def crear_descarga(archivo, nombre, tipo):

    archivo.seek(0)

    return StreamingResponse(
        archivo,
        media_type=tipo,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{nombre}"'
            )
        }
    )


# ==========================================
# CREAR FILTROS
# ==========================================

def crear_filtros(
    fecha_inicio,
    fecha_fin,
    programa,
    apellido,
    tipo_evaluacion=None
):

    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:

        raise HTTPException(
            status_code=400,
            detail=(
                "La fecha inicial no puede ser "
                "posterior a la fecha final"
            )
        )

    return FiltrosReporte(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        programa=programa,
        apellido=apellido,
        tipo_evaluacion=tipo_evaluacion
    )


# ==========================================
# REPORTE CARGA DOCENTE PDF
# ==========================================

@router.get("/carga-docente/pdf")
def descargar_carga_pdf(

    usuario_id: int = Query(..., gt=0),
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    programa: str | None = Query(None),
    apellido: str | None = Query(None)

):

    try:

        filtros = crear_filtros(
            fecha_inicio,
            fecha_fin,
            programa,
            apellido
        )

        archivo = service.reporte_carga_pdf(
            filtros,
            usuario_id
        )

        return crear_descarga(
            archivo,
            "reporte_carga_docente.pdf",
            "application/pdf"
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error generando reporte: {str(e)}"
        )


# ==========================================
# REPORTE CARGA DOCENTE EXCEL
# ==========================================

@router.get("/carga-docente/excel")
def descargar_carga_excel(

    usuario_id: int = Query(..., gt=0),
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    programa: str | None = Query(None),
    apellido: str | None = Query(None)

):

    try:

        filtros = crear_filtros(
            fecha_inicio,
            fecha_fin,
            programa,
            apellido
        )

        archivo = service.reporte_carga_excel(
            filtros,
            usuario_id
        )

        return crear_descarga(
            archivo,
            "reporte_carga_docente.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error generando reporte: {str(e)}"
        )


# ==========================================
# REPORTE EVALUACIONES PDF
# ==========================================

@router.get("/evaluaciones/pdf")
def descargar_evaluaciones_pdf(

    usuario_id: int = Query(..., gt=0),
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    programa: str | None = Query(None),
    apellido: str | None = Query(None),
    tipo_evaluacion: str | None = Query(None)

):

    try:

        filtros = crear_filtros(
            fecha_inicio,
            fecha_fin,
            programa,
            apellido,
            tipo_evaluacion
        )

        archivo = service.reporte_evaluaciones_pdf(
            filtros,
            usuario_id
        )

        return crear_descarga(
            archivo,
            "reporte_evaluaciones.pdf",
            "application/pdf"
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error generando reporte: {str(e)}"
        )


# ==========================================
# REPORTE EVALUACIONES EXCEL
# ==========================================

@router.get("/evaluaciones/excel")
def descargar_evaluaciones_excel(

    usuario_id: int = Query(..., gt=0),
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    programa: str | None = Query(None),
    apellido: str | None = Query(None),
    tipo_evaluacion: str | None = Query(None)

):

    try:

        filtros = crear_filtros(
            fecha_inicio,
            fecha_fin,
            programa,
            apellido,
            tipo_evaluacion
        )

        archivo = service.reporte_evaluaciones_excel(
            filtros,
            usuario_id
        )

        return crear_descarga(
            archivo,
            "reporte_evaluaciones.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error generando reporte: {str(e)}"
        )


# ==========================================
# ENVIAR REPORTE POR CORREO ELECTRONICO
# ==========================================

@router.post("/enviar-correo")
def enviar_reporte_correo(

    solicitud: SolicitudEnvioReporte = Body(...),

    usuario_id: int = Query(..., gt=0)

):

    try:

        # Crear filtros
        filtros = crear_filtros(
            solicitud.fecha_inicio,
            solicitud.fecha_fin,
            solicitud.programa,
            solicitud.apellido,
            solicitud.tipo_evaluacion
        )

        # Seleccionar reporte y formato
        reportes = {

            ("CARGA_DOCENTE", "PDF"): (
                service.reporte_carga_pdf,
                "reporte_carga_docente.pdf",
                "application/pdf"
            ),

            ("CARGA_DOCENTE", "EXCEL"): (
                service.reporte_carga_excel,
                "reporte_carga_docente.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),

            ("EVALUACIONES", "PDF"): (
                service.reporte_evaluaciones_pdf,
                "reporte_evaluaciones.pdf",
                "application/pdf"
            ),

            ("EVALUACIONES", "EXCEL"): (
                service.reporte_evaluaciones_excel,
                "reporte_evaluaciones.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        }

        funcion, nombre_archivo, mime_type = reportes[
            (
                solicitud.tipo_reporte,
                solicitud.formato
            )
        ]

        # Generar archivo
        archivo = funcion(
            filtros,
            usuario_id
        )

        if archivo is None:
            raise HTTPException(
                status_code=500,
                detail="No fue posible generar el archivo."
            )

        # Asunto del correo
        asunto = (
            "Reporte de carga docente"
            if solicitud.tipo_reporte == "CARGA_DOCENTE"
            else "Reporte de evaluaciones"
        )

        # Mensaje del correo
        mensaje = (
            "Cordial saludo.\n\n"
            "Adjuntamos el reporte solicitado desde la plataforma "
            "Carga Docente y Autoevaluación de la "
            "Institución Universitaria CUL.\n\n"
            "El documento contiene la información correspondiente "
            "a los filtros seleccionados.\n\n"
            "Este mensaje fue generado automáticamente."
        )

        # Enviar correo con archivo adjunto
        correo_service.enviar_correo(

            destinatario=solicitud.destinatario,

            asunto=asunto,

            mensaje=mensaje,

            archivo=archivo,

            nombre_archivo=nombre_archivo,

            mime_type=mime_type

        )

        return {

            "success": True,

            "mensaje": "El reporte fue enviado correctamente.",

            "destinatario": solicitud.destinatario,

            "archivo": nombre_archivo

        }

    except HTTPException:
        raise

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except RuntimeError:

        raise HTTPException(
            status_code=503,
            detail="El servicio de correo no está configurado correctamente."
        )

    except smtplib.SMTPException:

        raise HTTPException(
            status_code=502,
            detail="No fue posible enviar el correo electrónico."
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error enviando el reporte: {str(e)}"
        )
