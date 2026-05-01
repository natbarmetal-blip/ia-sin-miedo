#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de Investigacion de Trafico — La IA Sin Miedo
Analiza tendencias, YouTube y competencia para decirte donde y como publicar.
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path

import anthropic

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Dependencias opcionales ────────────────────────────────────────────────────

def check_dependencies():
    missing = []
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")
    return missing


def install_dependencies(packages):
    import subprocess
    for pkg in packages:
        print(f"Instalando {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])


# ── Recoleccion de datos ───────────────────────────────────────────────────────

def obtener_sugerencias_google(tema: str) -> dict:
    """Obtiene sugerencias y keywords relacionadas de Google Autocomplete."""
    import urllib.request
    import urllib.parse

    sugerencias = []
    variaciones = [tema, tema + " para", tema + " como", tema + " gratis", tema + " espanol"]

    for variacion in variaciones:
        try:
            encoded = urllib.parse.quote(variacion)
            url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={encoded}&hl=es&gl=es-419"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if len(data) > 1:
                    sugerencias.extend(data[1])
        except Exception:
            continue

    # Eliminar duplicados y el tema original
    sugerencias_unicas = list(dict.fromkeys(
        s for s in sugerencias if s.lower() != tema.lower()
    ))[:20]

    return {
        "sugerencias": sugerencias_unicas,
        "total": len(sugerencias_unicas),
        "status": "ok" if sugerencias_unicas else "sin_datos"
    }


def buscar_youtube(tema: str, max_resultados: int = 10) -> list:
    """Busca videos de YouTube relacionados al tema usando yt-dlp."""
    try:
        import yt_dlp
        query = f"ytsearch{max_resultados}:{tema} espanol"
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

        videos = []
        for v in info.get('entries', []):
            if v:
                videos.append({
                    "titulo": v.get('title', ''),
                    "canal": v.get('channel', v.get('uploader', '')),
                    "vistas": str(v.get('view_count', 0)),
                    "duracion": str(v.get('duration', '')),
                    "descripcion": v.get('description', '')[:200] if v.get('description') else ''
                })
        return videos
    except Exception as e:
        return []


# ── Analisis con Claude ────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres un estratega de contenido digital especializado en crecimiento orgánico para
creadores hispanohablantes. Tu especialidad es analizar datos de tendencias y competencia para dar
recomendaciones concretas y accionables.

El proyecto es "La IA Sin Miedo" — una marca que enseña a personas mayores de 45 años a usar
herramientas de inteligencia artificial en su vida diaria y su trabajo, sin tecnicismos y sin miedo.

Audiencia objetivo: personas hispanohablantes mayores de 45 años que no se consideran "de tecnología",
sienten confusión o miedo ante la IA, y quieren entender cómo puede ayudarles en su vida real y su
trabajo, sin necesidad de saber programación.

Herramientas que enseña la marca (SOLO estas 4): ChatGPT, Canva AI, CapCut, Suno.

Canales principales: Instagram, Facebook, YouTube, TikTok, newsletter por email.

Siempre das recomendaciones específicas, con ejemplos concretos orientados a esta audiencia mayor,
priorizadas por impacto."""


def analizar_con_claude(client: anthropic.Anthropic, tema: str,
                         tendencias: dict, videos_youtube: list) -> str:
    """Claude analiza todos los datos y genera el reporte estrategico."""

    # Preparar contexto de datos
    datos_tendencias = json.dumps(tendencias, ensure_ascii=False, indent=2)
    datos_youtube = json.dumps(videos_youtube[:8], ensure_ascii=False, indent=2)

    prompt = f"""Analiza estos datos de investigación para el tema: "{tema}"

## KEYWORDS Y SUGERENCIAS DE GOOGLE
{datos_tendencias}

## VIDEOS MAS POPULARES EN YOUTUBE (en español)
{datos_youtube}

---

Con base en estos datos, genera un REPORTE ESTRATÉGICO completo con estas secciones:

## 1. OPORTUNIDAD DEL TEMA
- ¿Qué tan buscado está este tema? ¿Va en crecimiento o bajando?
- ¿Vale la pena crear contenido sobre esto ahora?

## 2. KEYWORDS Y HASHTAGS
- 10 hashtags más efectivos para Instagram (mezcla español/inglés)
- 5 variaciones del tema para usar como keywords en títulos
- Palabras clave en tendencia relacionadas

## 3. LO QUE FUNCIONA EN YOUTUBE
- ¿Qué formatos/ángulos tienen más vistas?
- ¿Qué tienen en común los títulos exitosos?
- ¿Qué duración funciona mejor?

## 4. ÁNGULOS DE CONTENIDO GANADORES
- 5 ángulos específicos para posts de Instagram/TikTok
- 3 ideas para hilos de X (Twitter)
- 2 ideas para videos cortos (Reels/TikTok)

## 5. PLAN DE PUBLICACIÓN
- ¿En qué red social empezar para máximo impacto?
- Frecuencia recomendada
- Mejor momento para publicar (días/horarios generales)

## 6. PRÓXIMOS PASOS (priorizado)
Lista de 5 acciones concretas ordenadas por impacto inmediato

Sé específico, práctico y directo. Nada de teoría genérica."""

    print("\r Analizando datos con IA...                    ", end='', flush=True)

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

    print("\r Analisis completado                           ")
    return next(b.text for b in resultado.content if b.type == "text")


# ── Guardado ───────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
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


def guardar_reporte(tema: str, reporte: str, datos_raw: dict) -> Path:
    hoy = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(tema)
    carpeta = Path("output") / f"{hoy}_investigacion_{slug}"
    carpeta.mkdir(parents=True, exist_ok=True)

    (carpeta / "reporte.md").write_text(reporte, encoding="utf-8")
    (carpeta / "datos_raw.json").write_text(
        json.dumps(datos_raw, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return carpeta


# ── Punto de entrada ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Agente de Investigacion de Trafico - La IA Sin Miedo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Ejemplo: python agente_investigacion.py "ChatGPT para freelancers"'
    )
    parser.add_argument("tema", nargs="?", help="Tema o keyword a investigar")
    args = parser.parse_args()

    tema = args.tema
    if not tema:
        print("\nAgente de Investigacion de Trafico - La IA Sin Miedo\n")
        tema = input("Que tema quieres investigar? -> ").strip()
        if not tema:
            print("Necesitas ingresar un tema.")
            sys.exit(1)

    print(f"\nInvestigando: \"{tema}\"\n")

    # Verificar e instalar dependencias
    faltantes = check_dependencies()
    if faltantes:
        print(f"Instalando dependencias necesarias: {', '.join(faltantes)}")
        install_dependencies(faltantes)
        print()

    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY no encontrada.")
        print("Ejecuta: $env:ANTHROPIC_API_KEY = 'tu-clave-aqui'")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    # Recolectar datos
    print("Consultando sugerencias de Google...          ", end='', flush=True)
    tendencias = obtener_sugerencias_google(tema)
    if tendencias.get('status') == 'ok':
        print(f"\r Google: {tendencias['total']} keywords relacionadas encontradas")
    else:
        print(f"\r Google: sin datos")

    print("Buscando en YouTube...                        ", end='', flush=True)
    videos = buscar_youtube(tema)
    print(f"\r YouTube: {len(videos)} videos analizados              ")

    # Analizar con Claude
    reporte = analizar_con_claude(client, tema, tendencias, videos)

    # Guardar
    datos_raw = {"tendencias": tendencias, "videos_youtube": videos}
    carpeta = guardar_reporte(tema, reporte, datos_raw)

    print(f"""
----------------------------------------------------
Investigacion completada

Carpeta: {carpeta}/
  reporte.md      <- tu plan estrategico
  datos_raw.json  <- datos originales

----------------------------------------------------
""")

    # Mostrar resumen del reporte
    lineas = reporte.split('\n')
    print('\n'.join(lineas[:30]))
    if len(lineas) > 30:
        print(f"\n... (abre reporte.md para ver el reporte completo)")


if __name__ == "__main__":
    main()
