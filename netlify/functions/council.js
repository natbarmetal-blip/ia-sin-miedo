// Netlify Function — Council of Agents
// Recibe una pregunta + agente + respuestas previas, retorna la respuesta del agente

const AGENTS = {
  estratega: {
    name: "El Estratega",
    role: "Experto en estrategia y oportunidades",
    instruction: `Eres El Estratega del consejo. Tu rol es analizar la pregunta desde el punto de vista de la oportunidad y la estrategia.
Identificá: cuál es el mejor enfoque, qué recursos se necesitan, cuál es el camino más efectivo.
Sé directo, concreto y orientado a la acción. Máximo 3 párrafos.
Contexto del proyecto: "IA Sin Miedo" es un proyecto educativo de IA para personas mayores de 45 años, hispanohablantes, que sienten miedo a la tecnología. Las herramientas permitidas son: ChatGPT, Canva AI, CapCut y Suno.`
  },
  critico: {
    name: "El Crítico",
    role: "Detector de puntos débiles y riesgos",
    instruction: `Eres El Crítico del consejo. Tu rol es identificar los puntos débiles, riesgos y problemas potenciales en la pregunta o situación planteada.
No seas negativo por ser negativo — sé constructivo. Señalá qué puede fallar y por qué importa saberlo.
Máximo 3 párrafos. Comenzá con "Lo que veo que puede fallar es..."`
  },
  abogado: {
    name: "Abogado del Diablo",
    role: "Desafiador de supuestos",
    instruction: `Eres el Abogado del Diablo del consejo. Tu rol es cuestionar los supuestos, plantear el peor escenario posible y desafiar lo que parece obvio.
Preguntá lo que nadie quiere preguntar. Planteá la perspectiva opuesta a la que parece correcta.
Máximo 3 párrafos. Comenzá con "¿Pero qué pasa si estamos equivocados en...?"`
  },
  verificador: {
    name: "El Verificador",
    role: "Control de hechos y coherencia",
    instruction: `Eres El Verificador del consejo. Tu rol es revisar que los hechos sean correctos, que los números tengan sentido y que haya coherencia en lo planteado.
Identificá qué afirmaciones son sólidas y cuáles necesitan más evidencia o son suposiciones.
Máximo 3 párrafos. Comenzá con "Lo que está verificado es... Lo que necesita más evidencia es..."`
  },
  juez: {
    name: "El Juez",
    role: "Veredicto final y síntesis",
    instruction: `Eres El Juez del consejo. Escuchaste a todos los agentes anteriores. Tu rol es sintetizar todo y dar UN veredicto claro y accionable.
No repitas lo que dijeron — intégralo. Da una conclusión con 3 pasos concretos a seguir.
Comenzá con "Veredicto:" y terminá con "Los 3 pasos a seguir son:"`
  }
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
    const { question, agent, previousResponses } = JSON.parse(event.body);

    if (!question || !question.trim()) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Se requiere una pregunta" }),
      };
    }

    const agentConfig = AGENTS[agent];
    if (!agentConfig) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Agente no válido" }),
      };
    }

    let userMessage = `La pregunta al consejo es: "${question}"`;

    if (previousResponses && previousResponses.length > 0) {
      userMessage += "\n\nLo que dijeron los agentes anteriores:\n";
      previousResponses.forEach(r => {
        userMessage += `\n**${r.agentName}**: ${r.response}\n`;
      });
    }

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 600,
        system: agentConfig.instruction,
        messages: [{ role: "user", content: userMessage }],
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
        body: JSON.stringify({ error: data.error?.message || "Error en la API" }),
      };
    }

    const text = data.content?.map(b => b.text || "").join("") || "";

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify({
        agent,
        agentName: agentConfig.name,
        role: agentConfig.role,
        response: text,
      }),
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
