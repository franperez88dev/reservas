"""Envío de emails a través de Gmail (lo único que permite PythonAnywhere gratis).

Necesita dos variables de entorno:
  MAIL_USER      -> la dirección de Gmail que envía
  MAIL_PASSWORD  -> una "contraseña de aplicación" de Google (no la normal)

Si no están configuradas (por ejemplo, en tu PC), no se envía nada: el email
se muestra en la terminal para que puedas ver cómo quedaría.
"""
import os
import smtplib
from email.message import EmailMessage

from flask import current_app, render_template


def enviar(destinatario, asunto, plantilla, **datos):
    """Envía un email usando una plantilla de templates/emails/.

    Devuelve True si se ha enviado. Nunca lanza error: si el email falla,
    la reserva ya está guardada y no queremos que el usuario vea un error.
    """
    usuario = os.environ.get("MAIL_USER")
    password = os.environ.get("MAIL_PASSWORD")
    texto = render_template(f"emails/{plantilla}.txt", **datos)

    if not usuario or not password:
        print(f"\n--- EMAIL (no enviado, falta configurar) ---\n"
              f"Para: {destinatario}\nAsunto: {asunto}\n\n{texto}\n---\n")
        return False

    mensaje = EmailMessage()
    mensaje["From"] = f"{current_app.config['NOMBRE_SITIO']} <{usuario}>"
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    contacto = current_app.config.get("CONTACTO_EMAIL")
    if contacto:
        mensaje["Reply-To"] = contacto   # si responden, le llega a tu amigo
    mensaje.set_content(texto)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as servidor:
            servidor.login(usuario, password)
            servidor.send_message(mensaje)
        return True
    except Exception as error:   # se ve en el "Error log" de PythonAnywhere
        current_app.logger.error("No se pudo enviar el email a %s: %s", destinatario, error)
        return False
