# Reservas

Web sencilla para reservar plazas en sesiones con aforo limitado.
Flask + SQLite, sin pagos.

## Arrancar en local

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

Panel de administración en `/admin`.

## Configuración

Variables de entorno: `ADMIN_PASSWORD`, `SECRET_KEY`, `NOMBRE_SITIO`.