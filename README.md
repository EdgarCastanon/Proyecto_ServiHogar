# ServiHogar Durango

Plataforma web académica para conectar clientes con especialistas de servicios domésticos en Durango. Stack actual: Python, Flask, Jinja, SQLAlchemy y PostgreSQL; despliegue previsto/actual en Render y base PostgreSQL configurada mediante variables de entorno.

> **Estado del proyecto:** este repositorio contiene funcionalidades implementadas y propuestas de evolución. No marques una función como lista hasta probarla localmente y en el despliegue real. Revisa también el PDF de documentación académica del equipo.

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
- Documentación técnica y académica: `docs/Documentacion_Final_ServiHogar_APA.pdf`

## Funcionalidad que existe en la implementación Flask actual

- Página pública y catálogo de servicios.
- Registro de clientes al solicitar un servicio.
- Inicio y cierre de sesión con contraseñas hasheadas.
- Portal de cliente e historial de solicitudes.
- Panel para especialistas con solicitudes asignadas y actualización de estado.
- Dashboard para los roles internos existentes y asignación manual de especialistas.
- Reseñas para solicitudes terminadas.
- Endpoint `/health` para comprobar la conexión a la base de datos.
- Servicio backend de IA en `ai_service.py`, ruta autenticada `/asistente-ia` e interfaz `templates/asistente_ia.html` (requiere API key y activación por entorno).
- Diseño adaptable en HTML/CSS.

La aplicación principal define los modelos `User`, `Service`, `ServiceRequest` y `Review` directamente en `app.py`. El archivo `models.py` contiene un esquema previo con nombres de tablas diferentes. **No ejecutes scripts antiguos de creación de datos sin comprobar primero sus importaciones y compatibilidad.**

## Evolución propuesta

### Registro y directorio de especialistas

La propuesta amplía el perfil profesional con especialidades, años de experiencia, ciudad y biografía. Un formulario público puede facilitar el alta, pero en un sistema real la cuenta debe quedar pendiente de revisión antes de recibir trabajos. No se debe confiar en los datos declarados ni asignar automáticamente una cuenta no verificada.

### Funciones siguientes recomendadas

1. Verificación y aprobación administrativa de especialistas.
2. Habilidades normalizadas en una tabla relacionada, en lugar de texto libre.
3. Disponibilidad por calendario y zonas de cobertura.
4. Historial de estados y auditoría de quién realizó cada cambio.
5. Recuperación de contraseña y verificación de correo.
6. Protección CSRF, límites de intentos de inicio de sesión y validación de entradas.
7. Migraciones de esquema con Flask-Migrate/Alembic.
8. Pruebas automatizadas de rutas, roles, permisos y persistencia.
9. Notificaciones por correo; WhatsApp/SMS y pagos quedan como integraciones posteriores.
10. Funciones de IA documentadas en `docs/PLAN_IA.md`.

## Preparación local (Windows PowerShell)

Requiere Python 3.11+ y acceso a una base PostgreSQL o SQLite local.

```powershell
git clone https://github.com/EdgarCastanon/Proyecto_ServiHogar.git
cd Proyecto_ServiHogar
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y configura `SECRET_KEY` y `DATABASE_URL`. Para desarrollo local puedes usar:

```env
SECRET_KEY=pon_aqui_una_clave_aleatoria_larga
DATABASE_URL=sqlite:///servihogar_local.db
FLASK_DEBUG=true
```

Genera una clave aleatoria con:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Inicia la app:

```powershell
python app.py
```

Abre http://127.0.0.1:5000. No uses una clave de desarrollo ni `FLASK_DEBUG=true` en producción.

## Despliegue en Render

1. Conecta el repositorio y selecciona la rama que hayas probado.
2. Tipo de servicio: **Web Service**.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `gunicorn app:app`.
5. Configura `SECRET_KEY` y `DATABASE_URL` desde Environment. No subas el archivo `.env`.
6. Si usas PostgreSQL externo, confirma host, puerto, base, usuario, contraseña y TLS según las instrucciones del proveedor.
7. Después del despliegue, abre `/health` y revisa los logs de Render.

La aplicación ejecuta `db.create_all()` al iniciar. Esto no reemplaza un sistema de migraciones y no modifica de forma segura todos los cambios futuros de esquema. Haz un respaldo antes de tocar una base con datos reales.

## Base de datos: regla importante

No borres ni recrees las tablas existentes solo para probar nuevas funciones. Primero:
1. Identifica el valor real de `DATABASE_URL` sin copiar secretos en chats.
2. Realiza un respaldo.
3. Compara las tablas existentes con los modelos activos de `app.py`.
4. Prueba cambios en una base de pruebas.
5. Diseña una migración revisada y reversible.
6. Comprueba clientes, solicitudes, asignaciones y reseñas después de migrar.

## Seguridad y cuentas de demostración

- Nunca guardes contraseñas en texto plano.
- No permitas que un formulario público cree cuentas de administrador.
- No publiques credenciales demo compartidas en producción.
- Las cuentas de prueba deben crearse únicamente en un entorno local o de staging, con contraseñas temporales y datos ficticios.
- Mantén `.env`, tokens de IA, credenciales de base de datos y certificados fuera de Git.
- En producción usa HTTPS, una `SECRET_KEY` segura, logs revisados, permisos mínimos y copias de seguridad.


## Cuentas ficticias para pruebas locales

Para crear ocho perfiles de especialistas de prueba (datos y correos ficticios), activa explícitamente el modo local:

```powershell
$env:ENABLE_DEMO_ACCOUNTS="YES_I_AM_LOCAL"
$env:DEMO_PASSWORD="UnaClaveDePruebaLarga!"
python seed_demo_specialists.py
```

Todas las cuentas demo usan la contraseña temporal indicada en `DEMO_PASSWORD`. No uses datos reales ni esta contraseña en producción. El script bloquea su ejecución si detecta variables de entorno de Render o `FLASK_ENV=production`. Tras probar, elimina las cuentas ficticias o la base local.

## Lista de verificación antes de entregar

- [ ] Registro e inicio de sesión válidos e inválidos.
- [ ] El cliente solo ve sus solicitudes.
- [ ] El especialista solo ve solicitudes asignadas a su cuenta.
- [ ] Un especialista no puede asignarse trabajos ni elevar su rol por manipular el formulario.
- [ ] Los cambios de estado están limitados a transiciones permitidas.
- [ ] Solo solicitudes terminadas admiten reseña y no se duplica.
- [ ] Un usuario sin permiso recibe 403.
- [ ] `/health` responde correctamente en el despliegue.
- [ ] La interfaz funciona en móvil y escritorio.
- [ ] Los logs no muestran errores ni secretos.
- [ ] Se verificó un respaldo y la compatibilidad del esquema real.

## Inteligencia artificial

Consulta la guía paso a paso en [`docs/PLAN_IA.md`](docs/PLAN_IA.md). La integración de un modelo requiere una API key propia configurada como variable secreta, control de costos, validación del contenido y pruebas. Una función basada en reglas o una pantalla de chat no debe presentarse como un modelo de IA conectado.

## Asistente de inteligencia artificial (OpenAI)

Se añadió una primera integración de backend con la Responses API del SDK de OpenAI:
- `ai_service.py`: llamada al modelo desde el servidor.
- `/asistente-ia`: ruta protegida para usuarios que hayan iniciado sesión.
- `templates/asistente_ia.html`: interfaz de conversación.
- `.env.example`: variables necesarias.

**La función permanece desactivada por defecto** (`AI_ENABLED=false`) y no funcionará hasta que configures una API key válida y habilites la variable. No se incluye ni se debe subir ninguna clave al repositorio.

### Probar localmente

1. Actualiza el repositorio e instala dependencias:
   ```powershell
   git pull origin main
   pip install -r requirements.txt
   ```
2. Crea una API key desde la plataforma oficial de OpenAI: https://platform.openai.com/api-keys. La API tiene facturación y límites independientes de una suscripción de ChatGPT; revisa precios y establece límites de gasto antes de probar.
3. Añade a tu archivo local `.env`:
   ```env
   AI_ENABLED=true
   OPENAI_API_KEY=pega_tu_clave_aqui
   OPENAI_MODEL=gpt-4.1-mini
   ```
4. Reinicia `python app.py`, inicia sesión y abre `/asistente-ia`.
5. Prueba una pregunta sencilla y confirma que la respuesta se muestra. Si aparece un error, revisa la terminal; no publiques la clave ni logs con secretos.

### Activar en Render

En el servicio web de Render, entra en **Environment** y agrega `AI_ENABLED=true`, `OPENAI_API_KEY` (como valor secreto) y `OPENAI_MODEL=gpt-4.1-mini`. Guarda los cambios y deja que el servicio se reinicie. La disponibilidad del modelo depende de tu cuenta y de la API; si no está habilitado, elige un modelo al que tengas acceso.

### Límites conocidos de la primera versión

- El asistente orienta y ayuda a describir solicitudes; **no consulta la base de datos para verificar precios, disponibilidad o identidades**.
- El historial conversacional es corto y se conserva en la sesión del navegador, no como historial permanente en la base de datos.
- Hay una espera básica entre envíos por sesión, pero todavía falta un limitador de frecuencia robusto del lado del servidor, protección CSRF global, monitoreo de consumo y pruebas automatizadas.
- No debe utilizarse para decisiones de seguridad ni para diagnósticos técnicos definitivos. No introduzcas datos personales innecesarios.
- La aplicación sigue funcionando con IA desactivada.

Consulta también `docs/PLAN_IA.md` para la hoja de ruta de funciones adicionales.

## Licencia

Proyecto académico. Añade una licencia formal si el equipo decide distribuir el código bajo términos específicos.
