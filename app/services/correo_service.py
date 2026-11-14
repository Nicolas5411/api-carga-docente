
import os
import re
import json
import base64
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv()


class CorreoService:

    def enviar_correo(
        self,
        destinatario,
        asunto,
        mensaje,
        archivo,
        nombre_archivo,
        mime_type
    ):

        # Configuración de Brevo
        api_key = os.getenv("BREVO_API_KEY")
        correo_remitente = os.getenv("BREVO_SENDER_EMAIL")
        nombre_remitente = os.getenv(
            "BREVO_SENDER_NAME",
            "Carga Docente CUL"
        )

        # Verificar configuración
        if not all([
            api_key,
            correo_remitente,
            nombre_remitente
        ]):
            raise RuntimeError(
                "El servicio de correo no está configurado correctamente. "
                "Verifica BREVO_API_KEY, BREVO_SENDER_EMAIL "
                "y BREVO_SENDER_NAME."
            )

        # Validar correo del destinatario
        patron_correo = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.fullmatch(patron_correo, destinatario or ""):
            raise ValueError(
                "El correo destinatario no es válido"
            )

        # Validar tipo de archivo
        if not mime_type or "/" not in mime_type:
            raise ValueError(
                "El tipo de archivo no es válido"
            )

        # Convertir archivo a Base64
        archivo.seek(0)
        contenido = archivo.read()

        archivo_base64 = base64.b64encode(
            contenido
        ).decode("utf-8")

        # Preparar solicitud para Brevo
        datos = {
            "sender": {
                "name": nombre_remitente,
                "email": correo_remitente
            },
            "to": [
                {
                    "email": destinatario
                }
            ],
            "subject": asunto,
            "textContent": mensaje,
            "attachment": [
                {
                    "name": nombre_archivo,
                    "content": archivo_base64
                }
            ]
        }

        cuerpo = json.dumps(datos).encode("utf-8")

        solicitud = urllib.request.Request(
            "https://api.brevo.com/v3/smtp/email",
            data=cuerpo,
            headers={
                "api-key": api_key,
                "accept": "application/json",
                "content-type": "application/json"
            },
            method="POST"
        )

        # Enviar correo mediante Brevo
        try:
            with urllib.request.urlopen(
                solicitud,
                timeout=30
            ) as respuesta:

                resultado = json.loads(
                    respuesta.read().decode("utf-8")
                )

                return {
                    "success": True,
                    "message": "Correo enviado correctamente",
                    "message_id": resultado.get("messageId")
                }

        except urllib.error.HTTPError as error:

            detalle = error.read().decode(
                "utf-8",
                errors="replace"
            )

            raise RuntimeError(
                f"Brevo rechazó el envío: {detalle}"
            )

        except urllib.error.URLError as error:

            raise RuntimeError(
                f"No fue posible conectar con Brevo: {error.reason}"
            )


correo_service = CorreoService()
