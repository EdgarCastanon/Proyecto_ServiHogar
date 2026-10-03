# Proyecto ServiHogar Durango

Plataforma web para cotizar, contratar y dar seguimiento a servicios para el hogar
(Plomería, Electricidad, Limpieza), con roles de Prospecto, Cliente, Especialista,
Analista/Gerente y Administrador.

## Estado actual: Entregable 2 (Desarrollo I, II y III)

Sobre lo construido en el Entregable 1 (estructura, modelos, mockups), este entregable agrega:

- **Registro automático de Cliente**: al enviar el formulario de `/cotizar`, si el correo no
  existe, se crea automáticamente un `Usuario` + `Perfil` con rol `cliente`. La contraseña
  inicial es el número de teléfono (guardada como hash, nunca en texto plano).
- **Autenticación**: `/login` y `/logout`, con sesiones de Flask.
- **Asignación automática de especialista**: al crear la solicitud, el sistema busca en
  `especialistas_habilidades` al especialista disponible con mayor experiencia para ese tipo
  de servicio y se lo asigna automáticamente.
- **Portal del Cliente** (`/portal`): ver sus solicitudes y su estatus, cambiar su contraseña,
  dejar una reseña cuando el servicio esté terminado.
- **Panel del Especialista** (`/especialista`): ver sus solicitudes asignadas, actualizar el
  estatus (en proceso / terminado) y registrar observaciones en el historial.

**No incluye todavía:** dashboard ejecutivo para analistas/gerente/administrador, ni el
despliegue final en Render. Eso corresponde al Entregable 3.

## Credenciales de prueba
Después de ejecutar `python seed_datos.py` se crean 3 especialistas de ejemplo:

| Nombre | Correo | Contraseña | Servicio |
|---|---|---|---|
| Juan López | juan.lopez@servihogar.com | especialista123 | Plomería |
| Ana Torres | ana.torres@servihogar.com | especialista123 | Electricidad |
| Carlos Ruiz | carlos.ruiz@servihogar.com | especialista123 | Limpieza |

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

## Próximo entregable
- **Entregable 3:** dashboard ejecutivo para analista/gerente/administrador, control de
  vistas por rol, pruebas finales y despliegue en Render con base de datos en la nube.
