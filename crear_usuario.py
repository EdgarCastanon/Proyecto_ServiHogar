"""Crea usuarios internos de forma controlada desde la terminal.
Uso: python crear_usuario.py --nombre 'Nombre' --correo usuario@correo.com --rol especialista
No imprime ni guarda la contraseña en archivos; la solicita de forma interactiva.
"""
import argparse
from getpass import getpass
from app import app, db, User
from werkzeug.security import generate_password_hash

parser = argparse.ArgumentParser(description="Crear un usuario ServiHogar")
parser.add_argument("--nombre", required=True)
parser.add_argument("--correo", required=True)
parser.add_argument("--rol", required=True, choices=["cliente", "especialista", "analista", "gerente", "admin"])
parser.add_argument("--telefono", default="")
args = parser.parse_args()
password = getpass("Contraseña (mínimo 8 caracteres): ")
if len(password) < 8:
    raise SystemExit("Error: la contraseña debe tener al menos 8 caracteres.")
with app.app_context():
    email = args.correo.strip().lower()
    if User.query.filter_by(email=email).first():
        raise SystemExit("Error: ya existe una cuenta con ese correo.")
    user = User(name=args.nombre.strip(), email=email, phone=args.telefono.strip(),
                password_hash=generate_password_hash(password), role=args.rol)
    db.session.add(user)
    db.session.commit()
    print(f"Usuario creado: {user.email} (rol: {user.role}).")
