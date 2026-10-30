"""Crea cuentas ficticias para pruebas locales. NO ejecutar en producción.

PowerShell:
  $env:ENABLE_DEMO_ACCOUNTS="YES_I_AM_LOCAL"
  $env:DEMO_PASSWORD="UnaClaveDePruebaLarga!"
  python seed_demo_specialists.py

Usa una contraseña temporal y cámbiala después. El script es idempotente.
"""
import os
from werkzeug.security import generate_password_hash
from app import app, db, User, SpecialistProfile

if os.getenv("ENABLE_DEMO_ACCOUNTS") != "YES_I_AM_LOCAL":
    raise SystemExit("Bloqueado: configura ENABLE_DEMO_ACCOUNTS=YES_I_AM_LOCAL solo en local.")
if os.getenv("RENDER") or os.getenv("FLASK_ENV") == "production":
    raise SystemExit("Bloqueado: no crees cuentas demo en producción.")
password = os.getenv("DEMO_PASSWORD", "")
if len(password) < 12:
    raise SystemExit("Configura DEMO_PASSWORD con al menos 12 caracteres.")

DEMO = [
    ("Juan López", "demo.plomeria1@servihogar.test", "6180001001", "Plomería, Reparaciones generales", 8, "Durango, Durango", "Mantenimiento de tuberías, fugas y accesorios."),
    ("María Fernanda Soto", "demo.plomeria2@servihogar.test", "6180001002", "Plomería, Cerrajería", 5, "Durango, Durango", "Reparaciones domésticas y mantenimiento preventivo."),
    ("Ana Torres", "demo.electricidad1@servihogar.test", "6180001003", "Electricidad", 9, "Durango, Durango", "Instalaciones y revisión eléctrica residencial."),
    ("Luis Herrera", "demo.electricidad2@servihogar.test", "6180001004", "Electricidad, Reparaciones generales", 6, "Durango, Durango", "Diagnóstico y mantenimiento residencial."),
    ("Carlos Ruiz", "demo.limpieza1@servihogar.test", "6180001005", "Limpieza", 7, "Durango, Durango", "Limpieza profunda de casas y departamentos."),
    ("Diana Morales", "demo.limpieza2@servihogar.test", "6180001006", "Limpieza, Jardinería", 4, "Durango, Durango", "Limpieza periódica y cuidado básico de jardines."),
    ("Roberto Vázquez", "demo.carpinteria@servihogar.test", "6180001007", "Carpintería, Reparaciones generales", 10, "Durango, Durango", "Muebles, puertas y reparaciones generales."),
    ("Sofía Castillo", "demo.pintura@servihogar.test", "6180001008", "Pintura, Jardinería", 5, "Durango, Durango", "Pintura interior y mantenimiento exterior."),
]

with app.app_context():
    db.create_all()
    created = 0
    for name, email, phone, specialties, years, city, bio in DEMO:
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(name=name, email=email, phone=phone,
                        password_hash=generate_password_hash(password), role="especialista")
            db.session.add(user)
            db.session.flush()
            created += 1
        profile = SpecialistProfile.query.filter_by(user_id=user.id).first()
        if profile is None:
            db.session.add(SpecialistProfile(user_id=user.id, specialties=specialties,
                                             experience_years=years, city=city, bio=bio))
    db.session.commit()
    print(f"Proceso terminado. Cuentas nuevas: {created}.")
    print("Correos de prueba: demo.plomeria1@servihogar.test ... demo.pintura@servihogar.test")
    print("Todas usan la DEMO_PASSWORD indicada en esta terminal. No publiques esta contraseña.")
