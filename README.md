# ServiHogar Durango — versión final integrada

Aplicación web Flask para la gestión de solicitudes de servicios domésticos, con interfaz adaptable, autenticación por roles, portal de cliente, panel de especialista, asignación desde dashboard y reseñas.

## Importante antes de desplegar
- Esta carpeta es una **versión de mejora preparada como paquete independiente** basada en el alcance descrito en la documentación compartida. No incluye las credenciales de tu archivo `.env` original.
- Revisa y compara con el repositorio del equipo antes de reemplazarlo. No sobrescribas producción sin probar en una rama.
- No se afirma que Render/Aiven hayan sido probados desde este paquete. Comprueba `/health` después de configurar las variables.
- Pagos, SMS/WhatsApp y facturación electrónica no están implementados.

## Funciones incluidas
- Página de inicio y catálogo de servicios.
- Formulario de solicitud que guarda en la base de datos.
- Creación de cuenta de cliente desde la primera solicitud y hash de contraseña.
- Inicio y cierre de sesión.
- Portal del cliente para ver solicitudes.
- Panel de especialista para cambiar estados de solicitudes asignadas.
- Dashboard de administración/gerencia/analista con métricas, asignación de especialistas y reseñas.
- Control de acceso por rol en servidor.
- Endpoint `/health` para revisar la conexión a PostgreSQL.
- CSS responsive y componentes visuales consistentes.

## Requisitos
Python 3.11 o superior y PostgreSQL (Aiven para producción).

## Ejecución local en Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edita `.env` con una `SECRET_KEY` propia y `DATABASE_URL`. Para generar una clave:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
Inicia la aplicación:
```powershell
python app.py
```
Abre http://127.0.0.1:5000

En desarrollo puedes usar SQLite local cambiando `DATABASE_URL=sqlite:///servihogar_local.db` en `.env`. Para producción usa la URL PostgreSQL de Aiven, con los parámetros TLS que indique Aiven para tu servicio.

## Roles
Los registros nuevos desde el formulario tienen rol `cliente`. Para crear usuarios internos de forma controlada, ejecuta `python crear_usuario.py --nombre "Nombre Apellido" --correo usuario@correo.com --rol especialista` y escribe la contraseña cuando se solicite. Los roles permitidos son `especialista`, `analista`, `gerente` y `admin` (también `cliente`). No publiques credenciales ni habilites registro público de administradores.

## GitHub
1. Descomprime el proyecto.
2. Copia los archivos a una rama de trabajo del repositorio del equipo.
3. Confirma que `.env` no se encuentre en Git:
```bash
git status
git add app.py templates static requirements.txt Procfile README.md .env.example .gitignore docs
git commit -m "Mejora integral de interfaz y flujos de ServiHogar"
git push origin nombre-de-rama
```
Si el repositorio ya existe, conserva su remoto y su historial. No uses `git init` encima de un repositorio existente sin revisar primero.

## Render
- Conecta el repositorio GitHub o selecciona la rama de trabajo.
- Tipo: Web Service.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Configura `SECRET_KEY` y `DATABASE_URL` en Environment.
- Configura la URL PostgreSQL de Aiven y los parámetros SSL que Aiven indique.
- Tras desplegar, visita `/health`. Espera `{"status":"ok","database":"connected"}`.
- No guardes `.env` ni certificados privados en GitHub. Si Aiven entrega un certificado CA como archivo, usa el mecanismo de Secret Files de Render y configura la URL para utilizarlo, siguiendo las instrucciones vigentes del proveedor.

## Aiven
- En el servicio PostgreSQL, abre Connection information y copia host, puerto, nombre de base, usuario y contraseña.
- Descarga/usa el certificado CA indicado por Aiven si la configuración de conexión lo requiere.
- Configura la URL en Render como variable secreta. No pegues contraseñas en el repositorio ni en capturas.
- Haz una prueba de conexión con `/health`.
- Haz una copia de seguridad antes de aplicar cambios a una base de datos con información real.

## Lista de pruebas manuales
- [ ] Inicio carga sin error.
- [ ] Catálogo muestra los servicios.
- [ ] Formulario valida campos y crea una solicitud.
- [ ] Cliente inicia sesión y ve solo sus solicitudes.
- [ ] Especialista ve sus solicitudes asignadas y cambia estado.
- [ ] Administrador/gerente/analista accede al dashboard.
- [ ] Dashboard asigna un especialista válido.
- [ ] Solo se permite reseñar una solicitud terminada.
- [ ] Usuario sin permisos recibe 403.
- [ ] `/health` devuelve estado correcto en producción.
- [ ] Diseño probado en escritorio y móvil.
- [ ] Logs de Render revisados y no hay errores de conexión.

## Limitaciones y trabajo pendiente
Este paquete no importa datos existentes ni migra automáticamente el esquema de una base de datos anterior. La creación de tablas se realiza con `db.create_all()`, adecuado para un prototipo, pero una actualización de producción debe usar migraciones revisadas. Antes de entregar, el equipo debe ejecutar pruebas reales, verificar el flujo completo con cuentas de cada rol y capturar evidencias de la aplicación desplegada.
