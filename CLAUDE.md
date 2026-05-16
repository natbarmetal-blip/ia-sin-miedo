# IA Sin Miedo - Skill

## El Proyecto
Curso online de inteligencia artificial para hispanohablantes de 45+ que sienten miedo o rechazo hacia la tecnología.

## Lema
"Aprende IA sin complicaciones, sin tecnicismos, sin miedo"

## Público objetivo
- Edad: 45 años en adelante
- Idioma: Español
- Perfil: Personas que creen que la IA no es para ellos
- Miedo principal: Complicación, tecnicismos, sentirse perdidos

## Tono de comunicación
- Cercano y cálido
- Sin tecnicismos
- Como un amigo que explica, no como un profesor que enseña
- Motivacional pero honesto

## Estructura del curso
- 4 módulos: ChatGPT, Canva AI, CapCut AI, Suno
- 18 videos de 5-8 minutos cada uno
- 4 guías PDF
- Pago único con acceso de por vida
- Precio curso: $97 (pre-venta lista de espera: $67)
- Precio PDF: $9.99

## Plataforma
- Venta: Hotmart
- Landing page: moonlit-conkies-656152.netlify.app
- Repo: github.com/natbarmetal-blip/ia-sin-miedo
- Hosting: Netlify (deploy automático desde GitHub)
- Redes: Instagram y Facebook
- Handle: @natalio.iasinmiedo

## Stack técnico
- HTML/CSS/JS puro (sin frameworks)
- Netlify Functions (serverless) para proxy de API
- API de Anthropic (Claude Sonnet) para el asistente IA y generador de carruseles
- Netlify Forms para captura de leads
- Variable de entorno: ANTHROPIC_API_KEY (configurada en Netlify)

## Estructura del proyecto
```
ia-sin-miedo/
├── index.html          # Landing page principal
├── carousel.html       # Generador de carruseles virales
├── netlify.toml        # Config de Netlify
├── netlify/
│   └── functions/
│       ├── chat.js     # Proxy API Claude para asistente IA
│       └── carousel.js # Proxy API Claude para generar carruseles
└── .gitignore
```

## Páginas del sitio

### index.html (Landing page principal)
- **Hero**: Hook con CTA al asistente gratuito
- **Problema**: Pain points del público (4 cards)
- **Solución/Agente**: Asistente IA interactivo con quiz de 3 preguntas + chat en vivo
- **Testimonios**: 3 testimonios con nombres, edades y ciudades
- **Oferta PDF**: Guía a $9.99 con link a Hotmart (go.hotmart.com/V105443698D)
- **Lista de espera curso**: Pre-venta a $67 (precio regular $97) con countdown timer
- **Garantía**: 30 días de garantía
- **FAQ**: 5 preguntas frecuentes con acordeón
- **CTA Final**: Doble botón (asistente gratis + comprar guía) + link a lista de espera

### carousel.html (Generador de carruseles)
- Herramienta gratuita para crear carruseles virales con IA
- 4 estilos: Tips rápidos, Mitos vs Realidad, Paso a paso, Motivacional
- Renderizado en canvas (1080x1350px - formato Instagram)
- Descarga individual o todas las slides
- Banner de promoción del PDF
- Captura de email para tips semanales

## Formularios Netlify activos
1. `leads-ia-sin-miedo` — Captura email desde el asistente IA (index.html)
2. `waitlist-curso` — Lista de espera del curso (index.html)
3. `tips-carousel` — Suscripción tips semanales (carousel.html)

## Diseño y estilo
- **Tema**: Dark mode elegante
- **Colores principales**:
  - Dark: #0a0a12, #12121e, #1a1a2e
  - Accent (coral): #FF6B6B
  - Accent2 (naranja): #FFB347
  - Teal: #4ECDC4
  - Purple: #A78BFA
  - White: #f8f6f2
  - Muted: #8892a4
- **Tipografía**:
  - Títulos: Playfair Display (serif, 700/900)
  - Cuerpo: Lato (sans-serif, 300/400/700)
- **Animaciones**: fadeUp, float, glow, bounce, pulse, shimmer

## Reglas de contenido
- Siempre hablar de beneficios, no de características técnicas
- Ejemplos de la vida real: salud, familia, viajes, dinero
- Nivel profesional senior orientado a resultados económicos
- Nunca usar jerga técnica sin explicar
- El tono siempre es "tú puedes" no "tú debes"

## Estado actual del proyecto (Abril 2026)
- ✅ Landing page publicada y funcionando
- ✅ Asistente IA en vivo (quiz + chat con Claude)
- ✅ Generador de carruseles funcionando
- ✅ PDF en venta en Hotmart ($9.99)
- ✅ Lista de espera del curso activa
- ✅ 3 formularios capturando emails
- 🔄 Curso en producción (lanzamiento ~2 semanas)
- ❌ Link de Hotmart del curso (pendiente)

## Próximos pasos
1. Terminar los 18 videos del curso
2. Crear el producto en Hotmart y obtener el link de compra
3. Actualizar la sección de lista de espera con link de compra real
4. Lanzar y notificar a la lista de espera
