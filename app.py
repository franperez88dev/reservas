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
from models import HORAS_CIERRE, HORAS_PASE, Asistente, Reserva, Sesion, ahora, db

app = Flask(__name__)
# PythonAnywhere está detrás de un proxy: así los enlaces de los emails salen con https
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///" + os.path.join(app.root_path, "reservas.db")
)
app.config["NOMBRE_SITIO"] = os.environ.get("NOMBRE_SITIO", "Cuenta cuentos en familia")
app.config["CONTACTO_TELEFONO"] = os.environ.get("CONTACTO_TELEFONO", "")
app.config["CONTACTO_EMAIL"] = os.environ.get("CONTACTO_EMAIL", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
MAX_PERSONAS_POR_RESERVA = 4

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


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


@app.template_filter("dia")
def formatear_dia(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


@app.template_filter("fecha")
def formatear_fecha(dt):
    return f"{formatear_dia(dt)}, {dt:%H:%M}"


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
        primer_apellido = request.form.get("primer_apellido", "").strip()
        segundo_apellido = request.form.get("segundo_apellido", "").strip()
        email = request.form.get("email", "").strip().lower()
        try:
            adultos = int(request.form.get("adultos", 1))
            menores = int(request.form.get("menores", 1))
        except ValueError:
            adultos, menores = 0, 0   # fuerza el error de abajo
        # Un nombre por cada recuadro del formulario (ver reservar.html)
        nombres_adultos = [n.strip() for n in request.form.getlist("nombre_adulto")]
        nombres_menores = [n.strip() for n in request.form.getlist("nombre_menor")]

        errores = []
        if not nombre or not primer_apellido or not segundo_apellido:
            errores.append("Escribe tu nombre y tus dos apellidos.")
        if "@" not in email:
            errores.append("Escribe un email válido.")
        if adultos < 1 or menores < 1:
            errores.append("Tiene que venir al menos 1 adulto y 1 menor.")
        elif adultos + menores > MAX_PERSONAS_POR_RESERVA:
            errores.append(f"Máximo {MAX_PERSONAS_POR_RESERVA} personas por reserva, "
                           "entre adultos y menores.")
        elif adultos + menores > sesion_.libres:
            errores.append(f"Solo quedan {sesion_.libres} plazas libres.")
        elif (len(nombres_adultos) != adultos or len(nombres_menores) != menores
              or not all(nombres_adultos + nombres_menores)):
            errores.append("Escribe el nombre de cada asistente.")

        # Repetir email en el mismo pase se permite, pero preguntando antes: la
        # página se vuelve a pintar con un popup y su botón "Confirmar" envía esta marca
        repetida = Reserva.query.filter_by(sesion_id=sesion_.id, email=email).first()
        falta_confirmar = (not errores and repetida is not None
                           and not request.form.get("confirmar_repetida"))

        if errores or falta_confirmar:
            # No se usa flash(): estos avisos salen junto al botón, no arriba
            return render_template("reservar.html", sesion=sesion_, form=request.form,
                                   errores=errores, confirmar_repetida=falta_confirmar,
                                   nombres_adultos=nombres_adultos,
                                   nombres_menores=nombres_menores,
                                   max_personas=MAX_PERSONAS_POR_RESERVA)

        numero = max((r.numero for r in sesion_.reservas), default=0) + 1
        reserva = Reserva(sesion=sesion_, nombre=nombre,
                          apellidos=f"{primer_apellido} {segundo_apellido}",
                          email=email, adultos=adultos, menores=menores,
                          numero=numero)
        reserva.asistentes = (
            [Asistente(nombre=n) for n in nombres_adultos]
            + [Asistente(nombre=n, menor=True) for n in nombres_menores]
        )
        db.session.add(reserva)
        db.session.commit()

        enviar(reserva.email, f"Reserva confirmada · {reserva.codigo}", "confirmacion",
               reserva=reserva,
               enlace_cancelar=url_for("cancelar_reserva", token=reserva.token,
                                       _external=True))
        return redirect(url_for("ver_reserva", token=reserva.token))

    return render_template("reservar.html", sesion=sesion_, form={}, errores=[],
                           confirmar_repetida=False,
                           nombres_adultos=[], nombres_menores=[],
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
            hora = request.form["hora"]
            if hora not in HORAS_PASE:
                raise ValueError
            # El <input type="date"> envía '2026-10-31'
            nueva = Sesion(
                fecha_hora=datetime.strptime(f"{request.form['dia']} {hora}",
                                             "%Y-%m-%d %H:%M"),
                plazas=int(request.form["plazas"]),
            )
            if nueva.plazas < 1:
                raise ValueError
        except (KeyError, ValueError):
            flash("Revisa los campos: fecha, hora y plazas son obligatorios.", "error")
            return formulario_nueva_sesion(request.form)
        if nueva.pasada:
            flash("Esa fecha y hora ya han pasado.", "error")
            return formulario_nueva_sesion(request.form)
        if Sesion.query.filter_by(fecha_hora=nueva.fecha_hora).first():
            flash(f"Ya existe el pase de las {hora} del {formatear_dia(nueva.dia)}.",
                  "error")
            return formulario_nueva_sesion(request.form)
        nueva.titulo = nueva.nombre
        db.session.add(nueva)
        db.session.commit()
        flash("Sesión creada.", "ok")
        return redirect(url_for("panel"))
    return formulario_nueva_sesion({})


def formulario_nueva_sesion(form):
    """La página recibe los pases que ya existen para no dejar elegirlos otra vez."""
    ocupadas = {}
    for s in Sesion.query.filter(Sesion.fecha_hora >= ahora()):
        ocupadas.setdefault(s.dia.isoformat(), []).append(f"{s.fecha_hora:%H:%M}")
    return render_template("admin/nueva_sesion.html", form=form, horas_pase=HORAS_PASE,
                           ocupadas=ocupadas, hoy=ahora().date().isoformat())


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
            enviar(r.email, f"Sesión cancelada · {sesion_.nombre}", "sesion_cancelada",
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
                       "Total", "Nombres adultos", "Nombres menores", "Asistencia"])
    for r in reservas:
        escritor.writerow([r.codigo, r.apellidos, r.nombre, r.adultos, r.menores,
                           r.personas, ", ".join(r.nombres_adultos),
                           ", ".join(r.nombres_menores), ""])
    escritor.writerow([])
    escritor.writerow(["", "", "TOTAL",
                       sum(r.adultos for r in reservas),
                       sum(r.menores for r in reservas),
                       sesion_.ocupadas, "", "", ""])

    nombre_archivo = f"listado_{sesion_.fecha_hora:%d%m_%H%M}.csv"
    return Response(
        salida.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"},
    )


if __name__ == "__main__":
    app.run(debug=True)
