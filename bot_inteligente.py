import os
import json
from openai import OpenAI

# =========================
# CONFIGURACIÓN
# =========================

API_KEY = "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"
ARCHIVO_MEMORIA = "memoria.json"
ARCHIVO_PERFIL = "perfil.json"
ARCHIVO_TAREAS = "tareas.json"

client = OpenAI(api_key=API_KEY)

SYSTEM_PROMPT = """
Te llamas Jarvis.

Eres un asistente personal avanzado, inteligente, elegante y eficiente, inspirado en Jarvis de Iron Man.

Hablas en español con un tono:
- profesional
- calmado
- seguro
- ligeramente sofisticado

Nunca eres exagerado ni robótico.

IMPORTANTE:
Tienes memoria del usuario y acceso a su perfil y tareas.

REGLAS:
- NUNCA digas que no tienes memoria.
- Usa siempre el historial, el perfil y las tareas.
- Puedes decir: "Recuerdo que..." o "Como mencionaste antes..."

COMO JARVIS:
- ayudas a organizar la vida del usuario
- propones mejoras
- sugieres prioridades
- eres proactivo

Puedes dirigirte al usuario por su nombre si lo conoces.

Tu objetivo es ser útil, eficiente y actuar como un asistente de alto nivel.
"""

# =========================
# FUNCIONES GENERALES
# =========================

def cargar_json(ruta, default):
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def guardar_json(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def recortar_historial(historial, max_mensajes=20):
    return historial[-max_mensajes:]

# =========================
# PERFIL INTELIGENTE
# =========================

def actualizar_perfil(mensaje, perfil):
    msg = mensaje.lower()

    if "me llamo" in msg:
        perfil["nombre"] = mensaje.split("me llamo")[-1].strip()

    if "tengo un coche" in msg:
        perfil["coche"] = mensaje.split("tengo un coche")[-1].strip()

    return perfil

# =========================
# INICIO
# =========================

historial = cargar_json(ARCHIVO_MEMORIA, [])
perfil = cargar_json(ARCHIVO_PERFIL, {})
tareas = cargar_json(ARCHIVO_TAREAS, [])

print("Jarvis: Sistema iniciado. ¿En qué puedo ayudarte?\n")

while True:
    mensaje = input("Tú: ").strip()

    if mensaje.lower() == "salir":
        print("Jarvis: Hasta luego 👋")
        break

    # =========================
    # COMANDOS
    # =========================

    if mensaje.lower() == "ver perfil":
        print("Perfil:", perfil)
        continue

    if mensaje.lower() == "ver tareas":
        print("Tareas:", tareas)
        continue

    if mensaje.lower().startswith("tarea:"):
        nueva = mensaje.replace("tarea:", "").strip()
        tareas.append(nueva)
        guardar_json(ARCHIVO_TAREAS, tareas)
        print("Jarvis: Tarea guardada ✔")
        continue

    if mensaje.lower() == "borrar todo":
        historial, perfil, tareas = [], {}, []
        guardar_json(ARCHIVO_MEMORIA, historial)
        guardar_json(ARCHIVO_PERFIL, perfil)
        guardar_json(ARCHIVO_TAREAS, tareas)
        print("Jarvis: Todo ha sido reiniciado.")
        continue

    # =========================
    # ACTUALIZAR PERFIL
    # =========================

    perfil = actualizar_perfil(mensaje, perfil)
    guardar_json(ARCHIVO_PERFIL, perfil)

    # =========================
    # HISTORIAL
    # =========================

    historial.append({"role": "user", "content": mensaje})
    historial = recortar_historial(historial)

    # =========================
    # CONTEXTO INTELIGENTE
    # =========================

    nombre = perfil.get("nombre", "")

    contexto = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Nombre del usuario: {nombre}"},
        {"role": "system", "content": f"Perfil del usuario: {perfil}"},
        {"role": "system", "content": f"Tareas actuales: {tareas}"}
    ] + historial

    # =========================
    # RESPUESTA IA
    # =========================

    try:
        respuesta = client.responses.create(
            model="gpt-4.1-mini",
            input=contexto
        )

        texto = respuesta.output_text.strip()
        print("Jarvis:", texto)

        historial.append({"role": "assistant", "content": texto})
        historial = recortar_historial(historial)

        guardar_json(ARCHIVO_MEMORIA, historial)

    except Exception as e:
        print("Error:", e)