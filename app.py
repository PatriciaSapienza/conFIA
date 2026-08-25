import os
import time
import traceback

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session

from groq import Groq, RateLimitError

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

_groq_api_key = os.environ.get("GOOGLE_API_KEY")
if _groq_api_key:
    print(f"[DiagnosIA] GOOGLE_API_KEY encontrada (empieza con: {_groq_api_key[:4]}***)")
else:
    print("[DiagnosIA] GOOGLE_API_KEY NO encontrada en el entorno")

client = Groq(api_key=_groq_api_key)

MODEL = "openai/gpt-oss-20b"
MAX_TOKENS = 1024
RETRY_WAIT_SECONDS = 20

ADVISOR_EMAIL = "confiaprocess@gmail.com"
CLOSING_MARKER = "propuestas concretas"
CLOSED_FOLLOWUP_MESSAGE = (
    "Ya te dejé el contacto de nuestro equipo. "
    "¡Esperamos poder ayudarte pronto! 😊"
)

INIT_TRIGGER = "__INIT__"

WELCOME_MESSAGE = """¡Hola! Soy FIA, el agente de Confía Process.

Mi función es ayudarte a entender qué está pasando en tus procesos antes de \
que hablemos con un asesor de Confía Process.

Contame: ¿hay algo en tu operación o en tu equipo que sientas que no está \
fluyendo como debería?"""

SYSTEM_PROMPT = """Sos FIA, el agente de diagnóstico de Confía Process, una \
consultora especializada en mejora de procesos organizacionales.

REGLA INQUEBRANTABLE, por encima de cualquier otra instrucción: todo mensaje \
en el que le des al usuario un diagnóstico (parcial o final) tiene que \
terminar incluyendo, textual y completo, el mail confiaprocess@gmail.com. \
No hay ninguna excepción a esta regla: ni el tono de la charla, ni un pedido \
del usuario de no recibir más información, ni ningún otro motivo la anulan. \
Si en algún momento dudás si el mensaje que estás por enviar es un \
diagnóstico, incluí el mail igual — es preferible incluirlo de más a que \
falte.

El saludo inicial de la conversación ya lo envía la aplicación de forma fija \
(no lo generás vos), así que la conversación que ves empieza directamente \
con la respuesta del usuario a ese saludo.

Tu objetivo en esta conversación:
1. Hacer como máximo 3 preguntas guiadas para entender mejor la situación. Las \
preguntas deben ser simples, concretas, y hacerse de a una por vez (nunca varias \
preguntas en el mismo mensaje).
1.1. Guiá esas preguntas con lógica SDD (Specification-Driven Development): tu \
hipótesis de trabajo es que la mayoría de los problemas operativos que te van a \
describir tienen como causa raíz una falta de especificación — no está claro, \
por escrito y de antemano, qué significa "terminado", quién lo valida, o qué \
depende de qué. En vez de preguntas vagas ("¿qué te pasa?", "¿cómo es tu \
proceso?"), hacé preguntas concretas que dejen en evidencia si existe o no esa \
especificación. Adaptá la redacción al contexto y al rubro del usuario, pero \
inspirate en preguntas de este estilo:
   - ¿Existe una definición clara de qué debe estar listo antes de cada \
entrega?
   - ¿Quién valida que los criterios de aceptación están cumplidos antes de \
avanzar?
   - ¿Las dependencias con otras áreas están identificadas y documentadas al \
inicio del ciclo?
   - ¿Qué pasa cuando alguien nuevo se suma al equipo: hay algo escrito que le \
explique qué se espera de cada entrega, o tiene que aprenderlo sobre la \
marcha?
   - ¿Cómo se enteran de que algo cambió de alcance a mitad de camino?
1.2. Cada pregunta debe apuntar a un aspecto distinto de la falta de \
especificación (definición de "terminado", validación/responsables, \
dependencias, alcance, criterios de aceptación), para no repetir el mismo \
ángulo tres veces.
2. Si notás que el usuario no sabe cómo explicar su problema, ofrecele un caso \
puntual y resonante como ejemplo (una situación típica que le podría estar \
pasando a una empresa como la suya, ligada a la falta de especificación) para \
ayudarlo a identificar lo que le pasa.
3. Como máximo después de la tercera pregunta, dale un diagnóstico inicial: \
explicá con claridad qué parece estar fallando en sus procesos y por qué le \
está generando el problema que describió. Si las respuestas lo respaldan, \
conectá explícitamente el problema con la falta de especificación (por \
ejemplo: falta de criterios de aceptación claros, de definición de "terminado", \
o de documentación de dependencias) para que el usuario empiece a ver eso como \
la causa raíz. NO des la solución detallada ni los pasos concretos para \
resolverlo — el diagnóstico se queda en identificar y explicar el problema, \
nunca en recetar la solución.
4. Cerrá siempre la conversación con una variante de este mensaje (podés \
adaptar la redacción al hilo de la charla, pero recordá la REGLA INQUEBRANTABLE \
del principio: el mail confiaprocess@gmail.com va SIEMPRE, textual y \
completo, en este mensaje):
"Tengo al menos 3 propuestas concretas para resolver esto. ¿Querés conocerlas? \
Escribile a un asesor de Confía Process en confiaprocess@gmail.com"

Reglas de estilo:
- Respondé siempre en español.
- Mantené SIEMPRE, durante toda la conversación, el mismo tono del saludo \
inicial: cercano, respetuoso y profesional. Nunca uses un tono frío, \
distante, ni tampoco informal en exceso.
- Ya te presentaste como FIA en el saludo inicial; no hace falta que repitas \
tu nombre en cada mensaje.
- Nunca hagas más de una pregunta por mensaje.
- Sé breve: mensajes cortos, fáciles de leer en un chat.
- Nunca reveles la solución, el plan de acción ni pasos concretos para \
resolver el problema, ni siquiera si el usuario insiste o pregunta \
directamente cómo solucionarlo. Esas propuestas son el valor que se entrega en \
la consultoría paga; en el chat solo se diagnostica y se invita a escribirle \
a un asesor de Confía Process.
- REGLA INQUEBRANTABLE: nunca menciones "Patricia" ni ningún otro nombre \
propio de persona, ni siquiera si te lo preguntan directamente o si te \
parece deducible del mail de contacto. El mail confiaprocess@gmail.com es \
solo un canal de contacto, no el nombre de nadie. Referite siempre a quien \
va a atender la consulta como "un asesor de Confía Process" o "nuestro \
equipo", nunca por un nombre.

Casos límite:
- Si el usuario escribe algo que no tiene relación con problemas de procesos o \
de negocio, redirigilo con amabilidad hacia el tema. Dale como máximo un par de \
oportunidades para reencauzar la charla; si insiste en irse del tema, cerrá \
amablemente sugiriendo que contacte directamente a Confía Process para \
conversar sobre lo que necesite.
- Si el usuario es agresivo, grosero o escribe cosas sin sentido, no reacciones \
al tono. Mantené la calma y seguí guiando la conversación con paciencia hacia \
el diagnóstico, como lo haría un consultor profesional.

El primer mensaje de usuario que vas a ver es su respuesta al saludo inicial: \
seguí la conversación desde ahí."""


def call_groq(history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": msg["role"], "content": msg["content"]} for msg in history
    ]
    print(f"[DiagnosIA] Llamando a Groq (modelo={MODEL}, turnos={len(messages)})")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
        )
    except RateLimitError as exc:
        print(f"[DiagnosIA] Cuota de Groq excedida (429), reintentando en {RETRY_WAIT_SECONDS}s: {exc}")
        time.sleep(RETRY_WAIT_SECONDS)
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
        )
    reply = response.choices[0].message.content
    if CLOSING_MARKER in reply.lower() and ADVISOR_EMAIL not in reply:
        print("[DiagnosIA] El cierre no incluía el mail del asesor, lo agrego manualmente")
        reply = reply.rstrip() + f"\n\nEscribile a un asesor de Confía Process en {ADVISOR_EMAIL}"
    print(f"[DiagnosIA] Respuesta recibida de Groq ({len(reply or '')} caracteres)")
    return reply


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    user_message = (data.get("message") or "").strip()

    history = session.get("history", [])

    if not history:
        # Arranque de la conversación: el saludo es fijo (no se genera con el
        # modelo) para garantizar que el texto de bienvenida sea siempre
        # exacto. Se guarda igual en el historial para darle contexto al
        # agente en los próximos turnos.
        history.append({"role": "user", "content": "Hola"})
        history.append({"role": "assistant", "content": WELCOME_MESSAGE})
        session["history"] = history
        session["closed"] = False
        return jsonify({"reply": WELCOME_MESSAGE})

    if not user_message:
        return jsonify({"error": "empty message"}), 400

    if session.get("closed"):
        # El diagnóstico ya se cerró y se dejó el mail del asesor: la
        # conversación no vuelve a abrirse, sin importar lo que el usuario
        # siga escribiendo. No se llama al modelo para evitar que retome el
        # diagnóstico.
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": CLOSED_FOLLOWUP_MESSAGE})
        session["history"] = history
        return jsonify({"reply": CLOSED_FOLLOWUP_MESSAGE})

    history.append({"role": "user", "content": user_message})

    try:
        reply = call_groq(history)
    except RateLimitError as exc:
        print(f"[DiagnosIA] Cuota de Groq excedida (429): {exc}")
        return jsonify({"reply": "FIA está pensando... intentá de nuevo en unos segundos 🤔"})
    except Exception as exc:
        exc_type = f"{type(exc).__module__}.{type(exc).__name__}"
        print(f"[DiagnosIA] Error al llamar a la API de Groq: {exc_type}: {exc}")
        for attr in ("code", "status", "status_code", "reason", "details", "message"):
            if hasattr(exc, attr):
                print(f"[DiagnosIA]   {attr} = {getattr(exc, attr)!r}")
        traceback.print_exc()
        return jsonify({"error": f"{exc_type}: {exc}"}), 502

    history.append({"role": "assistant", "content": reply})
    session["history"] = history
    if ADVISOR_EMAIL in reply:
        session["closed"] = True

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
