// Netlify Function — Generador de Reels virales con Claude
// Recibe un tema, estilo y duración, retorna escenas estructuradas para Reel

exports.handler = async (event) => {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };

  // CORS preflight
  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers: corsHeaders, body: "" };
  }

  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      headers: { "Content-Type": "application/json", ...corsHeaders },
      body: JSON.stringify({ error: "Método no permitido" }),
    };
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json", ...corsHeaders },
      body: JSON.stringify({ error: "API key no configurada" }),
    };
  }

  try {
    const { topic, style, duration } = JSON.parse(event.body);

    if (!topic || !topic.trim()) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders },
        body: JSON.stringify({ error: "Se requiere un tema" }),
      };
    }

    // Scene count based on duration
    const sceneCount = {
      short: 4,
      medium: 6,
      long: 10,
    }[duration] || 6;

    const styleInstructions = {
      tips: "Genera tips prácticos y accionables. Cada escena debe tener UN consejo claro y directo. Usa verbos de acción. El hook debe ser una pregunta provocadora o un dato sorprendente.",
      storytelling: "Crea una narrativa emocional paso a paso. Comienza con un problema relatable, desarrolla la historia, y cierra con una solución o moraleja. El tono debe ser íntimo, como si hablaras con un amigo.",
      polemico: "Presenta afirmaciones atrevidas y contraintuitivas que generen debate. Usa el formato 'Lo que todos creen vs lo que realmente pasa'. El hook debe ser controversial pero respetuoso. Genera curiosidad y ganas de comentar.",
      motivacional: "Crea contenido emotivo y empoderador. Usa frases cortas y poderosas que conecten con personas de 45-75 años. Cada escena debe construir sobre la anterior hacia un mensaje de esperanza y acción.",
    };

    const styleGuide = styleInstructions[style] || styleInstructions.tips;

    const systemPrompt = `Eres un experto en contenido viral para Reels de Instagram, TikTok y Facebook. Tu especialidad es crear guiones de video corto que generan millones de vistas para la marca "IA Sin Miedo", que enseña a personas de 45-75 años a usar inteligencia artificial sin miedo.

REGLAS ESTRICTAS:
1. Siempre en español
2. Lenguaje ultra simple, SIN tecnicismos
3. Frases CORTAS y PODEROSAS — cada palabra debe contar
4. El texto principal ("text") debe tener MÁXIMO 10 palabras — es lo que aparece en grande en pantalla
5. El subtexto ("subtext") debe tener MÁXIMO 18 palabras — aparece más pequeño debajo
6. La primera escena DEBE ser un hook brutal que detenga el scroll en el primer segundo
7. La última escena DEBE ser un CTA para seguir @natalio.iasinmiedo
8. Usa UN emoji por escena que refuerce el mensaje
9. El contenido debe fluir como una narrativa — cada escena conecta con la siguiente
10. Piensa en cómo se VE en pantalla: texto grande, fondo de color, lectura rápida

ESTILO: ${styleGuide}

RESPONDE ÚNICAMENTE con un JSON válido con esta estructura exacta (sin markdown, sin comentarios, solo el JSON):
{
  "scenes": [
    {
      "type": "hook",
      "text": "Frase gancho impactante corta",
      "subtext": "Texto de apoyo breve",
      "emoji": "🔥"
    },
    {
      "type": "content",
      "text": "Punto principal",
      "subtext": "Explicación breve y clara del punto",
      "emoji": "💡"
    },
    {
      "type": "cta",
      "text": "¿Quieres aprender más?",
      "subtext": "Sígueme para tips diarios de IA sin tecnicismos",
      "emoji": "👉"
    }
  ]
}

Genera exactamente ${sceneCount} escenas: 1 hook + ${sceneCount - 2} contenido + 1 CTA.
El hook es LA ESCENA MÁS IMPORTANTE — debe detener el scroll inmediatamente.`;

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 2500,
        system: systemPrompt,
        messages: [
          {
            role: "user",
            content: `Crea un guión de Reel viral sobre: "${topic}"`,
          },
        ],
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        statusCode: response.status,
        headers: { "Content-Type": "application/json", ...corsHeaders },
        body: JSON.stringify({
          error: data.error?.message || "Error en la API de Claude",
        }),
      };
    }

    // Extract text content and parse JSON
    const textContent =
      data.content?.map((b) => b.text || "").join("") || "";

    let result;
    try {
      const jsonMatch = textContent.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        result = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error("No JSON found in response");
      }
    } catch (parseErr) {
      return {
        statusCode: 500,
        headers: { "Content-Type": "application/json", ...corsHeaders },
        body: JSON.stringify({
          error: "Error procesando la respuesta de la IA",
          raw: textContent,
        }),
      };
    }

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json", ...corsHeaders },
      body: JSON.stringify(result),
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json", ...corsHeaders },
      body: JSON.stringify({ error: "Error interno: " + err.message }),
    };
  }
};
