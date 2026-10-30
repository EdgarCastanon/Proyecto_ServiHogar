# ServiHogar Durango

Plataforma web académica para conectar clientes con especialistas de servicios domésticos en Durango. Permite consultar servicios, registrar solicitudes, dar seguimiento a trabajos, administrar asignaciones y conversar con un asistente de inteligencia artificial.

> **Estado de esta documentación:** describe la implementación encontrada en la rama `main`. La presencia de código no garantiza por sí sola que cada función esté configurada y probada en el servidor de producción. Las funciones que dependen de variables de entorno se indican expresamente.

## Equipo académico

- **Castañón Galván Edgar Ailton**
- **Pulgarin Flores Yosef Enrique**
- **Ramírez Campos Jesús Alejandro**

Instituto Tecnológico de Durango · Tecnológico Nacional de México  
Asignatura: Programación / Desarrollo Web · Grupo 8Y, 7.º semestre  
Docente: Rubén Pizarro Gurrola · Octubre de 2026

## Enlaces

- Repositorio: https://github.com/EdgarCastanon/Proyecto_ServiHogar
- Aplicación publicada: https://proyecto-servihogar.onrender.com/

## Tecnologías utilizadas

| Área | Tecnología | Función |
|---|---|---|
| Backend | Python | Lógica del servidor |
| Framework web | Flask | Rutas, sesiones y control de acceso |
| Plantillas | Jinja2, HTML | Páginas dinámicas |
| Interfaz | CSS | Diseño y adaptación a pantallas |
| Persistencia | Flask-SQLAlchemy / SQLAlchemy | Modelos y consultas |
| Base de datos | PostgreSQL en despliegue; SQLite para desarrollo local | Usuarios, servicios, solicitudes, perfiles y reseñas |
| Servidor de aplicación | Gunicorn | Ejecución de Flask en Render |
| Hosting | Render | Publicación y variables de entorno |
| Control de versiones | Git y GitHub | Código fuente y colaboración |
| IA | Groq API y SDK de Python `groq` | Respuestas del asistente conversacional |

## Funcionalidades implementadas

### 1. Sitio público y catálogo de servicios

- Página de inicio de ServiHogar.
- Catálogo inicial con Plomería, Electricidad y Limpieza.
- Cada servicio incluye descripción, precio inicial e icono.
- Acceso al formulario para solicitar/cotizar un servicio.
- Directorio público de especialistas registrados.

### 2. Clientes

- Registro de cuenta al solicitar un servicio.
- Inicio y cierre de sesión.
- Contraseñas almacenadas mediante hash.
- Formulario de solicitud con datos de contacto, servicio, dirección, descripción y fecha preferida.
- Portal privado con historial y seguimiento de las solicitudes propias.
- Posibilidad de dejar una reseña de 1 a 5 estrellas y comentario cuando la solicitud está terminada; se limita a una reseña por solicitud.
- Acceso al asistente de IA después de iniciar sesión.

### 3. Especialistas

- Registro de perfil profesional.
- Datos de teléfono, ciudad, biografía, años de experiencia y especialidades.
- Directorio público con perfiles registrados.
- Panel privado para consultar solicitudes asignadas.
- Actualización del estado de sus trabajos (En proceso, Terminada o Cancelada).
- El especialista solo puede gestionar solicitudes asignadas a su propia cuenta.

### 4. Administración

El panel se encuentra en `/dashboard` y está protegido para los roles autorizados (`admin`, `gerente` o `analista`).

- Consulta de las solicitudes registradas y sus detalles.
- Visualización de los datos de contacto y descripción proporcionados por el cliente.
- Indicadores de solicitudes totales, recibidas, en proceso y terminadas, además de clientes y especialistas.
- Asignación de especialistas a las solicitudes.
- Actualización del estado a Recibida, Aprobada, Rechazada, Asignada, En proceso, Terminada o Cancelada.
- Consulta de reseñas recientes.

#### Cuenta administradora

Configura estas variables privadas en Render:

- `ADMIN_EMAIL`: correo que se utilizará para iniciar sesión como administrador (el valor predeterminado del código es `ec037391@gmail.com`).
- `ADMIN_PASSWORD`: contraseña de al menos 12 caracteres.

Al iniciar la aplicación, si la contraseña cumple el requisito, la cuenta indicada se crea o actualiza con el rol `admin`. No publiques la contraseña en GitHub ni la compartas.

#### Especialistas ficticios para demostración

La inicialización de la aplicación crea ocho perfiles ficticios asignables desde el panel. La función está habilitada por defecto mediante `DEMO_SPECIALISTS_ENABLED=true`.

| Nombre de demostración | Especialidades | Experiencia |
|---|---|---:|
| Juan López | Plomería, reparaciones generales | 8 años |
| María Fernanda Soto | Plomería, cerrajería | 5 años |
| Ana Torres | Electricidad | 9 años |
| Luis Herrera | Electricidad, reparaciones generales | 6 años |
| Carlos Ruiz | Limpieza | 7 años |
| Diana Morales | Limpieza, jardinería | 4 años |
| Roberto Vázquez | Carpintería, reparaciones generales | 10 años |
| Sofía Castillo | Pintura, jardinería | 5 años |

Son perfiles ficticios para demostración académica, no proveedores reales ni verificados. Se pueden seleccionar para asignar solicitudes desde el panel administrativo. No es necesario iniciar sesión con esas cuentas para hacer asignaciones desde el panel. Si no se configura una contraseña demo válida, el código genera una contraseña aleatoria que no se publica.

### 5. Asistente de inteligencia artificial

La integración actual utiliza **Groq**, no una llamada directa a la API de OpenAI.

| Componente | Implementación |
|---|---|
| Proveedor de inferencia | Groq API |
| Biblioteca Python | SDK `groq` |
| Módulo de servicio | `ai_service.py` |
| Ruta web | `/asistente-ia` |
| Interfaz | `templates/asistente_ia.html` |
| Modelo predeterminado | `openai/gpt-oss-20b`, configurable mediante `GROQ_MODEL` |

El prefijo `openai/` es parte del identificador del modelo configurado en Groq; **el proveedor al que se conecta el código es Groq**. La guía anterior del README que pedía `OPENAI_API_KEY`, `OPENAI_MODEL` y el SDK OpenAI estaba desactualizada y queda sustituida por esta configuración.

#### ¿Qué hace el asistente?

- Conversa en español claro, amable y breve.
- Orienta sobre servicios domésticos: plomería, electricidad, limpieza, pintura, jardinería, carpintería, cerrajería y reparaciones generales.
- Ayuda al usuario a identificar qué tipo de servicio podría necesitar.
- Hace preguntas de aclaración cuando faltan datos.
- Ayuda a preparar o redactar una descripción de la solicitud.
- Conserva un contexto conversacional corto para responder tomando en cuenta mensajes recientes.

#### ¿Cómo funciona técnicamente?

1. El usuario autenticado abre `/asistente-ia`.
2. La ruta Flask recibe el mensaje del formulario y valida que no esté vacío ni supere 1,500 caracteres.
3. Se aplica una espera mínima de dos segundos entre envíos por sesión.
4. El backend llama a `generate_reply()` en `ai_service.py`.
5. El módulo crea el cliente de Groq con la clave secreta del entorno, prepara las instrucciones del sistema y hasta los últimos seis mensajes de historial que recibe.
6. Envía la conversación al modelo configurado y muestra la respuesta en la interfaz.
7. La sesión conserva un historial breve de los últimos intercambios; no se guarda como historial permanente en la base de datos.

El cliente Groq utiliza un timeout de 20 segundos y un reintento. El texto enviado al modelo se limita y la respuesta se recorta a un máximo de 4,000 caracteres.

#### Instrucciones y límites de seguridad del asistente

Las instrucciones del sistema le indican que:

- No invente precios, disponibilidad, identidades, reseñas ni asignaciones.
- No afirme consultar la base de datos: el asistente no tiene acceso a los datos actuales de solicitudes ni a la disponibilidad real de especialistas.
- No dé diagnósticos definitivos ni instrucciones para reparaciones peligrosas.
- Ante olor a gas, chispas, cables expuestos, riesgo de incendio o peligro inmediato, recomiende alejarse del riesgo y contactar a emergencias o a un profesional calificado.
- No solicite contraseñas, datos bancarios ni información personal innecesaria.
- Recuerde al usuario que es una IA y que debe revisar la información antes de actuar.

**La IA no asigna trabajos, no cambia estados, no aprueba ni rechaza solicitudes, no realiza cobros y no modifica la base de datos.** Esas acciones siguen bajo el control de las rutas y permisos de la aplicación.

#### Configuración de IA en Render o local

La función está apagada por defecto. Para habilitarla configura:

```env
AI_ENABLED=true
GROQ_API_KEY=tu_clave_secreta_de_groq
GROQ_MODEL=openai/gpt-oss-20b
```

- `AI_ENABLED`: debe valer `true` para activar el asistente; por defecto es `false`.
- `GROQ_API_KEY`: clave privada de Groq. Nunca debe subirse al repositorio.
- `GROQ_MODEL`: modelo disponible en Groq; si se omite, el código usa `openai/gpt-oss-20b`.

En Render, agrega las variables en **Environment** y guarda los cambios para que el servicio se reinicie. La disponibilidad depende de que la clave sea válida y el modelo esté habilitado en la cuenta. Para desactivar la función establece `AI_ENABLED=false`.

#### Limitaciones conocidas de la IA

- No está conectada a la base de datos ni conoce precios finales, solicitudes, disponibilidad o identidad real de especialistas.
- No ejecuta acciones en nombre del usuario.
- El historial es temporal y breve, asociado a la sesión.
- La espera de dos segundos es una protección básica por sesión, no un sistema robusto de limitación global de peticiones.
- No reemplaza a un técnico ni debe utilizarse para emergencias o diagnósticos definitivos.
- Su funcionamiento en producción requiere configurar y probar una clave válida de Groq y activar `AI_ENABLED=true`.

### 6. Otras rutas y utilidades

- `/health`: ejecuta una consulta sencilla a la base de datos y devuelve el estado de conexión.
- La aplicación inicializa las tablas y los datos básicos de servicios al arrancar mediante `db.create_all()` y `seed_services()`.

## Flujo de una solicitud

1. El cliente consulta el catálogo y elige un servicio.
2. Completa sus datos, dirección, descripción y fecha preferida.
3. La aplicación registra la solicitud con estado **Recibida** y crea o identifica la cuenta del cliente.
4. Administración revisa la solicitud y asigna un especialista.
5. El especialista consulta el trabajo en su panel y actualiza el estado.
6. El cliente revisa el seguimiento desde su portal.
7. Cuando el trabajo está **Terminado**, el cliente puede dejar una reseña.

## Estados de las solicitudes

- **Recibida:** solicitud registrada.
- **Aprobada:** solicitud aceptada por administración.
- **Rechazada:** solicitud no aceptada.
- **Asignada:** se seleccionó un especialista.
- **En proceso:** trabajo iniciado.
- **Terminada:** trabajo finalizado; habilita la reseña.
- **Cancelada:** solicitud cancelada.

## Modelos y base de datos

La implementación activa en `app.py` utiliza los modelos:

- `User`: usuarios, credenciales y roles.
- `Service`: catálogo de servicios.
- `ServiceRequest`: solicitudes, cliente, servicio, estado y asignación.
- `SpecialistProfile`: información profesional y especialidades.
- `Review`: calificaciones y comentarios asociados a solicitudes.

La aplicación ejecuta `db.create_all()` al iniciar. Esto crea tablas faltantes, pero no sustituye migraciones para cambios de estructura. Antes de modificar una base existente, realiza un respaldo y prueba los cambios en una base separada.

## Preparación local (Windows PowerShell)

Requiere Python 3.11+ y acceso a PostgreSQL o SQLite local.

```powershell
git clone https://github.com/EdgarCastanon/Proyecto_ServiHogar.git
cd Proyecto_ServiHogar
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y configura al menos `SECRET_KEY` y `DATABASE_URL`. Para desarrollo local puedes usar:

```env
SECRET_KEY=pon_aqui_una_clave_aleatoria_larga
DATABASE_URL=sqlite:///servihogar_local.db
FLASK_DEBUG=true
AI_ENABLED=false
```

Para usar el asistente localmente, agrega también `GROQ_API_KEY` y `GROQ_MODEL`, y establece `AI_ENABLED=true`.

Inicia la aplicación:

```powershell
python app.py
```

Abre http://127.0.0.1:5000. No uses una clave de desarrollo ni `FLASK_DEBUG=true` en producción.

## Despliegue en Render

1. Conecta el repositorio y selecciona la rama `main`.
2. Tipo de servicio: **Web Service**.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `gunicorn app:app`.
5. Configura `SECRET_KEY` y `DATABASE_URL` desde Environment.
6. Si deseas habilitar IA, configura también `AI_ENABLED=true`, `GROQ_API_KEY` y opcionalmente `GROQ_MODEL`.
7. Para el panel, configura `ADMIN_EMAIL` y `ADMIN_PASSWORD`.
8. Revisa `/health` y los logs de Render después del despliegue.

## Variables de entorno principales

| Variable | Propósito |
|---|---|
| `SECRET_KEY` | Firma de sesiones Flask; debe ser privada y aleatoria. |
| `DATABASE_URL` | Conexión a PostgreSQL o SQLite. |
| `AI_ENABLED` | Activa/desactiva el asistente; predeterminado `false`. |
| `GROQ_API_KEY` | Clave secreta para Groq. |
| `GROQ_MODEL` | Modelo de Groq; predeterminado `openai/gpt-oss-20b`. |
| `ADMIN_EMAIL` | Correo de la cuenta administradora. |
| `ADMIN_PASSWORD` | Contraseña administrativa; mínimo 12 caracteres. |
| `DEMO_SPECIALISTS_ENABLED` | Activa perfiles ficticios; predeterminado `true`. |
| `DEMO_SPECIALIST_PASSWORD` | Contraseña opcional de cuentas demo; si no cumple longitud, se genera una aleatoria. |

## Funciones que no están habilitadas en esta versión

- **Correo electrónico:** el envío de correos no está habilitado. No se necesita SMTP ni contraseña de aplicación de Gmail para utilizar el panel.
- **Pagos en línea:** no hay pasarela de pago activa.
- **WhatsApp/SMS:** no hay notificaciones por estos medios.
- **IA conectada a datos en tiempo real:** el asistente no consulta solicitudes, precios ni disponibilidad.
- **Verificación documental de especialistas:** los perfiles de demostración son ficticios y el registro de un perfil no equivale a una verificación profesional.

## Seguridad y mejoras pendientes

- Mantener claves, contraseñas y credenciales fuera de GitHub.
- Utilizar HTTPS, una `SECRET_KEY` segura, respaldos y permisos mínimos.
- Reforzar protección CSRF, límites globales de solicitudes y monitoreo.
- Incorporar migraciones con Flask-Migrate/Alembic.
- Añadir pruebas automatizadas de rutas, roles, permisos y persistencia.
- Incorporar verificación y aprobación administrativa de especialistas.
- Añadir auditoría del historial de estados y recuperación/verificación de cuentas.
- Para IA, mantener límites de costo, revisar privacidad y probar respuestas y errores del proveedor.

## Lista de verificación antes de la entrega

- [ ] Registro e inicio de sesión.
- [ ] El cliente solo consulta sus propias solicitudes.
- [ ] El especialista solo consulta trabajos asignados a su cuenta.
- [ ] Administración puede consultar solicitudes y asignar especialistas.
- [ ] Se pueden actualizar los estados permitidos.
- [ ] Solo las solicitudes terminadas admiten reseña y no se duplica.
- [ ] Un usuario sin permisos no puede entrar al panel administrativo.
- [ ] `/health` responde correctamente.
- [ ] La interfaz funciona en móvil y escritorio.
- [ ] El asistente IA responde con clave válida y muestra un mensaje útil cuando está desactivado o no configurado.
- [ ] Los logs no exponen claves ni contraseñas.
- [ ] Se verificó un respaldo y la compatibilidad del esquema de la base de datos.

## Licencia

Proyecto académico. Añade una licencia formal si el equipo decide distribuir el código bajo términos específicos.
