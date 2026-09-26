"""
Script de una sola vez para insertar servicios de ejemplo en la tabla 'servicios'.
Ejecutar con el entorno virtual activado:

    python seed_datos.py
"""
from app import app, crear_base_datos_si_no_existe
from models import db, Servicio

crear_base_datos_si_no_existe()

with app.app_context():
    db.create_all()

    if Servicio.query.count() == 0:
        db.session.add_all([
            Servicio(
                nombre="Plomería",
                descripcion="Reparación de fugas, destape de tuberías e instalación de accesorios.",
                precio_aproximado=350,
            ),
            Servicio(
                nombre="Electricidad",
                descripcion="Instalaciones y reparaciones eléctricas seguras para el hogar.",
                precio_aproximado=400,
            ),
            Servicio(
                nombre="Limpieza",
                descripcion="Limpieza profunda de casas, departamentos y oficinas.",
                precio_aproximado=300,
            ),
        ])
        db.session.commit()
        print("Servicios de ejemplo insertados correctamente.")
    else:
        print("Ya existen servicios registrados; no se insertaron duplicados.")
