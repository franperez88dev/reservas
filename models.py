from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
    def ocupadas(self):
        return sum(r.personas for r in self.reservas)

    @property
    def libres(self):
        return max(self.plazas - self.ocupadas, 0)

    @property
    def completa(self):
        return self.libres == 0


class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sesion_id = db.Column(db.Integer, db.ForeignKey("sesion.id"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(30), default="")
    personas = db.Column(db.Integer, nullable=False, default=1)
    creada = db.Column(db.DateTime, default=datetime.now)
