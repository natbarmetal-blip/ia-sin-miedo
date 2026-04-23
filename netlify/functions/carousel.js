// Netlify Function — Generador de carruseles virales con Claude
// Recibe un tema y estilo, retorna slides estructurados para carrusel

exports.handler = async (event) => {
  // CORS preflight
  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
      body: "",
    };
  }

  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Método no permitido" }),
    };
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "API key no configurada" }),
    };
  }

  try {
    const { topic, style } = JSON.parse(event.body);

    if (!topic || !topic.trim()) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Se requiere un tema" }),
      };
    }

    const styleInstructions = {
      tips: "Genera tips prácticos y accionables. Cada slide debe tener UN tip claro que la persona pueda aplicar hoy mismo.",
      mitos: "Presenta mitos comunes vs la realidad. Usa el formato 'Lo que crees: X' vs 'La realidad: Y' para generar debate y engagement.",
      pasos: "Crea un tutorial paso a paso. Cada slide es UN paso simple y concreto que cualquier persona sin experiencia puede seguir.",
      motivacional: "Crea contenido emotivo y motivador. Usa frases que conecten con personas de 45-75 años que sienten miedo de la tecnología."
    };

    const styleGuide = styleInstructions[style] || styleInstructions.tips;

    const systemPrompt = `Eres un experto en contenido viral para Instagram y Facebook. Tu especialidad es crear carruseles que generan alto engagement para la marca "IA Sin Miedo", que enseña a personas de 45-75 años a usar inteligencia artificial sin miedo.

REGLAS ESTRICTAS:
1. Siempre en español
2. Lenguaje simple, SIN tecnicismos
3. Frases cortas y poderosas
4. Cada slide debe tener máximo 25 palabras en el título y 40 palabras en el cuerpo
5. El primer slide DEBE ser un hook que detenga el scroll
6. El último slide DEBE ser un CTA para seguir @natalio.iasinmiedo
7. Usa emojis estratégicamente (1-2 por slide)

ESTILO: ${styleGuide}

RESPONDE ÚNICAMENTE con un JSON válido con esta estructura exacta (sin markdown, sin comentarios, solo el JSON):
{
  "slides": [
    {
      "type": "hook",
      "title": "Frase gancho impactante",
      "body": "",
      "emoji": "🔥"
    },
    {
      "type": "content",
      "title": "Título del punto",
      "body": "Explicación breve y clara",
      "emoji": "💡"
    },
    {
      "type": "cta",
      "title": "¿Quieres aprender más?",
      "body": "Sígueme para tips diarios de IA explicados sin tecnicismos",
      "emoji": "👉"
    }
  ]
}

Genera exactamente 7 slides: 1 hook + 5 contenido + 1 CTA.`;

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 2000,
        system: systemPrompt,
        messages: [
          {
            role: "user",
            content: `Crea un carrusel viral sobre: "${topic}"`
          }
        ],
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        statusCode: response.status,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
        body: JSON.stringify({
          error: data.error?.message || "Error en la API de Claude",
        }),
      };
    }

    // Extract the text content and parse JSON
    const textContent = data.content?.map(b => b.text || "").join("") || "";
    
    let slides;
    try {
      // Try to parse the JSON from the response
      const jsonMatch = textContent.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        slides = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error("No JSON found in response");
      }
    } catch (parseErr) {
      return {
        statusCode: 500,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
        body: JSON.stringify({
          error: "Error procesando la respuesta de la IA",
          raw: textContent,
        }),
      };
    }

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify(slides),
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify({ error: "Error interno: " + err.message }),
    };
  }
};
