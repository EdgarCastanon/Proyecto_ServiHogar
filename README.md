# Proyecto ServiHogar Durango

Plataforma web para cotizar, contratar y dar seguimiento a servicios para el hogar
(Plomería, Electricidad, Limpieza), con roles de Prospecto, Cliente, Especialista,
Analista/Gerente y Administrador.

## Estado actual: Entregable 3 (Integración, pruebas y despliegue)

Sobre lo construido en el Entregable 1 (estructura, modelos, mockups) y el Entregable 2
(registro automático, login, asignación automática, portales), este entregable agrega:

- **Dashboard ejecutivo** (`/dashboard`), solo para los roles `analista` y `administrador`:
  indicadores de cotizados/contratados/en proceso/terminados, gráfica de servicios más
  solicitados (Chart.js) y tabla de especialistas mejor calificados según las reseñas.
- **Control de vistas por rol reforzado**: el menú de navegación y cada ruta muestran/permiten
  solo lo que corresponde según el rol de la sesión activa (`cliente`, `especialista`,
  `analista`, `administrador`).
- **Soporte para base de datos en la nube con SSL** (Aiven), listo para desplegarse en Render.

Con este entregable, el ciclo completo del anteproyecto queda implementado:
Prospecto → Cliente → Asignación automática → Seguimiento → Reseña → Dashboard ejecutivo.

## Credenciales de prueba
Después de ejecutar `python seed_datos.py` se crean 3 especialistas de ejemplo:

| Nombre | Correo | Contraseña | Servicio |
|---|---|---|---|
| Juan López | juan.lopez@servihogar.com | especialista123 | Plomería |
| Ana Torres | ana.torres@servihogar.com | especialista123 | Electricidad |
| Carlos Ruiz | carlos.ruiz@servihogar.com | especialista123 | Limpieza |
| Laura Méndez | laura.mendez@servihogar.com | gerente123 | Analista |
| Rubén Pizarro | admin@servihogar.com | gerente123 | Administrador |

Para probar como Cliente, simplemente llena el formulario en `/cotizar` con un correo nuevo;
la cuenta y contraseña (tu teléfono) se muestran en la pantalla de confirmación.

## Estructura del proyecto
```
Proyecto_ServiHogar/
│
├── app.py                     (aplicación Flask: rutas, login, asignación automática)
├── models.py                   (modelos SQLAlchemy / tablas de la base de datos)
├── seed_datos.py                (servicios y especialistas de ejemplo)
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html               (catálogo público)
│   ├── cotizar.html              (formulario de cotización, ya funcional)
│   ├── confirmacion.html          (credenciales y especialista asignado)
│   ├── login.html
│   ├── portal_cliente.html
│   ├── cambiar_password.html
│   ├── resena.html
│   └── panel_especialista.html
│
├── static/
│   ├── css/estilos.css
│   ├── js/
│   └── img/
│
└── docs/
    └── diagrama_entidad_relacion.png
```

## Ejecución local
1. Copiar `.env.example` a `.env` y completar los datos (incluye ahora `SECRET_KEY`).
2. Crear entorno virtual e instalar dependencias:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Crear las tablas y los datos de ejemplo:
   ```
   python seed_datos.py
   ```
4. Ejecutar la aplicación:
   ```
   python app.py
   ```
5. Abrir en el navegador: http://127.0.0.1:5000

## Flujo de prueba sugerido
1. Entra a `/cotizar`, llena el formulario con un correo nuevo y elige "Plomería".
2. En la confirmación verás que se asignó automáticamente a Juan López.
3. Inicia sesión con el correo y el teléfono que usaste.
4. En tu portal verás la solicitud con estatus "contratado".
5. Cierra sesión e inicia con `juan.lopez@servihogar.com` / `especialista123`.
6. En su panel, cambia el estatus a "terminado" y agrega una observación.
7. Vuelve a entrar como cliente y deja una reseña desde tu portal.

## Lista de pruebas antes de entregar
- [ ] Un Prospecto nuevo puede cotizar y se crea su cuenta de Cliente automáticamente.
- [ ] El especialista correcto se asigna automáticamente según el tipo de servicio.
- [ ] El Cliente puede iniciar sesión, ver su solicitud, cambiar su contraseña y dejar reseña.
- [ ] El Especialista puede iniciar sesión, ver sus solicitudes y actualizar el estatus.
- [ ] El Analista/Gerente y el Administrador pueden ver el Dashboard; un Cliente o Especialista
      que intente entrar a `/dashboard` es redirigido y no puede verlo.
- [ ] La aplicación funciona igual en local y en la URL pública de Render.

## Despliegue en la nube (Render + Aiven PostgreSQL)
1. Crear (o reutilizar) una base de datos PostgreSQL gratuita en Aiven.
2. En Render, crear un Web Service nuevo conectado a este repositorio:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
3. Variables de entorno en Render: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`,
   `POSTGRES_PASSWORD`, `POSTGRES_DATABASE`, `SECRET_KEY`, y `POSTGRES_SSL_CA` con el valor
   `/etc/secrets/ca.pem`.
3. Subir el certificado de Aiven como **Secret File** en Render, con nombre `ca.pem`.
4. Desplegar y probar la URL pública siguiendo la lista de pruebas de arriba.
