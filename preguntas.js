// Encuestas. Claves "t_" = respuesta abierta. "contador" = pregunta obligatoria de una opción usada para contar votantes.
window.API = "https://ai.tunky.net/encuesta-api";
window.ENCUESTAS = {
  inicial: {
    titulo: "¿Cómo usas la IA hoy?",
    sub: "AI Productivity Engineering · eIA · Encuesta anónima de 3 minutos. Un solo voto por persona.",
    gracias: "Tu voto quedó registrado. Veremos los resultados juntos en la próxima clase.",
    clave: "encuesta-ia-s1", prefijo: "i-", contador: "q2",
    preguntas: [
      { id: "q1", tipo: "una", texto: "¿A qué te dedicas?", opciones: ["Ingeniería", "Tecnología / sistemas", "Gestión o administración", "Docencia o investigación", "Estudiante", "Otro"] },
      { id: "q2", tipo: "una", texto: "¿Con qué frecuencia usas IA?", opciones: ["Nunca o casi nunca", "Una vez a la semana", "Varias veces a la semana", "Todos los días", "Varias veces al día"] },
      { id: "q3", tipo: "varias", texto: "¿Qué herramientas usas?", opciones: ["ChatGPT", "Claude", "Gemini", "Grok", "Copilot", "DeepSeek", "Perplexity", "NotebookLM", "Cursor o Claude Code", "n8n, Make o Zapier", "Imagen o video", "Ninguna"] },
      { id: "q4", tipo: "varias", texto: "¿Para qué la usas más?", opciones: ["Redactar correos o documentos", "Resumir información", "Investigar", "Programar", "Analizar datos o Excel", "Hacer presentaciones", "Crear imágenes o video", "Automatizar tareas", "Estudiar o aprender"] },
      { id: "q5", tipo: "una", texto: "¿Pagas alguna suscripción de IA?", opciones: ["No", "Sí, una", "Sí, más de una", "La paga mi empresa"] },
      { id: "q6", tipo: "una", texto: "¿Sabes programar?", opciones: ["No", "Lo básico", "Sí, lo hago en mi trabajo"] },
      { id: "t_7", tipo: "texto", texto: "¿Qué tarea de tu trabajo te gustaría que la IA hiciera por ti?" },
      { id: "q8", tipo: "varias", max: 3, texto: "¿Qué temas quieres profundizar? (máximo 3)", opciones: ["Investigación con fuentes", "Programar con agentes", "Automatizar tareas", "Datos y dashboards", "Prototipos y apps", "Video y avatares", "Agentes en WhatsApp o Telegram", "IA local y privacidad"] },
      { id: "t_9", tipo: "texto", opcional: true, texto: "¿Qué duda o preocupación tienes sobre la IA? (opcional)" },
    ],
  },
  cierre: {
    titulo: "¿Cómo te fue en la sesión 1?",
    sub: "AI Productivity Engineering · eIA · Encuesta anónima de cierre, 2 minutos. Un solo voto por persona.",
    gracias: "¡Gracias por tu opinión! Con ella mejoramos la próxima sesión.",
    clave: "encuesta-ia-cierre-s1", prefijo: "c-", contador: "c1",
    preguntas: [
      { id: "c1", tipo: "una", texto: "¿Qué tan útil fue la clase de hoy?", opciones: ["1 · Nada útil", "2", "3", "4", "5 · Muy útil"] },
      { id: "c2", tipo: "una", texto: "El ritmo de la clase fue…", opciones: ["Muy lento", "Adecuado", "Muy rápido"] },
      { id: "c3", tipo: "varias", max: 3, texto: "¿Qué fue lo más valioso? (máximo 3)", opciones: ["Radar IA y noticias", "Qué es la IA y sus retos", "Recorrido de herramientas", "Agentes en WhatsApp y Telegram", "Modelos y cómo elegir", "Problemas comunes y tokens", "Context engineering", "La práctica"] },
      { id: "c4", tipo: "una", texto: "¿Qué tan seguro te sientes para elegir el modelo correcto para una tarea?", opciones: ["1 · Nada seguro", "2", "3", "4", "5 · Muy seguro"] },
      { id: "c5", tipo: "una", texto: "¿Vas a usar algo de lo visto esta semana en tu trabajo?", opciones: ["Sí", "Tal vez", "No"] },
      { id: "c6", tipo: "una", texto: "¿Recomendarías este curso a un colega?", opciones: ["Sí", "Tal vez", "No"] },
      { id: "t_c7", tipo: "texto", texto: "¿Qué mejorarías de la clase?" },
      { id: "t_c8", tipo: "texto", opcional: true, texto: "¿Qué te gustaría ver en la próxima sesión? (opcional)" },
    ],
  },
};
