// Netlify Function — Generador de post ligero (imagen única) con Claude

const TIPOS = {
  frase: "Genera una frase motivadora e impactante relacionada al tema. Máximo 12 palabras. Que detenga el scroll.",
  tip: "Genera UN tip práctico y concreto que alguien de 45+ pueda aplicar hoy mismo con IA. Simple, sin tecnicismos.",
  pregunta: "Genera una pregunta que invite a la audiencia a responder en los comentarios. Que genere curiosidad y debate.",
  dato: "Genera UN dato sorprendente sobre inteligencia artificial que sea relevante para personas de 45+ años."
};

exports.handler = async (event) => {
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
    const { topic, tipo } = JSON.parse(event.body);

    if (!topic || !topic.trim()) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Se requiere un tema" }),
      };
    }

    const tipoGuide = TIPOS[tipo] || TIPOS.frase;

    const systemPrompt = `Eres un experto en contenido viral para Instagram y Facebook para la marca "IA Sin Miedo".
Tu audiencia son personas de 45-75 años que sienten miedo o confusión ante la inteligencia artificial.
Tono: cálido, simple, motivador. Como un amigo paciente que explica tecnología.

HERRAMIENTAS PERMITIDAS (solo estas 4):
- ChatGPT
- Canva AI
- CapCut
- Suno

TIPO DE CONTENIDO: ${tipoGuide}

REGLAS:
1. Siempre en español
2. Sin tecnicismos
3. Frases cortas y poderosas
4. Usa 1 emoji máximo

RESPONDE ÚNICAMENTE con un JSON válido sin markdown (solo el JSON):
{
  "texto_principal": "El texto grande que va en el centro de la imagen",
  "subtexto": "Una frase pequeña complementaria (opcional, puede ser vacío)",
  "emoji": "Un solo emoji representativo",
  "caption": "El texto para pegar en Instagram/Facebook (2-3 párrafos cortos + CTA para seguir @natalio.iasinmiedo). Para Instagram termina con: Seguime 👉 @natalio.iasinmiedo. Para Facebook termina con: Probá gratis aquí 👉 moonlit-conkies-656152.netlify.app",
  "caption_facebook": "Igual que caption pero siempre termina con: Probá gratis aquí 👉 moonlit-conkies-656152.netlify.app",
  "hashtags": "#IAsinmiedo #InteligenciaArtificial #ChatGPT #MayoresDe45 #EmprendedoresLatinos"
}`;

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-5",
        max_tokens: 800,
        system: systemPrompt,
        messages: [{ role: "user", content: `Crea un post ligero sobre: "${topic}"` }],
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        statusCode: response.status,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        body: JSON.stringify({ error: data.error?.message || "Error en la API" }),
      };
    }

    const text = data.content?.map(b => b.text || "").join("") || "";

    let result;
    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      result = JSON.parse(jsonMatch[0]);
    } catch {
      return {
        statusCode: 500,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        body: JSON.stringify({ error: "Error procesando la respuesta" }),
      };
    }

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify(result),
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ error: "Error interno: " + err.message }),
    };
  }
};
