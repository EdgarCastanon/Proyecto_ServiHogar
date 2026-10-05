"""
Script de una sola vez para preparar datos de ejemplo:
  - Servicios del catálogo.
  - Usuarios especialistas con su habilidad, experiencia y disponibilidad.

Ejecutar con el entorno virtual activado:

    python seed_datos.py
"""
from werkzeug.security import generate_password_hash

from app import app, crear_base_datos_si_no_existe
from models import db, Servicio, Usuario, Perfil, EspecialistaHabilidad

crear_base_datos_si_no_existe()

with app.app_context():
    db.create_all()

    # ---------------- Servicios ----------------
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

    # ---------------- Especialistas de ejemplo ----------------
    # Contraseña de prueba para los 3: "especialista123"
    especialistas_ejemplo = [
        ("Juan López", "juan.lopez@servihogar.com", "6181234501", "Plomería", 5),
        ("Ana Torres", "ana.torres@servihogar.com", "6181234502", "Electricidad", 5),
        ("Carlos Ruiz", "carlos.ruiz@servihogar.com", "6181234503", "Limpieza", 4),
    ]

    if Usuario.query.filter_by(correo="juan.lopez@servihogar.com").first() is None:
        for nombre, correo, telefono, tipo_servicio, nivel in especialistas_ejemplo:
            usuario = Usuario(
                nombre=nombre,
                correo=correo,
                telefono=telefono,
                password_hash=generate_password_hash("especialista123"),
            )
            db.session.add(usuario)
            db.session.flush()

            db.session.add(Perfil(id_usuario=usuario.id, rol="especialista"))
            db.session.add(EspecialistaHabilidad(
                id_usuario=usuario.id,
                tipo_servicio=tipo_servicio,
                nivel_experiencia=nivel,
                disponible=True,
            ))
        db.session.commit()
        print("Especialistas de ejemplo insertados correctamente (contraseña: especialista123).")
    else:
        print("Ya existen especialistas registrados; no se insertaron duplicados.")

    # ---------------- Analista/Gerente y Administrador de ejemplo ----------------
    # Contraseña de prueba para ambos: "gerente123"
    gerencia_ejemplo = [
        ("Laura Méndez", "laura.mendez@servihogar.com", "6181234510", "analista"),
        ("Rubén Pizarro", "admin@servihogar.com", "6181234511", "administrador"),
    ]

    if Usuario.query.filter_by(correo="admin@servihogar.com").first() is None:
        for nombre, correo, telefono, rol in gerencia_ejemplo:
            usuario = Usuario(
                nombre=nombre,
                correo=correo,
                telefono=telefono,
                password_hash=generate_password_hash("gerente123"),
            )
            db.session.add(usuario)
            db.session.flush()
            db.session.add(Perfil(id_usuario=usuario.id, rol=rol))
        db.session.commit()
        print("Usuarios de analista y administrador insertados (contraseña: gerente123).")
    else:
        print("Ya existen usuarios de gerencia; no se insertaron duplicados.")
