# Encuesta IA · AI Productivity Engineering

Encuesta anónima para la sesión 1 del curso. Sirve para ajustar las clases siguientes según cómo usan la IA los participantes.

- **Votar:** https://unimauro.github.io/encuesta-ia/
- **Resultados (solo docente, con clave):** https://unimauro.github.io/encuesta-ia/resultados.html

## Cómo funciona

- Las páginas son estáticas en GitHub Pages. Las preguntas están en `preguntas.js`.
- Los votos se guardan en una API mínima (`api/server.py`, Python estándar y SQLite) en el VPS, detrás de `https://ai.tunky.net/encuesta-api/`.
- **Un voto por persona:** cada navegador genera un identificador y la API rechaza un segundo voto con el mismo identificador. Sin inicio de sesión no se puede garantizar al 100%: alguien podría votar de nuevo desde otro navegador o en modo incógnito.
- **Resultados privados:** `/results` exige la cabecera `X-Admin-Key`. La clave vive en el `.env` del servidor y en `.admin-key` local, que no se sube al repo.

## Despliegue de la API

```bash
# contenedor (ya creado)
docker run -d --name encuesta-ia --restart unless-stopped --env-file /opt/encuesta-ia/.env \
  -v /opt/encuesta-ia/server.py:/app/server.py:ro -v /opt/encuesta-ia/data:/data \
  -p 127.0.0.1:3440:8000 python:3.12-alpine python -u /app/server.py
```

Ruta en Caddy, dentro del bloque `ai.tunky.net`:

```
handle_path /encuesta-api/* {
	reverse_proxy 127.0.0.1:3440
}
```
