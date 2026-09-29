"""API mínima del curso (solo biblioteca estándar).

POST /vote              {token, answers}  -> 201 | 409 si ese dispositivo ya votó
GET  /results           (X-Admin-Key) -> totales por pregunta y respuestas abiertas
GET  /plazo?tarea=s1    -> fecha límite de entrega (público)
POST /entrega           {tarea, email, nombre, grupo, texto, enlace, archivo:{nombre,tipo,b64}} -> 201 | 403 fuera de plazo
GET  /entregas?tarea=s1 (X-Admin-Key) -> todas las entregas (todas las versiones)
GET  /archivo?id=N      (X-Admin-Key) -> archivo adjunto
GET  /health
"""
import base64, hashlib, hmac, json, os, re, sqlite3, time, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB = os.environ.get("DB_PATH", "/data/votos.db")
ADMIN_KEY = os.environ["ADMIN_KEY"]
ALLOWED = set(os.environ.get("ALLOWED_ORIGINS", "https://unimauro.github.io").split(","))
SALT = os.environ.get("IP_SALT", "sal")
MAX_PER_IP = int(os.environ.get("MAX_PER_IP", "80"))
# Fechas límite en UTC. Por defecto: sesión 1 hasta el jueves 1 de octubre de 2026, 6:59 p. m. de Lima (23:59 UTC).
PLAZOS = json.loads(os.environ.get("PLAZOS", '{"s1": "2026-10-01T23:59:00Z"}'))
FILES = os.environ.get("FILES_DIR", "/data/archivos")
MAX_FILE = 10 * 1024 * 1024
EXT_OK = {"pdf", "xlsx", "xls", "csv", "docx", "doc", "pptx", "txt", "md", "png", "jpg", "jpeg", "zip"}
EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[a-zA-Z]{2,}$")

def db():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS votos (token TEXT PRIMARY KEY, ip TEXT, ts INTEGER, answers TEXT)")
    c.execute("""CREATE TABLE IF NOT EXISTS entregas (id INTEGER PRIMARY KEY AUTOINCREMENT, tarea TEXT, email TEXT, nombre TEXT,
                 grupo TEXT, texto TEXT, enlace TEXT, archivo_nombre TEXT, archivo_tipo TEXT, archivo_path TEXT, ts INTEGER, ip TEXT)""")
    return c

def plazo(tarea):
    p = PLAZOS.get(tarea)
    return datetime.strptime(p, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() if p else None

class H(BaseHTTPRequestHandler):
    def _cors(self):
        o = self.headers.get("Origin", "")
        if o in ALLOWED:
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Key")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def _admin(self):
        return hmac.compare_digest(self.headers.get("X-Admin-Key", ""), ADMIN_KEY)

    def _q(self, k):
        from urllib.parse import urlparse, parse_qs
        return (parse_qs(urlparse(self.path).query).get(k) or [""])[0]

    def do_GET(self):
        if self.path.startswith("/health"):
            return self._json(200, {"ok": True})
        if self.path.startswith("/plazo"):
            t = self._q("tarea") or "s1"
            return self._json(200, {"tarea": t, "plazo": PLAZOS.get(t), "ahora": int(time.time())})
        if self.path.startswith("/entregas"):
            if not self._admin():
                return self._json(401, {"error": "clave incorrecta"})
            t = self._q("tarea") or "s1"
            rows = db().execute("SELECT id, email, nombre, grupo, texto, enlace, archivo_nombre, ts FROM entregas WHERE tarea=? ORDER BY ts", (t,)).fetchall()
            keys = ["id", "email", "nombre", "grupo", "texto", "enlace", "archivo", "ts"]
            return self._json(200, {"tarea": t, "plazo": PLAZOS.get(t), "entregas": [dict(zip(keys, r)) for r in rows]})
        if self.path.startswith("/archivo"):
            if not self._admin():
                return self._json(401, {"error": "clave incorrecta"})
            r = db().execute("SELECT archivo_nombre, archivo_tipo, archivo_path FROM entregas WHERE id=?", (self._q("id"),)).fetchone()
            if not r or not r[2] or not os.path.exists(r[2]):
                return self._json(404, {"error": "sin archivo"})
            data = open(r[2], "rb").read()
            self.send_response(200); self._cors()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + __import__("urllib.parse").parse.quote(r[0]))
            self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            return
        if self.path.startswith("/results"):
            if not hmac.compare_digest(self.headers.get("X-Admin-Key", ""), ADMIN_KEY):
                return self._json(401, {"error": "clave incorrecta"})
            rows = db().execute("SELECT ts, answers FROM votos ORDER BY ts").fetchall()
            totals, texts = {}, {}
            for ts, a in rows:
                for q, v in json.loads(a).items():
                    if isinstance(v, list):
                        for opt in v:
                            totals.setdefault(q, {}).setdefault(opt, 0); totals[q][opt] += 1
                    elif isinstance(v, str) and v.strip():
                        if q.startswith("t_"):
                            texts.setdefault(q, []).append(v.strip())
                        else:
                            totals.setdefault(q, {}).setdefault(v, 0); totals[q][v] += 1
            return self._json(200, {"votos": len(rows), "totales": totals, "textos": texts,
                                    "ultimo": rows[-1][0] if rows else None})
        self._json(404, {"error": "no encontrado"})

    def do_POST(self):
        if self.headers.get("Origin", "") not in ALLOWED:
            return self._json(403, {"error": "origen no permitido"})
        if self.path.startswith("/entrega"):
            return self._entrega()
        if not self.path.startswith("/vote"):
            return self._json(404, {"error": "no encontrado"})
        try:
            n = min(int(self.headers.get("Content-Length", 0)), 20000)
            data = json.loads(self.rfile.read(n))
            token = str(data["token"])[:64]
            answers = data["answers"]
            assert isinstance(answers, dict) and len(token) >= 16
            clean = {}
            for k, v in list(answers.items())[:30]:
                k = str(k)[:40]
                if isinstance(v, list):
                    clean[k] = [str(x)[:80] for x in v[:15]]
                else:
                    clean[k] = str(v)[:1000]
        except Exception:
            return self._json(400, {"error": "datos inválidos"})
        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        iph = hashlib.sha256((SALT + ip).encode()).hexdigest()[:16]
        c = db()
        if c.execute("SELECT COUNT(*) FROM votos WHERE ip=?", (iph,)).fetchone()[0] >= MAX_PER_IP:
            return self._json(429, {"error": "demasiados votos desde esta red"})
        try:
            c.execute("INSERT INTO votos VALUES (?,?,?,?)", (token, iph, int(time.time()), json.dumps(clean, ensure_ascii=False)))
            c.commit()
        except sqlite3.IntegrityError:
            return self._json(409, {"error": "ya votaste"})
        self._json(201, {"ok": True})

    def _entrega(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > MAX_FILE * 1.4 + 200000:
                return self._json(413, {"error": "el archivo supera 10 MB"})
            d = json.loads(self.rfile.read(n))
            tarea = str(d.get("tarea", "s1"))[:10]
            email = str(d.get("email", "")).strip().lower()[:254]
            nombre = str(d.get("nombre", "")).strip()[:120]
            grupo = str(d.get("grupo", "")).strip()[:120]
            texto = str(d.get("texto", "")).strip()[:20000]
            enlace = str(d.get("enlace", "")).strip()[:500]
        except Exception:
            return self._json(400, {"error": "datos inválidos"})
        lim = plazo(tarea)
        if lim is None:
            return self._json(400, {"error": "tarea desconocida"})
        if time.time() > lim:
            return self._json(403, {"error": "el plazo de entrega ya venció"})
        if not EMAIL.match(email) or not nombre:
            return self._json(400, {"error": "falta un correo válido o tu nombre"})
        if enlace and not re.match(r"^https?://", enlace):
            return self._json(400, {"error": "el enlace debe empezar con http:// o https://"})
        a = d.get("archivo") or {}
        path = aname = atype = None
        if a.get("b64"):
            aname = os.path.basename(str(a.get("nombre", "archivo")))[:150]
            ext = aname.rsplit(".", 1)[-1].lower() if "." in aname else ""
            if ext not in EXT_OK:
                return self._json(400, {"error": "tipo de archivo no permitido"})
            try:
                raw = base64.b64decode(a["b64"], validate=True)
            except Exception:
                return self._json(400, {"error": "archivo dañado"})
            if len(raw) > MAX_FILE:
                return self._json(413, {"error": "el archivo supera 10 MB"})
            os.makedirs(FILES, exist_ok=True)
            path = os.path.join(FILES, uuid.uuid4().hex + "." + ext)
            open(path, "wb").write(raw)
            atype = str(a.get("tipo", ""))[:100]
        if not (texto or enlace or path):
            return self._json(400, {"error": "envía un texto, un enlace o un archivo"})
        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        iph = hashlib.sha256((SALT + ip).encode()).hexdigest()[:16]
        c = db()
        c.execute("INSERT INTO entregas (tarea,email,nombre,grupo,texto,enlace,archivo_nombre,archivo_tipo,archivo_path,ts,ip) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (tarea, email, nombre, grupo, texto, enlace, aname, atype, path, int(time.time()), iph))
        c.commit()
        return self._json(201, {"ok": True, "recibido": int(time.time())})

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), H).serve_forever()
