"""Servicio de IA de ServiHogar usando Gemini. La API key solo se lee del entorno del servidor."""
import os

from google import genai
from google.genai import types


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

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("AI_NOT_CONFIGURED")

    client = genai.Client(api_key=api_key)
    contents = []

    # Gemini usa el rol "model" para las respuestas del asistente.
    for item in (history or [])[-6:]:
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            content = content.strip()[:1000]
            if content:
                gemini_role = "user" if role == "user" else "model"
                contents.append(
                    types.Content(
                        role=gemini_role,
                        parts=[types.Part.from_text(text=content)],
                    )
                )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message[:1500])],
        )
    )

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            max_output_tokens=350,
            temperature=0.7,
        ),
    )

    answer = (response.text or "").strip()
    if not answer:
        raise RuntimeError("AI_EMPTY_RESPONSE")
    return answer[:4000]
