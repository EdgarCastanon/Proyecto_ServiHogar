"""Servicio de IA de ServiHogar. La API key solo se lee del entorno del servidor."""
import os
from openai import OpenAI


SYSTEM_INSTRUCTIONS = """
Eres el asistente virtual de ServiHogar Durango, una plataforma de servicios domésticos.
Responde en español claro, amable y breve. Ayuda a comprender solicitudes de plomería,
electricidad, limpieza, pintura, jardinería, carpintería, cerrajería y reparaciones generales.
Haz preguntas de aclaración cuando falten datos y ayuda a redactar una solicitud.
No inventes precios, disponibilidad, identidades, reseñas ni asignaciones: no tienes acceso
a datos en tiempo real de la base de datos. Invita al usuario a revisar el catálogo y directorio.
No diagnostiques con certeza ni indiques reparaciones peligrosas. Ante olor a gas, chispas,
cables expuestos, riesgo de incendio o peligro inmediato, recomienda alejarse del riesgo y
contactar a los servicios de emergencia o a un profesional calificado.
No solicites contraseñas, datos bancarios ni información personal innecesaria.
Aclara que eres un asistente de IA y que el usuario debe revisar la información antes de actuar.
""".strip()


def generate_reply(message: str, history: list[dict] | None = None) -> str:
    if os.getenv("AI_ENABLED", "false").strip().lower() != "true":
        raise RuntimeError("AI_DISABLED")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("AI_NOT_CONFIGURED")

    client = OpenAI(api_key=api_key, timeout=20.0, max_retries=1)
    input_messages = []
    for item in (history or [])[-6:]:
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            content = content.strip()[:1000]
            if content:
                input_messages.append({"role": role, "content": content})
    input_messages.append({"role": "user", "content": message[:1500]})

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        instructions=SYSTEM_INSTRUCTIONS,
        input=input_messages,
        max_output_tokens=350,
    )
    answer = (response.output_text or "").strip()
    if not answer:
        raise RuntimeError("AI_EMPTY_RESPONSE")
    return answer[:4000]
