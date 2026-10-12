import os
import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Horas antes de la sesión en las que se cierran las reservas
HORAS_CIERRE = int(os.environ.get("HORAS_CIERRE", 5))

# Horas a las que puede haber pase: las del desplegable de "Nueva sesión"
HORAS_PASE = ["11:00", "12:00"]


def ahora():
    """Hora actual de Madrid. El servidor de PythonAnywhere va en UTC (2 h menos)."""
    return datetime.now(ZoneInfo("Europe/Madrid")).replace(tzinfo=None)


def nuevo_token():
    """Cadena aleatoria imposible de adivinar, para los enlaces privados."""
    return secrets.token_urlsafe(16)


class Sesion(db.Model):
    """Un evento/clase con aforo limitado."""

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, default="")
    fecha_hora = db.Column(db.DateTime, nullable=False)
    lugar = db.Column(db.String(200), default="")
    plazas = db.Column(db.Integer, nullable=False)

    reservas = db.relationship(
        "Reserva", backref="sesion", cascade="all, delete-orphan", lazy=True
    )

    @property
    def nombre(self):
        """Lo que se enseña como título. De momento es siempre igual: solo cambia
        la hora (la columna `titulo` se conserva por las sesiones antiguas)."""
        return f"Pase de las {self.fecha_hora:%H:%M}"

    @property
    def dia(self):
        return self.fecha_hora.date()

    @property
    def ocupadas(self):
        return sum(r.personas for r in self.reservas)

    @property
    def libres(self):
        return max(self.plazas - self.ocupadas, 0)

    @property
    def completa(self):
        return self.libres == 0

    @property
    def cierre(self):
        """Momento a partir del cual ya no se admiten reservas."""
        return self.fecha_hora - timedelta(hours=HORAS_CIERRE)

    @property
    def abierta(self):
        return ahora() < self.cierre

    @property
    def pasada(self):
        return self.fecha_hora < ahora()


class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sesion_id = db.Column(db.Integer, db.ForeignKey("sesion.id"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    apellidos = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    adultos = db.Column(db.Integer, nullable=False, default=1)
    menores = db.Column(db.Integer, nullable=False, default=0)
    numero = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(32), unique=True, nullable=False, default=nuevo_token)
    creada = db.Column(db.DateTime, default=ahora)

    asistentes = db.relationship(
        "Asistente", backref="reserva", cascade="all, delete-orphan", lazy=True,
        order_by="Asistente.id"
    )

    @property
    def personas(self):
        return self.adultos + self.menores

    @property
    def nombres_adultos(self):
        return [a.nombre for a in self.asistentes if not a.menor]

    @property
    def nombres_menores(self):
        return [a.nombre for a in self.asistentes if a.menor]

    @property
    def codigo(self):
        fecha = self.sesion.fecha_hora.strftime("%d%m_%H%M")
        return f"{fecha}_{self.numero:02d}"


class Asistente(db.Model):
    """Cada persona que viene con una reserva. Las reservas antiguas no tienen."""

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey("reserva.id"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    menor = db.Column(db.Boolean, nullable=False, default=False)
