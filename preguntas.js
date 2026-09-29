// Preguntas de la encuesta. Claves "t_" = respuesta abierta.
window.API = "https://ai.tunky.net/encuesta-api";
window.PREGUNTAS = [
  { id: "q1", tipo: "una", texto: "¿A qué te dedicas?", opciones: ["Ingeniería", "Tecnología / sistemas", "Gestión o administración", "Docencia o investigación", "Estudiante", "Otro"] },
  { id: "q2", tipo: "una", texto: "¿Con qué frecuencia usas IA?", opciones: ["Nunca o casi nunca", "Una vez a la semana", "Varias veces a la semana", "Todos los días", "Varias veces al día"] },
  { id: "q3", tipo: "varias", texto: "¿Qué herramientas usas?", opciones: ["ChatGPT", "Claude", "Gemini", "Grok", "Copilot", "DeepSeek", "Perplexity", "NotebookLM", "Cursor o Claude Code", "n8n, Make o Zapier", "Imagen o video", "Ninguna"] },
  { id: "q4", tipo: "varias", texto: "¿Para qué la usas más?", opciones: ["Redactar correos o documentos", "Resumir información", "Investigar", "Programar", "Analizar datos o Excel", "Hacer presentaciones", "Crear imágenes o video", "Automatizar tareas", "Estudiar o aprender"] },
  { id: "q5", tipo: "una", texto: "¿Pagas alguna suscripción de IA?", opciones: ["No", "Sí, una", "Sí, más de una", "La paga mi empresa"] },
  { id: "q6", tipo: "una", texto: "¿Sabes programar?", opciones: ["No", "Lo básico", "Sí, lo hago en mi trabajo"] },
  { id: "t_7", tipo: "texto", texto: "¿Qué tarea de tu trabajo te gustaría que la IA hiciera por ti?" },
  { id: "q8", tipo: "varias", max: 3, texto: "¿Qué temas quieres profundizar? (máximo 3)", opciones: ["Investigación con fuentes", "Programar con agentes", "Automatizar tareas", "Datos y dashboards", "Prototipos y apps", "Video y avatares", "Agentes en WhatsApp o Telegram", "IA local y privacidad"] },
  { id: "t_9", tipo: "texto", opcional: true, texto: "¿Qué duda o preocupación tienes sobre la IA? (opcional)" },
];
