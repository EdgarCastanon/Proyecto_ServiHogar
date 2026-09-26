from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuario(db.Model):
    """Cuenta de acceso de cualquier tipo de usuario del sistema
    (cliente, especialista, analista/gerente o administrador)."""
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    perfil = db.relationship("Perfil", backref="usuario", uselist=False)

    def __repr__(self):
        return f"<Usuario {self.correo}>"


class Perfil(db.Model):
    """Define el rol del usuario dentro del sistema."""
    __tablename__ = "perfiles"

    ROLES = ["cliente", "especialista", "analista", "administrador"]

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, unique=True)
    rol = db.Column(db.String(20), nullable=False, default="cliente")

    def __repr__(self):
        return f"<Perfil {self.rol}>"


class Servicio(db.Model):
    """Catálogo de servicios que ofrece la empresa (Plomería, Electricidad, Limpieza...)."""
    __tablename__ = "servicios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_aproximado = db.Column(db.Numeric(10, 2))
    imagen_url = db.Column(db.String(255))

    def __repr__(self):
        return f"<Servicio {self.nombre}>"


class EspecialistaHabilidad(db.Model):
    """Habilidad, experiencia y disponibilidad de un especialista para un tipo de servicio.
    Un mismo especialista puede tener varias filas (una por cada servicio que domina)."""
    __tablename__ = "especialistas_habilidades"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    tipo_servicio = db.Column(db.String(100), nullable=False)
    nivel_experiencia = db.Column(db.Integer, default=1)  # escala 1 (básico) a 5 (experto)
    disponible = db.Column(db.Boolean, default=True)

    especialista = db.relationship("Usuario")


class SolicitudServicio(db.Model):
    """Cada cotización/solicitud de servicio realizada por un cliente."""
    __tablename__ = "solicitudes_servicio"

    ESTATUS = ["cotizado", "contratado", "en_proceso", "terminado"]

    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    id_servicio = db.Column(db.Integer, db.ForeignKey("servicios.id"), nullable=False)
    id_especialista = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    descripcion = db.Column(db.Text)
    estatus = db.Column(db.String(30), default="cotizado")
    precio_final = db.Column(db.Numeric(10, 2))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship("Usuario", foreign_keys=[id_cliente])
    servicio = db.relationship("Servicio")
    especialista = db.relationship("Usuario", foreign_keys=[id_especialista])

    def __repr__(self):
        return f"<Solicitud {self.id} - {self.estatus}>"


class HistorialEstatus(db.Model):
    """Bitácora de cambios de estatus y observaciones que va documentando el especialista."""
    __tablename__ = "historial_estatus"

    id = db.Column(db.Integer, primary_key=True)
    id_solicitud = db.Column(db.Integer, db.ForeignKey("solicitudes_servicio.id"), nullable=False)
    estatus_anterior = db.Column(db.String(30))
    estatus_nuevo = db.Column(db.String(30))
    observaciones = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    solicitud = db.relationship("SolicitudServicio", backref="historial")


class Resena(db.Model):
    """Calificación y comentario que deja el cliente al finalizar un servicio."""
    __tablename__ = "resenas"

    id = db.Column(db.Integer, primary_key=True)
    id_solicitud = db.Column(db.Integer, db.ForeignKey("solicitudes_servicio.id"), nullable=False, unique=True)
    calificacion = db.Column(db.Integer)  # escala 1 a 5
    comentario = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    solicitud = db.relationship("SolicitudServicio", backref=db.backref("resena", uselist=False))
