
from app.repositories.reportes_repository import ReportesRepository
from app.utils.generar_archivos import generar_pdf, generar_excel


class ReportesService:

    def __init__(self):
        self.repository = ReportesRepository()

    # ==========================================
    # COLUMNAS DE LOS REPORTES
    # ==========================================

    def columnas_carga(self):
        return [
            "docente",
            "programa",
            "asignatura",
            "grupo",
            "periodo",
            "fecha_inicio",
            "fecha_finalizar",
            "estado"
        ]

    def columnas_evaluaciones(self):
        return [
            "docente",
            "programa",
            "tipo_evaluacion",
            "titulo",
            "fecha_envio",
            "promedio",
            "preguntas_respondidas",
            "comentarios"
        ]

    # ==========================================
    # REPORTE CARGA DOCENTE PDF
    # ==========================================

    def reporte_carga_pdf(self, filtros, usuario_id):

        print("\n========== REPORTE CARGA PDF ==========")
        print("Usuario:", usuario_id)
        print("Filtros:", filtros)

        datos = self.repository.obtener_carga_docente(filtros)

        print("Registros encontrados:", len(datos))

        archivo = generar_pdf(
            datos,
            "REPORTE DE CARGA DOCENTE",
            self.columnas_carga()
        )

        if archivo is None:
            raise Exception("No se pudo generar el PDF de carga docente.")

        archivo.seek(0)

        print("PDF generado correctamente.")
        print("=======================================\n")

        self.repository.registrar_historial(
            usuario_id=usuario_id,
            tipo_reporte="CARGA_DOCENTE",
            formato="PDF",
            filtros=filtros
        )

        archivo.seek(0)
        return archivo

    # ==========================================
    # REPORTE CARGA DOCENTE EXCEL
    # ==========================================

    def reporte_carga_excel(self, filtros, usuario_id):

        print("\n========= REPORTE CARGA EXCEL =========")
        print("Usuario:", usuario_id)
        print("Filtros:", filtros)

        datos = self.repository.obtener_carga_docente(filtros)

        print("Registros encontrados:", len(datos))

        archivo = generar_excel(
            datos,
            "REPORTE DE CARGA DOCENTE",
            self.columnas_carga()
        )

        if archivo is None:
            raise Exception("No se pudo generar el Excel de carga docente.")

        archivo.seek(0)

        self.repository.registrar_historial(
            usuario_id=usuario_id,
            tipo_reporte="CARGA_DOCENTE",
            formato="EXCEL",
            filtros=filtros
        )

        print("Excel generado correctamente.")
        print("=======================================\n")

        archivo.seek(0)
        return archivo

    # ==========================================
    # REPORTE EVALUACIONES PDF
    # ==========================================

    def reporte_evaluaciones_pdf(self, filtros, usuario_id):

        print("\n======== REPORTE EVALUACIONES PDF ========")
        print("Usuario:", usuario_id)
        print("Filtros:", filtros)

        datos = self.repository.obtener_evaluaciones(filtros)

        print("Registros encontrados:", len(datos))

        archivo = generar_pdf(
            datos,
            "REPORTE DE EVALUACIÓN DE DESEMPEÑO",
            self.columnas_evaluaciones()
        )

        if archivo is None:
            raise Exception("No se pudo generar el PDF de evaluaciones.")

        archivo.seek(0)

        self.repository.registrar_historial(
            usuario_id=usuario_id,
            tipo_reporte="EVALUACIONES",
            formato="PDF",
            filtros=filtros
        )

        print("PDF de evaluaciones generado correctamente.")
        print("==========================================\n")

        archivo.seek(0)
        return archivo

    # ==========================================
    # REPORTE EVALUACIONES EXCEL
    # ==========================================

    def reporte_evaluaciones_excel(self, filtros, usuario_id):

        print("\n======= REPORTE EVALUACIONES EXCEL =======")
        print("Usuario:", usuario_id)
        print("Filtros:", filtros)

        datos = self.repository.obtener_evaluaciones(filtros)

        print("Registros encontrados:", len(datos))

        archivo = generar_excel(
            datos,
            "REPORTE DE EVALUACIÓN DE DESEMPEÑO",
            self.columnas_evaluaciones()
        )

        if archivo is None:
            raise Exception("No se pudo generar el Excel de evaluaciones.")

        archivo.seek(0)

        self.repository.registrar_historial(
            usuario_id=usuario_id,
            tipo_reporte="EVALUACIONES",
            formato="EXCEL",
            filtros=filtros
        )

        print("Excel de evaluaciones generado correctamente.")
        print("==========================================\n")

        archivo.seek(0)
        return archivo
