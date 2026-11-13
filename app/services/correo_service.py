
import os
import re
import smtplib

from io import BytesIO
from email.message import EmailMessage
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

        # Configuración SMTP
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        correo_remitente = os.getenv("SMTP_FROM") or smtp_user
        usar_ssl = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

        # Verificar configuración
        if not all([
            smtp_host,
            smtp_user,
            smtp_password,
            correo_remitente
        ]):
            raise RuntimeError(
                "Falta configurar las variables SMTP en el archivo .env"
            )

        # Validar correo del destinatario
        patron_correo = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.fullmatch(patron_correo, destinatario or ""):
            raise ValueError("El correo destinatario no es válido")

        # Preparar mensaje
        correo = EmailMessage()

        correo["Subject"] = asunto
        correo["From"] = correo_remitente
        correo["To"] = destinatario

        correo.set_content(mensaje)

        # Preparar archivo adjunto
        archivo.seek(0)
        contenido = archivo.read()

        if "/" not in mime_type:
            raise ValueError("El tipo de archivo no es válido")

        tipo_principal, tipo_secundario = mime_type.split("/", 1)

        correo.add_attachment(
            contenido,
            maintype=tipo_principal,
            subtype=tipo_secundario,
            filename=nombre_archivo
        )

        # Enviar correo
        if usar_ssl:
            with smtplib.SMTP_SSL(
                smtp_host,
                smtp_port,
                timeout=30
            ) as servidor:

                servidor.login(smtp_user, smtp_password)
                servidor.send_message(correo)

        else:
            with smtplib.SMTP(
                smtp_host,
                smtp_port,
                timeout=30
            ) as servidor:

                servidor.ehlo()
                servidor.starttls()
                servidor.ehlo()

                servidor.login(smtp_user, smtp_password)
                servidor.send_message(correo)

        return True


correo_service = CorreoService()
