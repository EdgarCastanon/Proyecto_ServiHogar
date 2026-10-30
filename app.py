import os
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from ai_service import generate_reply
import time

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-this-key")
database_url = os.getenv("DATABASE_URL", "sqlite:///servihogar_local.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
if database_url.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 300}
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="cliente")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    requests = db.relationship("ServiceRequest", backref="customer", foreign_keys="ServiceRequest.customer_id", lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    starting_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    icon = db.Column(db.String(10), nullable=False, default="🏠")

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    specialist_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    address = db.Column(db.String(250), nullable=False)
    details = db.Column(db.Text, nullable=False)
    preferred_date = db.Column(db.String(30), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Recibida")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    service = db.relationship("Service")
    specialist = db.relationship("User", foreign_keys=[specialist_id])


class SpecialistProfile(db.Model):
    """Información pública opcional para especialistas; se almacena aparte para no romper usuarios existentes."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False, index=True)
    specialties = db.Column(db.String(300), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False, default=0)
    city = db.Column(db.String(100), nullable=False, default="Durango, Durango")
    bio = db.Column(db.String(600), nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship("User", backref=db.backref("specialist_profile", uselist=False))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("service_request.id"), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    request = db.relationship("ServiceRequest")

def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            user = current_user()
            if user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator

@app.context_processor
def inject_user():
    return {"current_user": current_user()}

@app.route("/")
def index():
    services = Service.query.order_by(Service.id).all()
    return render_template("index.html", services=services)

@app.route("/cotizar", methods=["GET", "POST"])
def quote():
    services = Service.query.order_by(Service.name).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        service_id = request.form.get("service_id", type=int)
        address = request.form.get("address", "").strip()
        details = request.form.get("details", "").strip()
        preferred_date = request.form.get("preferred_date", "").strip()
        service = db.session.get(Service, service_id)
        if not all([name, email, password, service, address, details]):
            flash("Completa los campos obligatorios y selecciona un servicio válido.", "danger")
            return render_template("cotizar.html", services=services)
        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "danger")
            return render_template("cotizar.html", services=services)
        user = User.query.filter_by(email=email).first()
        if user and not session.get("user_id"):
            flash("Ese correo ya tiene una cuenta. Inicia sesión para solicitar el servicio.", "warning")
            return redirect(url_for("login"))
        if not user:
            user = User(name=name, email=email, phone=phone,
                        password_hash=generate_password_hash(password), role="cliente")
            db.session.add(user)
            db.session.flush()
        elif user.id != session.get("user_id"):
            flash("Inicia sesión con el correo de esa cuenta para continuar.", "warning")
            return redirect(url_for("login"))
        req = ServiceRequest(customer_id=user.id, service_id=service.id, address=address,
                             details=details, preferred_date=preferred_date, status="Recibida")
        db.session.add(req)
        db.session.commit()
        session["user_id"] = user.id
        flash(f"Solicitud #{req.id} registrada correctamente. Ya puedes consultar el seguimiento desde tu cuenta.", "success")
        return redirect(url_for("portal"))
    return render_template("cotizar.html", services=services)


@app.route("/registro-especialista", methods=["GET", "POST"])
def registro_especialista():
    """Registro público de especialistas. En producción debe añadirse verificación documental."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        specialties = request.form.getlist("specialties")
        experience = request.form.get("experience_years", type=int)
        city = request.form.get("city", "Durango, Durango").strip()
        bio = request.form.get("bio", "").strip()
        allowed = {"Plomería", "Electricidad", "Limpieza", "Pintura", "Jardinería", "Carpintería", "Cerrajería", "Reparaciones generales"}
        specialties = [item for item in specialties if item in allowed]
        if not all([name, email, password, phone, city]) or not specialties:
            flash("Completa los datos obligatorios y selecciona al menos una especialidad.", "danger")
            return render_template("registro_especialista.html")
        if len(password) < 10:
            flash("Usa una contraseña de al menos 10 caracteres.", "danger")
            return render_template("registro_especialista.html")
        if experience is None or not 0 <= experience <= 60:
            flash("Indica años de experiencia entre 0 y 60.", "danger")
            return render_template("registro_especialista.html")
        if User.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese correo. Inicia sesión o usa otro correo.", "warning")
            return render_template("registro_especialista.html")
        user = User(name=name, email=email, phone=phone,
                    password_hash=generate_password_hash(password), role="especialista")
        db.session.add(user)
        db.session.flush()
        profile = SpecialistProfile(user_id=user.id, specialties=", ".join(specialties),
                                     experience_years=experience, city=city, bio=bio[:600])
        db.session.add(profile)
        db.session.commit()
        flash("Cuenta de especialista creada. Tu perfil ya puede ser revisado por el equipo.", "success")
        return redirect(url_for("login"))
    return render_template("registro_especialista.html")

@app.route("/especialistas")
def directorio_especialistas():
    profiles = SpecialistProfile.query.join(User).filter(User.role == "especialista").order_by(
        SpecialistProfile.experience_years.desc(), User.name.asc()
    ).all()
    return render_template("directorio_especialistas.html", profiles=profiles)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            flash("Bienvenido de nuevo.", "success")
            destination = "dashboard" if user.role in ("admin", "gerente", "analista") else ("especialista" if user.role == "especialista" else "portal")
            return redirect(url_for(destination))
        flash("Correo o contraseña incorrectos.", "danger")
    return render_template("login.html")

@app.route("/salir")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("index"))

@app.route("/portal")
@roles_required("cliente")
def portal():
    user = current_user()
    requests_list = ServiceRequest.query.filter_by(customer_id=user.id).order_by(ServiceRequest.created_at.desc()).all()
    reviewed = {r.request_id for r in Review.query.filter_by(customer_id=user.id).all()}
    return render_template("portal.html", requests_list=requests_list, reviewed=reviewed)

@app.route("/resena/<int:request_id>", methods=["GET", "POST"])
@roles_required("cliente")
def review(request_id):
    req = ServiceRequest.query.filter_by(id=request_id, customer_id=current_user().id).first_or_404()
    if req.status != "Terminada":
        flash("Solo puedes reseñar servicios terminados.", "warning")
        return redirect(url_for("portal"))
    if Review.query.filter_by(request_id=req.id).first():
        flash("Esta solicitud ya tiene una reseña.", "info")
        return redirect(url_for("portal"))
    if request.method == "POST":
        rating = request.form.get("rating", type=int)
        comment = request.form.get("comment", "").strip()
        if rating not in range(1, 6) or not comment:
            flash("Selecciona una calificación y escribe un comentario.", "danger")
        else:
            db.session.add(Review(request_id=req.id, customer_id=current_user().id, rating=rating, comment=comment))
            db.session.commit()
            flash("Gracias por compartir tu opinión.", "success")
            return redirect(url_for("portal"))
    return render_template("resena.html", req=req)

@app.route("/especialista", methods=["GET", "POST"])
@roles_required("especialista", "admin")
def especialista():
    user = current_user()
    if request.method == "POST":
        req = db.session.get(ServiceRequest, request.form.get("request_id", type=int))
        status = request.form.get("status", "")
        if not req or status not in ("En proceso", "Terminada", "Cancelada"):
            abort(400)
        if user.role != "admin" and req.specialist_id != user.id:
            abort(403)
        req.status = status
        db.session.commit()
        flash("Estado actualizado.", "success")
        return redirect(url_for("especialista"))
    query = ServiceRequest.query.order_by(ServiceRequest.created_at.desc())
    if user.role != "admin":
        query = query.filter_by(specialist_id=user.id)
    return render_template("especialista.html", requests_list=query.all())

@app.route("/dashboard", methods=["GET", "POST"])
@roles_required("admin", "gerente", "analista")
def dashboard():
    if request.method == "POST":
        req = db.session.get(ServiceRequest, request.form.get("request_id", type=int))
        action = request.form.get("action", "assign")
        if not req:
            abort(404)
        if action == "status":
            new_status = request.form.get("status", "")
            if new_status not in ("Aprobada", "Rechazada", "En proceso", "Terminada", "Cancelada"):
                abort(400)
            req.status = new_status
            db.session.commit()
            flash(f"Solicitud #{req.id} actualizada correctamente.", "success")
        else:
            specialist_id = request.form.get("specialist_id", type=int)
            specialist = User.query.filter_by(id=specialist_id, role="especialista").first()
            if not specialist:
                flash("Selecciona un especialista válido.", "danger")
            else:
                req.specialist_id = specialist.id
                if req.status == "Recibida":
                    req.status = "Asignada"
                db.session.commit()
                flash("Especialista asignado correctamente.", "success")
        return redirect(url_for("dashboard"))
    all_requests = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).all()
    specialists = User.query.filter_by(role="especialista").order_by(User.name).all()
    counts = {
        "total": ServiceRequest.query.count(),
        "received": ServiceRequest.query.filter_by(status="Recibida").count(),
        "progress": ServiceRequest.query.filter_by(status="En proceso").count(),
        "done": ServiceRequest.query.filter_by(status="Terminada").count(),
        "customers": User.query.filter_by(role="cliente").count(),
        "specialists": len(specialists),
    }
    reviews = Review.query.order_by(Review.created_at.desc()).limit(8).all()
    return render_template("dashboard.html", requests_list=all_requests, specialists=specialists, counts=counts, reviews=reviews)

@app.route("/asistente-ia", methods=["GET", "POST"])
@login_required
def asistente_ia():
    """Asistente conversacional; solo usuarios autenticados para limitar abuso."""
    history = session.get("servihogar_ai_history", [])
    error_message = None
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        now = time.time()
        last_request = session.get("servihogar_ai_last_request", 0)
        if now - last_request < 2:
            error_message = "Espera un momento antes de enviar otro mensaje."
        elif not message:
            error_message = "Escribe una pregunta para continuar."
        elif len(message) > 1500:
            error_message = "Tu mensaje es demasiado largo. Usa máximo 1500 caracteres."
        else:
            session["servihogar_ai_last_request"] = now
            history = history[-4:]
            try:
                answer = generate_reply(message, history)
                history.extend([
                    {"role": "user", "content": message[:350]},
                    {"role": "assistant", "content": answer[:350]},
                ])
                session["servihogar_ai_history"] = history[-4:]
            except RuntimeError as exc:
                if str(exc) == "AI_DISABLED":
                    error_message = "El asistente de IA está temporalmente desactivado. Puedes seguir usando ServiHogar normalmente."
                else:
                    error_message = "El asistente no está configurado correctamente. Inténtalo más tarde."
            except Exception:
                app.logger.exception("Fallo al consultar el asistente de IA")
                error_message = "No pudimos conectar con el asistente en este momento. Inténtalo más tarde."
    return render_template("asistente_ia.html", history=history, error_message=error_message)


@app.route("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return {"status": "ok", "database": "connected"}, 200
    except Exception:
        app.logger.exception("Health check: database unavailable")
        return {"status": "error", "database": "unavailable"}, 503

@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="No tienes permisos para ver esta sección."), 403

@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="No encontramos la página que buscas."), 404

def seed_services():
    defaults = [
        ("Plomería", "Reparación de fugas, instalación y mantenimiento de tuberías.", 350, "🔧"),
        ("Electricidad", "Instalaciones, revisión de cortos y mantenimiento eléctrico.", 400, "⚡"),
        ("Limpieza", "Limpieza profunda y mantenimiento para tu hogar.", 300, "✨"),
    ]
    for name, description, price, icon in defaults:
        if not Service.query.filter_by(name=name).first():
            db.session.add(Service(name=name, description=description, starting_price=price, icon=icon))
    db.session.commit()

def seed_demo_accounts():
    admin_email = os.getenv("ADMIN_EMAIL", "ec037391@gmail.com").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    if admin_password and len(admin_password) >= 12:
        admin = User.query.filter_by(email=admin_email).first()
        if admin is None:
            db.session.add(User(name="Administrador ServiHogar", email=admin_email,
                                password_hash=generate_password_hash(admin_password), role="admin"))
        else:
            # La cuenta indicada como ADMIN_EMAIL se reserva para el panel administrativo.
            admin.name = "Administrador ServiHogar"
            admin.role = "admin"
            admin.password_hash = generate_password_hash(admin_password)

    if os.getenv("DEMO_SPECIALISTS_ENABLED", "false").strip().lower() == "true":
        demo_password = os.getenv("DEMO_SPECIALIST_PASSWORD", "")
        demo = [
            ("Juan López", "demo.plomeria1@servihogar.test", "Plomería, Reparaciones generales", 8, "Mantenimiento de tuberías y fugas."),
            ("María Fernanda Soto", "demo.plomeria2@servihogar.test", "Plomería, Cerrajería", 5, "Reparaciones domésticas y mantenimiento."),
            ("Ana Torres", "demo.electricidad1@servihogar.test", "Electricidad", 9, "Instalaciones eléctricas residenciales."),
            ("Luis Herrera", "demo.electricidad2@servihogar.test", "Electricidad, Reparaciones generales", 6, "Diagnóstico y mantenimiento residencial."),
            ("Carlos Ruiz", "demo.limpieza1@servihogar.test", "Limpieza", 7, "Limpieza profunda de casas."),
            ("Diana Morales", "demo.limpieza2@servihogar.test", "Limpieza, Jardinería", 4, "Limpieza y cuidado de jardines."),
            ("Roberto Vázquez", "demo.carpinteria@servihogar.test", "Carpintería, Reparaciones generales", 10, "Muebles, puertas y reparaciones."),
            ("Sofía Castillo", "demo.pintura@servihogar.test", "Pintura, Jardinería", 5, "Pintura interior y mantenimiento exterior."),
        ]
        if len(demo_password) >= 12:
            for name, email, specialties, years, bio in demo:
                user = User.query.filter_by(email=email).first()
                if user is None:
                    user = User(name=name, email=email, phone="6180000000",
                                password_hash=generate_password_hash(demo_password), role="especialista")
                    db.session.add(user)
                    db.session.flush()
                if not SpecialistProfile.query.filter_by(user_id=user.id).first():
                    db.session.add(SpecialistProfile(user_id=user.id, specialties=specialties,
                                                     experience_years=years, city="Durango, Durango", bio=bio))
        else:
            app.logger.warning("Configura DEMO_SPECIALIST_PASSWORD con al menos 12 caracteres.")
    db.session.commit()

with app.app_context():
    try:
        db.create_all()
        seed_services()
        seed_demo_accounts()
    except Exception:
        app.logger.exception("No fue posible inicializar la base de datos. Revisa DATABASE_URL.")

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
