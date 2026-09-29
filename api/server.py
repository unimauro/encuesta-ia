"""API mínima de la encuesta (solo biblioteca estándar).

POST /vote     {token, answers}  -> 201 | 409 si ese dispositivo ya votó
GET  /results  (header X-Admin-Key) -> totales por pregunta y respuestas abiertas
GET  /health
"""
import hashlib, hmac, json, os, sqlite3, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB = os.environ.get("DB_PATH", "/data/votos.db")
ADMIN_KEY = os.environ["ADMIN_KEY"]
ALLOWED = set(os.environ.get("ALLOWED_ORIGINS", "https://unimauro.github.io").split(","))
SALT = os.environ.get("IP_SALT", "sal")
MAX_PER_IP = int(os.environ.get("MAX_PER_IP", "80"))

def db():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS votos (token TEXT PRIMARY KEY, ip TEXT, ts INTEGER, answers TEXT)")
    return c

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

    def do_GET(self):
        if self.path.startswith("/health"):
            return self._json(200, {"ok": True})
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
        if not self.path.startswith("/vote"):
            return self._json(404, {"error": "no encontrado"})
        if self.headers.get("Origin", "") not in ALLOWED:
            return self._json(403, {"error": "origen no permitido"})
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

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), H).serve_forever()
