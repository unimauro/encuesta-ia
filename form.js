(function () {
  const E = ENCUESTAS[document.body.dataset.encuesta];
  const f = document.getElementById("f"), estado = document.getElementById("estado");
  document.getElementById("titulo").textContent = E.titulo;
  document.getElementById("sub").textContent = E.sub;
  document.title = E.titulo;
  const K = E.clave;
  const get = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const set = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
  function yaVoto() { estado.innerHTML = '<div class="msg"><b>¡Listo!</b> </div>'; estado.querySelector("div").append(E.gracias); f.remove(); }
  if (get(K + ":votado")) { yaVoto(); return; }
  let token = get(K + ":token");
  if (!token) { token = E.prefijo + (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now()); set(K + ":token", token); }
  for (const p of E.preguntas) {
    const fs = document.createElement("fieldset"); const lg = document.createElement("legend"); lg.textContent = p.texto; fs.appendChild(lg);
    if (p.tipo === "texto") { const t = document.createElement("textarea"); t.name = p.id; t.maxLength = 1000; fs.appendChild(t); }
    else for (const o of p.opciones) {
      const l = document.createElement("label"); l.className = "op";
      const i = document.createElement("input"); i.type = p.tipo === "una" ? "radio" : "checkbox"; i.name = p.id; i.value = o;
      if (p.max) i.addEventListener("change", () => { if (f.querySelectorAll(`input[name=${p.id}]:checked`).length > p.max) i.checked = false; });
      l.append(i, document.createTextNode(o)); fs.appendChild(l);
    }
    f.appendChild(fs);
  }
  const b = document.createElement("button"); b.type = "submit"; b.textContent = "Enviar mi voto"; f.appendChild(b);
  const err = document.createElement("p"); err.className = "err"; f.appendChild(err);
  f.addEventListener("submit", async (e) => {
    e.preventDefault(); err.textContent = "";
    const answers = {};
    for (const p of E.preguntas) {
      if (p.tipo === "texto") answers[p.id] = f.elements[p.id].value.trim();
      else if (p.tipo === "una") { const c = f.querySelector(`input[name=${p.id}]:checked`); answers[p.id] = c ? c.value : ""; }
      else answers[p.id] = [...f.querySelectorAll(`input[name=${p.id}]:checked`)].map(x => x.value);
    }
    const falta = E.preguntas.find(p => !p.opcional && (Array.isArray(answers[p.id]) ? !answers[p.id].length : !answers[p.id]));
    if (falta) { err.textContent = "Falta responder: " + falta.texto; return; }
    b.disabled = true; b.textContent = "Enviando...";
    try {
      const r = await fetch(API + "/vote", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token, answers }) });
      if (r.status === 201 || r.status === 409) { set(K + ":votado", "1"); yaVoto(); return; }
      const j = await r.json().catch(() => ({})); throw new Error(j.error || ("error " + r.status));
    } catch (x) { err.textContent = "No se pudo enviar: " + x.message + ". Intenta de nuevo."; b.disabled = false; b.textContent = "Enviar mi voto"; }
  });
})();
