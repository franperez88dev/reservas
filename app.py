import os
from datetime import datetime
from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from models import Reserva, Sesion, db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///" + os.path.join(app.root_path, "reservas.db")
)
app.config["NOMBRE_SITIO"] = os.environ.get("NOMBRE_SITIO", "Reservas")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
MAX_PERSONAS_POR_RESERVA = 6

db.init_app(app)
with app.app_context():
    db.create_all()


@app.context_processor
def variables_globales():
    return {"nombre_sitio": app.config["NOMBRE_SITIO"], "es_admin": session.get("admin")}


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
        Sesion.query.filter(Sesion.fecha_hora >= datetime.now())
        .order_by(Sesion.fecha_hora)
        .all()
    )
    return render_template("index.html", sesiones=proximas)


@app.route("/sesion/<int:sesion_id>", methods=["GET", "POST"])
def reservar(sesion_id):
    sesion_ = db.get_or_404(Sesion, sesion_id)
    if sesion_.fecha_hora < datetime.now():
        abort(404)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefono = request.form.get("telefono", "").strip()
        try:
            personas = int(request.form.get("personas", 1))
        except ValueError:
            personas = 0

        errores = []
        if not nombre:
            errores.append("Escribe tu nombre.")
        if "@" not in email:
            errores.append("Escribe un email válido.")
        if not 1 <= personas <= MAX_PERSONAS_POR_RESERVA:
            errores.append(f"Puedes reservar entre 1 y {MAX_PERSONAS_POR_RESERVA} plazas.")
        elif personas > sesion_.libres:
            errores.append(f"Solo quedan {sesion_.libres} plazas libres.")

        # TODO (Fran, parte 3): evitar que el mismo email reserve dos veces
        # en la misma sesión.

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("reservar.html", sesion=sesion_, form=request.form,
                                   max_personas=MAX_PERSONAS_POR_RESERVA)

        reserva = Reserva(sesion=sesion_, nombre=nombre, email=email,
                          telefono=telefono, personas=personas)
        db.session.add(reserva)
        db.session.commit()
        return redirect(url_for("confirmacion", reserva_id=reserva.id))

    return render_template("reservar.html", sesion=sesion_, form={},
                           max_personas=MAX_PERSONAS_POR_RESERVA)


@app.route("/confirmacion/<int:reserva_id>")
def confirmacion(reserva_id):
    reserva = db.get_or_404(Reserva, reserva_id)
    return render_template("confirmacion.html", reserva=reserva)


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
    return render_template("admin/panel.html", sesiones=sesiones, ahora=datetime.now())


@app.route("/admin/sesion/nueva", methods=["GET", "POST"])
@solo_admin
def nueva_sesion():
    if request.method == "POST":
        try:
            nueva = Sesion(
                titulo=request.form["titulo"].strip(),
                descripcion=request.form.get("descripcion", "").strip(),
                lugar=request.form.get("lugar", "").strip(),
                fecha_hora=datetime.strptime(request.form["fecha_hora"], "%Y-%m-%dT%H:%M"),
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


@app.route("/admin/sesion/<int:sesion_id>")
@solo_admin
def ver_reservas(sesion_id):
    # TODO (Fran, parte 1): carga la sesión y pásala a la plantilla
    # admin/reservas.html para listar quién ha reservado.
    abort(501)


# TODO (Fran, parte 2): ruta POST para cancelar una reserva
#   /admin/reserva/<int:reserva_id>/cancelar  -> borra y vuelve a ver_reservas


if __name__ == "__main__":
    app.run(debug=True)
