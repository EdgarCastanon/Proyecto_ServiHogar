from flask import Flask, render_template
import os
from dotenv import load_dotenv

from models import db, Servicio

load_dotenv()

app = Flask(__name__)

# ==========================================================
# CONFIGURACIÓN DE LA BASE DE DATOS (PostgreSQL)
#   - En LOCAL se leen desde el archivo .env
#   - En RENDER (nube) se configuran en el Dashboard, en "Environment"
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
    """Se conecta a la base de datos de mantenimiento 'postgres' (que siempre existe)
    y crea la base de datos del proyecto si todavía no existe. Esto evita tener que
    crearla manualmente desde pgAdmin antes de correr la app por primera vez."""
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


@app.route("/")
def inicio():
    """Página pública: catálogo de servicios (vista Prospecto)."""
    servicios = Servicio.query.all()
    return render_template("index.html", servicios=servicios)


@app.route("/cotizar")
def cotizar():
    """Formulario de solicitud de cotización.
    NOTA (Entregable 1): esta vista solo muestra el formulario.
    El guardado en base de datos y la conversión automática a Cliente
    se implementarán en el Entregable 2."""
    servicios = Servicio.query.all()
    return render_template("cotizar.html", servicios=servicios)


if __name__ == "__main__":
    crear_base_datos_si_no_existe()
    with app.app_context():
        db.create_all()
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)
