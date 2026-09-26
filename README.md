# Proyecto ServiHogar Durango

Plataforma web para cotizar, contratar y dar seguimiento a servicios para el hogar
(Plomería, Electricidad, Limpieza), con roles de Prospecto, Cliente, Especialista,
Analista/Gerente y Administrador.

## Estado actual: Entregable 1 (Análisis y Diseño)

Este entregable incluye:

- Estructura completa de carpetas del proyecto Flask.
- Modelo de base de datos (SQLAlchemy) con las 7 tablas del diseño relacional.
- Diagrama entidad-relación (`docs/diagrama_entidad_relacion.png`).
- Páginas públicas iniciales: catálogo de servicios y formulario de cotización
  (todavía sin lógica de guardado; eso se implementa en el Entregable 2).
- Hoja de estilos con la identidad visual de la marca.

**No incluye todavía:** registro automático de clientes, login, asignación automática
de especialistas, portal de seguimiento ni dashboard ejecutivo. Esas funcionalidades
corresponden a los Entregables 2 y 3, según el calendario del anteproyecto.

## Estructura del proyecto
```
Proyecto_ServiHogar/
│
├── app.py                  (aplicación Flask principal)
├── models.py                (modelos SQLAlchemy / tablas de la base de datos)
├── seed_datos.py             (script para insertar servicios de ejemplo)
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html            (catálogo público de servicios)
│   └── cotizar.html           (formulario de cotización - solo interfaz)
│
├── static/
│   ├── css/estilos.css
│   ├── js/                    (para futuras funciones dinámicas)
│   └── img/
│
└── docs/
    └── diagrama_entidad_relacion.png
```

## Modelo de datos (resumen)
| Tabla | Propósito |
|---|---|
| usuarios | Cuenta de acceso de cualquier tipo de usuario |
| perfiles | Rol del usuario (cliente, especialista, analista, administrador) |
| servicios | Catálogo de servicios ofrecidos |
| especialistas_habilidades | Habilidades/experiencia/disponibilidad de cada especialista |
| solicitudes_servicio | Cada cotización/solicitud de un cliente |
| historial_estatus | Bitácora de avance de cada solicitud |
| resenas | Calificación y comentario del cliente al finalizar |

Ver el diagrama completo en `docs/diagrama_entidad_relacion.png`.

## Ejecución local
1. Instalar PostgreSQL localmente (o usar el que ya se instaló en prácticas anteriores).
2. Copiar `.env.example` a `.env` y completar los datos de conexión.
3. Crear entorno virtual e instalar dependencias:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Crear las tablas y cargar servicios de ejemplo:
   ```
   python seed_datos.py
   ```
5. Ejecutar la aplicación:
   ```
   python app.py
   ```
6. Abrir en el navegador: http://127.0.0.1:5000

## Próximos entregables
- **Entregable 2:** registro automático de cliente, autenticación, asignación automática
  de especialista, portal de cliente y especialista.
- **Entregable 3:** dashboard ejecutivo, control de vistas por rol, pruebas y despliegue
  final en Render.
