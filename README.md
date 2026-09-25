# Reservas

Web sencilla para reservar plazas en sesiones con aforo limitado.
Flask + SQLite, sin pagos. Envía la confirmación por email con enlace para cancelar.

## Arrancar en local

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

Panel de administración en `/admin`. En local, si no configuras el correo,
los emails se muestran en la terminal en lugar de enviarse.

## Configuración (variables de entorno)

- `ADMIN_PASSWORD`, `SECRET_KEY`, `NOMBRE_SITIO`
- `MAIL_USER`, `MAIL_PASSWORD`: cuenta de Gmail y su contraseña de aplicación
- `CONTACTO_TELEFONO`, `CONTACTO_EMAIL`: aparecen en la web y en los emails
- `HORAS_CIERRE`: horas antes de cada sesión en que se cierran las reservas (5 por defecto)
