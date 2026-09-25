import csv
import io
import os
import unicodedata
from datetime import datetime
from functools import wraps

from flask import (Flask, Response, abort, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.middleware.proxy_fix import ProxyFix

from correo import enviar
from models import HORAS_CIERRE, Reserva, Sesion, ahora, db

app = Flask(__name__)
# PythonAnywhere está detrás de un proxy: así los enlaces de los emails salen con https
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///" + os.path.join(app.root_path, "reservas.db")
)
app.config["NOMBRE_SITIO"] = os.environ.get("NOMBRE_SITIO", "Reservas")
app.config["CONTACTO_TELEFONO"] = os.environ.get("CONTACTO_TELEFONO", "")
app.config["CONTACTO_EMAIL"] = os.environ.get("CONTACTO_EMAIL", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
MAX_PERSONAS_POR_RESERVA = 6

db.init_app(app)
with app.app_context():
    db.create_all()


@app.context_processor
def variables_globales():
    """Variables disponibles en TODAS las plantillas sin tener que pasarlas."""
    return {
        "nombre_sitio": app.config["NOMBRE_SITIO"],
        "contacto_telefono": app.config["CONTACTO_TELEFONO"],
        "contacto_email": app.config["CONTACTO_EMAIL"],
        "horas_cierre": HORAS_CIERRE,
        "es_admin": session.get("admin"),
    }


@app.template_filter("fecha")
def formatear_fecha(dt):
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month - 1]}, {dt:%H:%M}"


# ---------------------------------------------------------------- público

@app.route("/")
def index():
    proximas = (
        Sesion.query.filter(Sesion.fecha_hora >= ahora())
        .order_by(Sesion.fecha_hora)
        .all()
    )
    return render_template("index.html", sesiones=proximas)


@app.route("/sesion/<int:sesion_id>", methods=["GET", "POST"])
def reservar(sesion_id):
    sesion_ = db.get_or_404(Sesion, sesion_id)
    if sesion_.pasada:
        abort(404)

    # Si ya no se admiten reservas, la plantilla muestra el aviso y no el formulario
    if request.method == "POST" and sesion_.abierta:
        nombre = request.form.get("nombre", "").strip()
        apellidos = request.form.get("apellidos", "").strip()
        email = request.form.get("email", "").strip().lower()
        try:
            adultos = int(request.form.get("adultos", 1))
            menores = int(request.form.get("menores", 0))
        except ValueError:
            adultos, menores = 0, -1   # fuerza el error de abajo

        errores = []
        if not nombre or not apellidos:
            errores.append("Escribe tu nombre y apellidos.")
        if "@" not in email:
            errores.append("Escribe un email válido.")
        elif Reserva.query.filter_by(sesion_id=sesion_.id, email=email).first():
            errores.append("Ya hay una reserva con este email para esta sesión. "
                           "Si quieres cambiarla, cancélala desde el enlace de tu email "
                           "y vuelve a reservar.")
        if adultos < 1 or menores < 0:
            errores.append("Tiene que venir al menos 1 adulto.")
        elif adultos + menores > MAX_PERSONAS_POR_RESERVA:
            errores.append(f"Máximo {MAX_PERSONAS_POR_RESERVA} plazas por reserva.")
        elif adultos + menores > sesion_.libres:
            errores.append(f"Solo quedan {sesion_.libres} plazas libres.")

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("reservar.html", sesion=sesion_, form=request.form,
                                   max_personas=MAX_PERSONAS_POR_RESERVA)

        numero = max((r.numero for r in sesion_.reservas), default=0) + 1
        reserva = Reserva(sesion=sesion_, nombre=nombre, apellidos=apellidos,
                          email=email, adultos=adultos, menores=menores,
                          numero=numero)
        db.session.add(reserva)
        db.session.commit()

        enviar(reserva.email, f"Reserva confirmada · {reserva.codigo}", "confirmacion",
               reserva=reserva,
               enlace_cancelar=url_for("cancelar_reserva", token=reserva.token,
                                       _external=True))
        return redirect(url_for("ver_reserva", token=reserva.token))

    return render_template("reservar.html", sesion=sesion_, form={},
                           max_personas=MAX_PERSONAS_POR_RESERVA)


@app.route("/reserva/<token>")
def ver_reserva(token):
    """Página de confirmación. Usa el token secreto, no el id, para que nadie
    pueda ver las reservas de otros cambiando el número de la URL."""
    reserva = Reserva.query.filter_by(token=token).first_or_404()
    return render_template("confirmacion.html", reserva=reserva)


@app.route("/reserva/<token>/cancelar", methods=["GET", "POST"])
def cancelar_reserva(token):
    reserva = Reserva.query.filter_by(token=token).first()
    if reserva is None:
        # Ya se canceló (o el enlace está mal): no es un error grave
        return render_template("cancelada.html", reserva=None)
    if reserva.sesion.pasada:
        abort(404)

    # El enlace del email abre una página con un botón (GET). Solo se cancela al
    # pulsarlo (POST). Algunos programas de correo "visitan" los enlaces solos,
    # y no queremos que eso cancele la reserva sin querer.
    if request.method == "POST":
        datos = {"reserva": reserva}
        enviar(reserva.email, f"Reserva cancelada · {reserva.codigo}", "cancelacion",
               **datos)
        db.session.delete(reserva)
        db.session.commit()
        return render_template("cancelada.html", reserva=reserva)

    return render_template("cancelar.html", reserva=reserva)


# ---------------------------------------------------------------- admin

def solo_admin(vista):
    @wraps(vista)
    def envoltorio(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login", siguiente=request.path))
        return vista(*args, **kwargs)
    return envoltorio


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(request.args.get("siguiente") or url_for("panel"))
        flash("Contraseña incorrecta.", "error")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("index"))


@app.route("/admin")
@solo_admin
def panel():
    sesiones = Sesion.query.order_by(Sesion.fecha_hora.desc()).all()
    return render_template("admin/panel.html", sesiones=sesiones, ahora=ahora())


@app.route("/admin/sesion/nueva", methods=["GET", "POST"])
@solo_admin
def nueva_sesion():
    if request.method == "POST":
        try:
            nueva = Sesion(
                titulo=request.form["titulo"].strip(),
                descripcion=request.form.get("descripcion", "").strip(),
                lugar=request.form.get("lugar", "").strip(),
                fecha_hora=datetime_desde_formulario(request.form["fecha_hora"]),
                plazas=int(request.form["plazas"]),
            )
            if not nueva.titulo or nueva.plazas < 1:
                raise ValueError
        except (KeyError, ValueError):
            flash("Revisa los campos: título, fecha y plazas son obligatorios.", "error")
            return render_template("admin/nueva_sesion.html", form=request.form)
        db.session.add(nueva)
        db.session.commit()
        flash("Sesión creada.", "ok")
        return redirect(url_for("panel"))
    return render_template("admin/nueva_sesion.html", form={})


def datetime_desde_formulario(texto):
    """El <input type="datetime-local"> envía '2026-09-28T16:00'."""
    return datetime.strptime(texto, "%Y-%m-%dT%H:%M")


@app.route("/admin/sesion/<int:sesion_id>")
@solo_admin
def ver_reservas(sesion_id):
    sesion_ = db.get_or_404(Sesion, sesion_id)
    reservas = sorted(sesion_.reservas, key=lambda r: r.numero)
    return render_template("admin/reservas.html", sesion=sesion_, reservas=reservas)


@app.route("/admin/sesion/<int:sesion_id>/borrar", methods=["POST"])
@solo_admin
def borrar_sesion(sesion_id):
    sesion_ = db.get_or_404(Sesion, sesion_id)
    avisados = 0
    if not sesion_.pasada:   # si ya pasó, no tiene sentido avisar a nadie
        for r in sesion_.reservas:
            enviar(r.email, f"Sesión cancelada · {sesion_.titulo}", "sesion_cancelada",
                   reserva=r)
            avisados += 1
    db.session.delete(sesion_)   # las reservas se borran solas (cascade)
    db.session.commit()
    mensaje = "Sesión borrada."
    if avisados:
        mensaje += f" Se ha avisado por email a {avisados} reserva(s)."
    flash(mensaje, "ok")
    return redirect(url_for("panel"))


def sin_tildes(texto):
    """'Álvarez' -> 'alvarez', para ordenar alfabéticamente sin que las tildes molesten."""
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


@app.route("/admin/sesion/<int:sesion_id>/listado.csv")
@solo_admin
def descargar_listado(sesion_id):
    """Listado para imprimir el día del evento, ordenado por apellidos."""
    sesion_ = db.get_or_404(Sesion, sesion_id)
    reservas = sorted(sesion_.reservas,
                      key=lambda r: (sin_tildes(r.apellidos), sin_tildes(r.nombre)))

    salida = io.StringIO()
    # ";" y BOM (utf-8-sig) para que el Excel en español lo abra bien a la primera
    escritor = csv.writer(salida, delimiter=";")
    escritor.writerow(["Nº reserva", "Apellidos", "Nombre", "Adultos", "Menores",
                       "Total", "Asistencia"])
    for r in reservas:
        escritor.writerow([r.codigo, r.apellidos, r.nombre, r.adultos, r.menores,
                           r.personas, ""])
    escritor.writerow([])
    escritor.writerow(["", "", "TOTAL",
                       sum(r.adultos for r in reservas),
                       sum(r.menores for r in reservas),
                       sesion_.ocupadas, ""])

    nombre_archivo = f"listado_{sesion_.fecha_hora:%d%m_%H%M}.csv"
    return Response(
        salida.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"},
    )


if __name__ == "__main__":
    app.run(debug=True)
