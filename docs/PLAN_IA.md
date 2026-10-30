# Plan de integración de IA en ServiHogar Durango

Este documento separa ideas de implementación futura de las funciones que ya están conectadas. La aplicación actual es Flask/Jinja/SQLAlchemy; no debe afirmarse que tiene IA hasta conectar y probar un proveedor/modelo real.

## Funciones de IA con valor práctico

1. **Asistente para describir la solicitud:** convierte lo que escribe el cliente en una descripción más clara y propone preguntas de aclaración. El cliente revisa y acepta el texto antes de guardar.
2. **Clasificación y priorización:** sugiere categoría, urgencia y datos faltantes. Para electricidad, gas, inundaciones u otros riesgos, mostrar reglas de seguridad y recomendar servicios de emergencia cuando corresponda; no permitir que el modelo decida por sí solo.
3. **Recomendación de especialista:** filtra primero por especialidad, disponibilidad, zona y carga de trabajo mediante consultas SQL. La IA solo puede explicar las opciones elegibles; no debe inventar perfiles ni saltarse criterios.
4. **Ayuda al especialista:** resume la solicitud y sugiere una lista de comprobación, sin reemplazar el criterio profesional.
5. **Analítica administrativa:** resume tendencias agregadas sin enviar nombres, direcciones, teléfonos ni textos identificables al proveedor.
6. **Asistente de preguntas frecuentes:** responde usando únicamente contenido aprobado de los servicios, precios de referencia, horarios y políticas.

## Arquitectura recomendada

Navegador → ruta Flask autenticada → módulo de servicio de IA en el servidor → proveedor de modelo → validación de salida → respuesta al usuario.

- Nunca llames a la API de IA directamente desde JavaScript del navegador con una clave secreta.
- Guarda la clave como variable de entorno en Render (por ejemplo, `OPENAI_API_KEY`); no en GitHub, HTML ni `.env` versionado.
- Limita tamaño de entrada y salida, tiempo de espera, tasa de solicitudes y presupuesto.
- Envía solo los datos mínimos. Enmascara nombres, correos, teléfonos y direcciones cuando no sean necesarios.
- Trata el texto del usuario como datos no confiables; no permitas que instrucciones dentro de una solicitud cambien permisos, consulten datos ajenos o ejecuten acciones.
- La IA no debe asignar trabajos, cambiar estados, cobrar, rechazar clientes ni modificar la base por su cuenta. Esas acciones requieren reglas de servidor y confirmación autorizada.
- Registra metadatos técnicos y errores sin almacenar secretos ni conversaciones sensibles innecesarias.
- Proporciona alternativa manual cuando el proveedor no esté disponible.
- Informa al usuario cuándo interactúa con IA y establece una política de privacidad/retención apropiada.

## Paso a paso para añadir un modelo a Flask

### 1. Crear credenciales del proveedor
Crea una API key en el panel oficial del proveedor elegido. No reutilices ni publiques claves personales. Para OpenAI, consulta la documentación oficial: https://platform.openai.com/docs/ y https://platform.openai.com/docs/quickstart.

### 2. Añadir dependencia
En un entorno virtual de desarrollo instala el SDK del proveedor seleccionado. Si usas el SDK de OpenAI:

```powershell
pip install openai
pip freeze
```

Añade la dependencia compatible a `requirements.txt` mediante una revisión, sin sustituir las dependencias existentes.

### 3. Guardar secretos
En local agrega a `.env` (archivo ignorado por Git):

```env
OPENAI_API_KEY=tu_clave_real_local
OPENAI_MODEL=gpt-4.1-mini
```

El nombre del modelo disponible y su precio deben verificarse en la documentación actual del proveedor. En Render crea esas variables en **Environment**; no subas el archivo `.env`.

### 4. Crear un módulo de servicio aislado
Ejemplo ilustrativo, requiere el paquete `openai` y una clave válida. Verifica el modelo y la API con la documentación vigente antes de desplegar:

```python
# ai_service.py
import os
from openai import OpenAI

def mejorar_descripcion(texto: str) -> str:
    texto = (texto or "").strip()
    if not texto or len(texto) > 3000:
        raise ValueError("La descripción debe contener entre 1 y 3000 caracteres.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("La asistencia de IA no está configurada.")

    client = OpenAI(api_key=api_key, timeout=15.0, max_retries=1)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=(
            "Ayuda a mejorar la claridad de una solicitud de reparación doméstica. "
            "No inventes hechos, precios, diagnósticos ni urgencias. "
            "Devuelve solo una versión clara en español y conserva la incertidumbre."
        ),
        input=texto,
        max_output_tokens=250,
    )
    return response.output_text.strip()
```

Este ejemplo es una base de integración, no una garantía de compatibilidad permanente. Comprueba el SDK, el modelo disponible, los límites y los costos actuales.

### 5. Exponer una ruta Flask con límites
Crea una ruta `POST` que:
- valide longitud y tipo de entrada;
- aplique CSRF (por ejemplo, con Flask-WTF) y límites de frecuencia;
- exija sesión cuando corresponda;
- llame a `mejorar_descripcion` dentro de manejo de errores;
- devuelva texto sugerido para que el usuario lo revise;
- no guarde la salida hasta que el usuario confirme.

No envíes al modelo correo, teléfono, nombre ni dirección si solo necesita la descripción del trabajo.

### 6. Diseñar la experiencia de usuario
Añade un botón “Mejorar descripción con IA” junto al campo de detalles. Muestra carga, error recuperable, resultado editable y aviso de que la sugerencia puede equivocarse. El formulario normal debe seguir funcionando sin IA.

### 7. Pruebas y despliegue
- Prueba sin clave, con clave inválida, timeout, límite excedido y texto vacío.
- Prueba entradas maliciosas y textos que pidan revelar datos.
- Comprueba que no se filtren datos de otros clientes.
- Revisa logs, latencia, costo por petición y cuotas.
- Despliega primero en una rama/staging y configura la clave solo en el servicio de prueba.
- Añade pruebas automatizadas y un mecanismo para desactivar la función mediante una variable como `AI_ENABLED=false`.

## Ejemplo de variables de entorno

```env
AI_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
```

Empieza con `AI_ENABLED=false`. Activa la función solo cuando la ruta, validaciones, privacidad, presupuesto y pruebas estén listas.

## Criterios de aceptación de IA

- [ ] Sin clave, la aplicación sigue funcionando y muestra un mensaje útil.
- [ ] El secreto solo existe en el servidor.
- [ ] La IA no recibe datos personales innecesarios.
- [ ] El cliente puede editar/rechazar la sugerencia.
- [ ] La IA no modifica estados, asignaciones ni pagos.
- [ ] Hay límites de entrada, tiempo y frecuencia.
- [ ] Se han evaluado costo, precisión, sesgos y errores.
- [ ] La función puede apagarse sin redeplegar código.
