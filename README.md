# Web de reservas (Flask + SQLite)

Web sencilla para reservar plazas en sesiones con aforo limitado. Sin pagos.

- **Parte pública**: lista de próximas sesiones con plazas libres → formulario de reserva → confirmación.
- **Panel de admin** (`/admin`): crear sesiones y ver la ocupación.

## Arrancar en local

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                   # http://127.0.0.1:5000
```

La base de datos `reservas.db` se crea sola al arrancar. Admin: `/admin` (contraseña por defecto `admin`).

## Variables de entorno

| Variable         | Para qué                               | Por defecto           |
|------------------|----------------------------------------|-----------------------|
| `NOMBRE_SITIO`   | Nombre en la cabecera                  | `Reservas`            |
| `ADMIN_PASSWORD` | Contraseña del panel                   | `admin` ⚠️ cámbiala   |
| `SECRET_KEY`     | Firma de la cookie de sesión           | ⚠️ cámbiala           |
| `DATABASE_URL`   | Otra BD si algún día hace falta        | SQLite local          |

## Tus partes (los `TODO` del código)

1. **Ver reservas de una sesión**: ruta `ver_reservas` en `app.py` + tabla en `templates/admin/reservas.html`.
2. **Cancelar una reserva**: nueva ruta POST `/admin/reserva/<id>/cancelar` + botón en cada fila.
3. **Evitar reservas duplicadas**: el mismo email no puede reservar dos veces en la misma sesión.

## Desplegar gratis en PythonAnywhere (recomendado: SQLite persiste)

1. Crea una cuenta gratuita y sube el proyecto (Files o `git clone` desde una consola Bash).
2. En una consola: `mkvirtualenv reservas --python=python3.11 && pip install -r requirements.txt`
3. Web → *Add a new web app* → *Manual configuration* → Python 3.11.
4. Rellena *Source code* y *Virtualenv* con tus rutas.
5. Edita el fichero WSGI:
   ```python
   import sys, os
   sys.path.insert(0, "/home/TUUSUARIO/reservas")
   os.environ["ADMIN_PASSWORD"] = "..."
   os.environ["SECRET_KEY"] = "..."
   os.environ["NOMBRE_SITIO"] = "..."
   from app import app as application
   ```
6. *Static files*: URL `/static/` → `/home/TUUSUARIO/reservas/static`.
7. *Reload*. Queda en `TUUSUARIO.pythonanywhere.com`.

> Render gratis también sirve, pero su disco se borra en cada despliegue y SQLite perdería las reservas. Para Render habría que pasar a Postgres (`DATABASE_URL`).
