from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

from models import (
    db, Servicio, Usuario, Perfil, EspecialistaHabilidad,
    SolicitudServicio, HistorialEstatus, Resena
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-insegura-solo-para-desarrollo-local")

# ==========================================================
# CONFIGURACIÓN DE LA BASE DE DATOS (PostgreSQL)
# ==========================================================
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
DB_NAME = os.environ.get("POSTGRES_DATABASE", "servihogar")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def crear_base_datos_si_no_existe():
    """Crea la base de datos del proyecto si todavía no existe (evita tener
    que crearla manualmente desde pgAdmin antes de correr la app)."""
    import psycopg2
    try:
        conexion = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname="postgres"
        )
        conexion.autocommit = True
        cursor = conexion.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Base de datos '{DB_NAME}' creada automáticamente.")
        cursor.close()
        conexion.close()
    except Exception as error:
        print("Aviso al verificar/crear la base de datos:", error)


# ==========================================================
# UTILIDADES DE SESIÓN Y ROLES
# ==========================================================
def login_required(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para continuar.", "error")
            return redirect(url_for("login"))
        return vista(*args, **kwargs)
    return envoltura


def rol_requerido(*roles_permitidos):
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if "usuario_id" not in session:
                flash("Debes iniciar sesión para continuar.", "error")
                return redirect(url_for("login"))
            if session.get("rol") not in roles_permitidos:
                flash("No tienes permiso para acceder a esta sección.", "error")
                return redirect(url_for("inicio"))
            return vista(*args, **kwargs)
        return envoltura
    return decorador


def asignar_especialista(nombre_servicio):
    """Busca, entre los especialistas disponibles para este tipo de servicio,
    al que tenga mayor nivel de experiencia. Devuelve su id_usuario o None
    si no hay nadie disponible en este momento."""
    habilidad = (
        EspecialistaHabilidad.query
        .filter_by(tipo_servicio=nombre_servicio, disponible=True)
        .order_by(EspecialistaHabilidad.nivel_experiencia.desc())
        .first()
    )
    return habilidad.id_usuario if habilidad else None


# ==========================================================
# PÁGINAS PÚBLICAS (Prospecto)
# ==========================================================
@app.route("/")
def inicio():
    servicios = Servicio.query.all()
    return render_template("index.html", servicios=servicios)


@app.route("/cotizar", methods=["GET", "POST"])
def cotizar():
    servicios = Servicio.query.all()

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        correo = request.form["correo"].strip().lower()
        telefono = request.form["telefono"].strip()
        id_servicio = int(request.form["servicio"])
        descripcion = request.form.get("descripcion", "").strip()

        servicio = Servicio.query.get_or_404(id_servicio)

        # ¿Ya existe una cuenta con este correo? (alguien que vuelve a cotizar)
        usuario = Usuario.query.filter_by(correo=correo).first()
        contrasena_generada = None

        if not usuario:
            # El teléfono es la contraseña inicial, tal como pide el anteproyecto
            contrasena_generada = telefono
            usuario = Usuario(
                nombre=nombre,
                correo=correo,
                telefono=telefono,
                password_hash=generate_password_hash(contrasena_generada),
            )
            db.session.add(usuario)
            db.session.flush()  # para obtener usuario.id antes del commit

            perfil = Perfil(id_usuario=usuario.id, rol="cliente")
            db.session.add(perfil)

        id_especialista = asignar_especialista(servicio.nombre)

        solicitud = SolicitudServicio(
            id_cliente=usuario.id,
            id_servicio=servicio.id,
            id_especialista=id_especialista,
            descripcion=descripcion,
            estatus="contratado" if id_especialista else "cotizado",
        )
        db.session.add(solicitud)
        db.session.commit()

        if id_especialista:
            db.session.add(HistorialEstatus(
                id_solicitud=solicitud.id,
                estatus_anterior="cotizado",
                estatus_nuevo="contratado",
                observaciones="Especialista asignado automáticamente por el sistema.",
            ))
            db.session.commit()

        return render_template(
            "confirmacion.html",
            usuario=usuario,
            solicitud=solicitud,
            contrasena_generada=contrasena_generada,
        )

    return render_template("cotizar.html", servicios=servicios)


# ==========================================================
# AUTENTICACIÓN
# ==========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"].strip().lower()
        password = request.form["password"]

        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario and check_password_hash(usuario.password_hash, password):
            session["usuario_id"] = usuario.id
            session["nombre"] = usuario.nombre
            session["rol"] = usuario.perfil.rol if usuario.perfil else "cliente"
            flash(f"Bienvenido, {usuario.nombre}.", "success")

            if session["rol"] == "especialista":
                return redirect(url_for("panel_especialista"))
            return redirect(url_for("portal_cliente"))

        flash("Correo o contraseña incorrectos.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("login"))


# ==========================================================
# PORTAL DEL CLIENTE
# ==========================================================
@app.route("/portal")
@rol_requerido("cliente")
def portal_cliente():
    solicitudes = (
        SolicitudServicio.query
        .filter_by(id_cliente=session["usuario_id"])
        .order_by(SolicitudServicio.fecha_creacion.desc())
        .all()
    )
    return render_template("portal_cliente.html", solicitudes=solicitudes)


@app.route("/portal/cambiar-password", methods=["GET", "POST"])
@rol_requerido("cliente")
def cambiar_password():
    if request.method == "POST":
        actual = request.form["actual"]
        nueva = request.form["nueva"]
        confirmar = request.form["confirmar"]

        usuario = Usuario.query.get(session["usuario_id"])

        if not check_password_hash(usuario.password_hash, actual):
            flash("La contraseña actual no es correcta.", "error")
        elif nueva != confirmar:
            flash("La nueva contraseña y su confirmación no coinciden.", "error")
        elif len(nueva) < 4:
            flash("La nueva contraseña debe tener al menos 4 caracteres.", "error")
        else:
            usuario.password_hash = generate_password_hash(nueva)
            db.session.commit()
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for("portal_cliente"))

    return render_template("cambiar_password.html")


@app.route("/portal/resena/<int:id_solicitud>", methods=["GET", "POST"])
@rol_requerido("cliente")
def dejar_resena(id_solicitud):
    solicitud = SolicitudServicio.query.get_or_404(id_solicitud)

    if solicitud.id_cliente != session["usuario_id"]:
        flash("Esa solicitud no pertenece a tu cuenta.", "error")
        return redirect(url_for("portal_cliente"))

    if solicitud.estatus != "terminado":
        flash("Solo puedes dejar una reseña cuando el servicio esté terminado.", "error")
        return redirect(url_for("portal_cliente"))

    if request.method == "POST":
        calificacion = int(request.form["calificacion"])
        comentario = request.form.get("comentario", "").strip()

        if solicitud.resena:
            solicitud.resena.calificacion = calificacion
            solicitud.resena.comentario = comentario
        else:
            db.session.add(Resena(
                id_solicitud=solicitud.id,
                calificacion=calificacion,
                comentario=comentario,
            ))
        db.session.commit()
        flash("¡Gracias por tu reseña!", "success")
        return redirect(url_for("portal_cliente"))

    return render_template("resena.html", solicitud=solicitud)


# ==========================================================
# PANEL DEL ESPECIALISTA
# ==========================================================
@app.route("/especialista")
@rol_requerido("especialista")
def panel_especialista():
    solicitudes = (
        SolicitudServicio.query
        .filter_by(id_especialista=session["usuario_id"])
        .order_by(SolicitudServicio.fecha_creacion.desc())
        .all()
    )
    return render_template("panel_especialista.html", solicitudes=solicitudes)


@app.route("/especialista/actualizar/<int:id_solicitud>", methods=["POST"])
@rol_requerido("especialista")
def actualizar_solicitud(id_solicitud):
    solicitud = SolicitudServicio.query.get_or_404(id_solicitud)

    if solicitud.id_especialista != session["usuario_id"]:
        flash("Esa solicitud no está asignada a ti.", "error")
        return redirect(url_for("panel_especialista"))

    nuevo_estatus = request.form["estatus"]
    observaciones = request.form.get("observaciones", "").strip()
    estatus_anterior = solicitud.estatus

    solicitud.estatus = nuevo_estatus
    db.session.add(HistorialEstatus(
        id_solicitud=solicitud.id,
        estatus_anterior=estatus_anterior,
        estatus_nuevo=nuevo_estatus,
        observaciones=observaciones,
    ))
    db.session.commit()
    flash("Avance registrado correctamente.", "success")
    return redirect(url_for("panel_especialista"))


if __name__ == "__main__":
    crear_base_datos_si_no_existe()
    with app.app_context():
        db.create_all()
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)
