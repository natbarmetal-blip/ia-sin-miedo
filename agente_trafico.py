#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de Tráfico Orgánico — La IA Sin Miedo
Genera paquetes de contenido completos a partir de un tema o keyword.
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path

import anthropic

# Forzar UTF-8 en Windows para que los emojis no rompan la consola
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Configuración ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres el cerebro creativo de "La IA Sin Miedo", una marca que enseña a personas
mayores de 45 años a usar inteligencia artificial en su vida diaria y su trabajo, sin tecnicismos,
sin miedo y sin complicaciones.

VOZ DE MARCA
- Tono: cálido, paciente y cercano. Como un hijo o amigo que le explica tecnología a sus padres con
  mucho cariño y sin apuro.
- Nunca usas términos técnicos. Si no hay forma de evitarlos, los explicas con una analogía simple.
- Empoderas, no abrumas. Cada pieza deja al lector pensando "esto sí puedo hacerlo yo, hoy mismo".
- Usas ejemplos del día a día de una persona de 50-65 años: organizar el negocio familiar, escribir
  un email importante, preparar una presentación, ahorrar tiempo en tareas repetitivas.
- Nunca haces sentir tonto al lector. Al contrario: lo haces sentir capaz y moderno.

AUDIENCIA
Personas hispanohablantes mayores de 45 años que:
- No se consideran "de tecnología" y sienten miedo o confusión ante la IA
- Han escuchado hablar de ChatGPT pero no saben para qué sirve en su vida real
- Quieren entender cómo la IA puede ayudarles sin tener que aprender programación
- Valoran la simplicidad, la paciencia y los ejemplos concretos de la vida real

HERRAMIENTAS PERMITIDAS (usa SOLO estas 4, nunca menciones otras):
- ChatGPT
- Canva AI
- CapCut
- Suno

PRINCIPIOS DE CONTENIDO
1. Empieza siempre con una situación real que esta persona vive o siente
2. Ofrece valor concreto: un paso, un tip, una acción que puedan hacer hoy
3. Usa un lenguaje simple, frases cortas, sin jerga
4. CTAs directos y amables, nunca agresivos
5. Hashtags relevantes en español para máximo alcance

Cuando generes contenido, sigue exactamente el formato solicitado. Cada sección debe estar claramente
delimitada con los encabezados indicados."""

# ── Helpers ────────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convierte texto a slug para nombre de carpeta."""
    text = text.lower().strip()
    text = re.sub(r'[áàä]', 'a', text)
    text = re.sub(r'[éèë]', 'e', text)
    text = re.sub(r'[íìï]', 'i', text)
    text = re.sub(r'[óòö]', 'o', text)
    text = re.sub(r'[úùü]', 'u', text)
    text = re.sub(r'ñ', 'n', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text[:50]


def print_progress(message: str, done: bool = False):
    """Imprime progreso en una sola línea."""
    if done:
        print(f"\r✅ {message:<60}")
    else:
        print(f"\r⏳ {message:<60}", end='', flush=True)


def get_client() -> anthropic.Anthropic:
    """Inicializa el cliente de Anthropic con validación de API key."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ Error: ANTHROPIC_API_KEY no encontrada.")
        print("   Creá un archivo .env con tu API key o exportá la variable:")
        print("   export ANTHROPIC_API_KEY=tu_clave_aqui\n")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


# ── Generación de contenido ────────────────────────────────────────────────────

def generar_articulo(client: anthropic.Anthropic, tema: str) -> str:
    """Genera artículo SEO optimizado."""
    print_progress("Generando artículo SEO...")

    prompt = f"""Escribe un artículo SEO completo sobre el tema: "{tema}"

REQUISITOS:
- Longitud: 900-1100 palabras
- Keyword principal: {tema}
- Incluye una meta descripción al inicio (máx 160 caracteres)
- Estructura con H1, H2 y H3 usando markdown (#, ##, ###)
- Primer párrafo: engancha con el problema real del lector
- Incluye al menos 3 consejos o pasos prácticos
- Cierra con un CTA suave hacia el newsletter o los recursos de "La IA Sin Miedo"
- Optimizado para búsqueda en Google en español

FORMATO DE SALIDA:
---META---
[meta descripción aquí]
---ARTICULO---
[artículo completo en markdown]"""

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        resultado = stream.get_final_message()

    print_progress("Artículo SEO listo", done=True)
    return next(b.text for b in resultado.content if b.type == "text")


def generar_posts_redes(client: anthropic.Anthropic, tema: str) -> str:
    """Genera 3 posts para Instagram/LinkedIn."""
    print_progress("Generando posts para redes sociales...")

    prompt = f"""Crea 3 posts diferentes para Instagram y LinkedIn sobre el tema: "{tema}"

Cada post debe ser distinto en formato y ángulo. Usa estas variantes:
- Post 1: Formato lista (tips o pasos)
- Post 2: Historia/anécdota breve + aprendizaje
- Post 3: Pregunta provocadora + respuesta

ESTRUCTURA DE CADA POST:
🪝 HOOK: (primera línea que detiene el scroll)
📝 CUERPO: (2-4 párrafos cortos)
📣 CTA: (llamada a la acción clara)
#️⃣ HASHTAGS: (15-20 hashtags mezclados español/inglés)

---SEPARADOR ENTRE POSTS---

Empieza cada post con "## POST [número]: [tipo]" """

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        resultado = stream.get_final_message()

    print_progress("Posts de redes sociales listos", done=True)
    return next(b.text for b in resultado.content if b.type == "text")


def generar_hilo_x(client: anthropic.Anthropic, tema: str) -> str:
    """Genera hilo para X (Twitter)."""
    print_progress("Generando hilo para X (Twitter)...")

    prompt = f"""Crea un hilo de Twitter/X sobre el tema: "{tema}"

REQUISITOS:
- Entre 6 y 8 tweets
- Tweet 1: Hook irresistible que haga querer leer el resto (promete el valor)
- Tweets 2-6: Desarrollo con puntos concretos, uno por tweet
- Tweet 7 (opcional): Ejemplo real o caso práctico
- Tweet final: CTA + invitación a seguir para más contenido sobre IA

REGLAS:
- Cada tweet máximo 280 caracteres (¡cuenta bien!)
- Numera los tweets: 1/, 2/, etc.
- Usa emojis estratégicamente, no en exceso
- Cada tweet debe funcionar solo si alguien lo ve fuera del hilo

FORMATO:
## HILO: [título descriptivo]

1/ [texto del tweet]

2/ [texto del tweet]
[continúa...]"""

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        resultado = stream.get_final_message()

    print_progress("Hilo de X listo", done=True)
    return next(b.text for b in resultado.content if b.type == "text")


def generar_email(client: anthropic.Anthropic, tema: str) -> str:
    """Genera email para newsletter."""
    print_progress("Generando email para newsletter...")

    prompt = f"""Escribe un email para el newsletter de "La IA Sin Miedo" sobre el tema: "{tema}"

ESTRUCTURA:
**ASUNTO:** [línea de asunto persuasiva, máx 50 caracteres]
**PREHEADER:** [texto previo, máx 90 caracteres]

---CUERPO---

**Saludo:** Personalizado pero breve

**Párrafo de apertura:** Conecta con un problema o situación cotidiana del lector
(2-3 oraciones máximo)

**Cuerpo principal:**
- El tema central con valor concreto
- 2-3 párrafos cortos o una lista de puntos clave
- Máx 300 palabras en el cuerpo

**CTA principal:** Un solo llamado a la acción claro (puede ser a un recurso,
artículo, herramienta o simplemente responder el email)

**Cierre:** Cálido, como despedirte de un amigo

**Firma:**
Natalio
La IA Sin Miedo 🤖

---

P.D.: [posdata opcional con un tip bonus o pregunta para generar respuestas]"""

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        resultado = stream.get_final_message()

    print_progress("Email listo", done=True)
    return next(b.text for b in resultado.content if b.type == "text")


# ── Guardado y registro ────────────────────────────────────────────────────────

def guardar_contenido(tema: str, articulo: str, posts: str, hilo: str, email: str) -> Path:
    """Guarda todos los archivos en la carpeta de output."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(tema)
    carpeta = Path("output") / f"{hoy}_{slug}"
    carpeta.mkdir(parents=True, exist_ok=True)

    (carpeta / "articulo.md").write_text(articulo, encoding="utf-8")
    (carpeta / "posts_redes.md").write_text(posts, encoding="utf-8")
    (carpeta / "hilo_x.md").write_text(hilo, encoding="utf-8")
    (carpeta / "email.md").write_text(email, encoding="utf-8")

    return carpeta


def registrar_historial(tema: str, carpeta: Path):
    """Agrega entrada al historial JSON."""
    historial_path = Path("historial.json")

    if historial_path.exists():
        with open(historial_path, encoding="utf-8") as f:
            historial = json.load(f)
    else:
        historial = []

    historial.append({
        "fecha": datetime.now().isoformat(),
        "tema": tema,
        "carpeta": str(carpeta),
        "archivos": ["articulo.md", "posts_redes.md", "hilo_x.md", "email.md"]
    })

    with open(historial_path, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)


# ── Punto de entrada ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Agente de Trafico Organico - La IA Sin Miedo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplo: python agente_trafico.py \"cómo usar ChatGPT para escribir emails\""
    )
    parser.add_argument(
        "tema",
        nargs="?",
        help="Tema o keyword para generar el contenido"
    )
    args = parser.parse_args()

    # Si no se pasó tema, pedirlo interactivo
    tema = args.tema
    if not tema:
        print("\n🤖 Agente de Tráfico Orgánico — La IA Sin Miedo\n")
        tema = input("¿Sobre qué tema querés generar contenido? → ").strip()
        if not tema:
            print("❌ Necesitás ingresar un tema.")
            sys.exit(1)

    print(f"\n🚀 Generando paquete de contenido para: \"{tema}\"\n")

    # Cambiar al directorio del script para que los paths sean correctos
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    client = get_client()

    # Generar todo el contenido
    articulo = generar_articulo(client, tema)
    posts = generar_posts_redes(client, tema)
    hilo = generar_hilo_x(client, tema)
    email = generar_email(client, tema)

    # Guardar archivos
    print_progress("Guardando archivos...")
    carpeta = guardar_contenido(tema, articulo, posts, hilo, email)
    print_progress("Archivos guardados", done=True)

    # Registrar en historial
    registrar_historial(tema, carpeta)

    # Resumen final
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Paquete de contenido generado con éxito

📁 Carpeta: {carpeta}/
   ├── articulo.md       (SEO, ~1000 palabras)
   ├── posts_redes.md    (3 posts Instagram/LinkedIn)
   ├── hilo_x.md         (hilo de Twitter/X)
   └── email.md          (newsletter)

📋 Historial actualizado en historial.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == "__main__":
    main()
