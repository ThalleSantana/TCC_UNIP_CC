/* ============================
   EmoSync — frontend/js/app.js
   ============================ */

/*  ✅ Importante:
    - Usamos URLs RELATIVAS nos fetch() (ex.: "/auth/login").
      Assim, funciona em qualquer porta (8000, 8001, etc.).
    - Se quiser forçar versão e evitar cache, carregue no HTML:
      <script src="./js/app.js?v=3"></script>
*/

/* ---------------------------
   Helpers de Autenticação
--------------------------- */
const tokenKey = "emo_token";

function setToken(t) { localStorage.setItem(tokenKey, t); }
function getToken() { return localStorage.getItem(tokenKey); }
function clearToken() { localStorage.removeItem(tokenKey); }

function authHeaders() {
  const t = getToken();
  return t ? { "Authorization": `Bearer ${t}` } : {};
}

/* ---------------------------
   LOGIN
--------------------------- */
async function handleLogin(email, password) {
  const res = await fetch(`/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) {
    const err = await safeJson(res);
    throw new Error(err.detail || "Login inválido");
  }
  const data = await res.json();
  setToken(data.access_token);
  window.location.href = "/frontend/index.html";
}

/* ---------------------------
   REGISTRO
--------------------------- */
async function handleRegister(first_name, last_name, email, password) {
  const res = await fetch(`/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ first_name, last_name, email, password })
  });
  if (!res.ok) {
    const err = await safeJson(res);
    throw new Error(err.detail || "Erro ao cadastrar");
  }
  alert("Cadastro realizado! Faça login para continuar.");
  window.location.href = "/frontend/login.html";
}

/* ---------------------------
   REDEFINIÇÃO DE SENHA (pedido)
--------------------------- */
async function handleResetRequest(email) {
  const res = await fetch(`/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });
  // Por segurança, backend retorna a mesma msg exista ou não o e-mail
  if (!res.ok) {
    const err = await safeJson(res);
    throw new Error(err.detail || "Erro ao solicitar redefinição.");
  }
  alert("Se este e-mail estiver cadastrado, você receberá as instruções.");
  window.location.href = "/frontend/login.html";
}

/* ---------------------------
   ANALISAR POST
--------------------------- */
async function handleAnalyze(platform, url) {
  const res = await fetch(`/posts/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ platform, url })
  });
  if (!res.ok) {
    if (res.status === 401) {
      alert("Faça login para continuar.");
      return (window.location.href = "/frontend/login.html");
    }
    const err = await safeJson(res);
    throw new Error(err.detail || "Falha ao analisar");
  }
  const data = await res.json();
  localStorage.setItem("last_analysis_id", data.analysis_id);
  window.location.href = "/frontend/result.html";
}

/* ---------------------------
   CARREGAR RESULTADO
--------------------------- */
async function loadResult() {
  const id = localStorage.getItem("last_analysis_id");
  if (!id) return;

  const res = await fetch(`/analysis/${id}`, { headers: { ...authHeaders() }});
  if (!res.ok) {
    if (res.status === 401) return (window.location.href = "/frontend/login.html");
    const err = await safeJson(res);
    console.warn("Erro ao carregar resultado:", err);
    return;
  }
  const data = await res.json();

  // Contadores
  putText("[data-count-positive]", data.summary_positive);
  putText("[data-count-neutral]",  data.summary_neutral);
  putText("[data-count-negative]", data.summary_negative);

  // Comentários
  const list = qs("[data-comments]");
  if (list) {
    list.innerHTML = "";
    (data.comments || []).forEach(c => {
      const li = document.createElement("li");
      li.textContent = `[${c.label}] ${c.text}`;
      list.appendChild(li);
    });
  }
}

/* ---------------------------
   HISTÓRICO
--------------------------- */
async function loadHistory() {
  const res = await fetch(`/analysis/`, { headers: { ...authHeaders() }});
  if (!res.ok) {
    if (res.status === 401) return (window.location.href = "/frontend/login.html");
    const err = await safeJson(res);
    console.warn("Erro ao carregar histórico:", err);
    return;
  }
  const data = await res.json();
  const tbody = qs("[data-history]");
  if (!tbody) return;

  tbody.innerHTML = "";
  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="px-4 py-3 text-sm text-gray-700">${row.id}</td>
      <td class="px-4 py-3 text-sm text-gray-700 capitalize">${row.platform}</td>
      <td class="px-4 py-3 text-sm text-blue-600 truncate max-w-[280px]">
        <a href="${row.url}" target="_blank" class="hover:underline">${row.url}</a>
      </td>
      <td class="px-4 py-3 text-sm text-green-700">${row.summary_positive}</td>
      <td class="px-4 py-3 text-sm text-yellow-700">${row.summary_neutral}</td>
      <td class="px-4 py-3 text-sm text-red-700">${row.summary_negative}</td>
      <td class="px-4 py-3 text-sm text-gray-500">${row.created_at ? new Date(row.created_at).toLocaleString() : '-'}</td>
      <td class="px-4 py-3 text-sm">
        <button class="px-3 py-1 rounded-md bg-[var(--primary-color)] text-white hover:bg-blue-700" data-goto-result="${row.id}">Ver</button>
      </td>`;
    tbody.appendChild(tr);
  });

  tbody.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-goto-result]");
    if (!btn) return;
    const id = btn.getAttribute("data-goto-result");
    localStorage.setItem("last_analysis_id", id);
    window.location.href = "/frontend/result.html";
  });
}

/* ---------------------------
   UTILITÁRIOS DOM/Fetch
--------------------------- */
function qs(sel) { return document.querySelector(sel); }
function putText(sel, value) {
  const el = qs(sel);
  if (!el) return;
  el.textContent = (value ?? "").toString();
}
async function safeJson(res) {
  try { return await res.json(); }
  catch { return {}; }
}

/* ---------------------------
   LISTENERS POR PÁGINA
--------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  /* LOGIN */
  const loginForm = qs("[data-form='login']");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = loginForm.querySelector("input[name='email']").value.trim();
      const password = loginForm.querySelector("input[name='password']").value;
      try { await handleLogin(email, password); }
      catch (err) { alert(err.message); }
    });
  }

  /* REGISTER */
  if (document.body.matches("[data-page='register']")) {
    const form = document.getElementById("register-form");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const first_name = form.first_name.value.trim();
        const last_name  = form.last_name.value.trim();
        const email      = form.email.value.trim();
        const password   = form.password.value;
        const confirm    = form.confirm_password.value;
        if (password !== confirm) return alert("As senhas não coincidem!");
        try { await handleRegister(first_name, last_name, email, password); }
        catch (err) { alert(err.message); }
      });
    }
  }

  /* RESET (pedido de redefinição) */
  if (document.body.matches("[data-page='reset']")) {
    const form = document.getElementById("reset-form");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = form.email.value.trim();
        try { await handleResetRequest(email); }
        catch (err) { alert(err.message); }
      });
    }
  }

  /* HOME / ANALISAR */
  const analyzeBtn = qs("[data-action='analyze']");
  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", async () => {
      const url = qs("[data-input='url']").value.trim();
      const platform = document.querySelector("[data-input='platform']:checked")?.value || "youtube";
      if (!url) return alert("Cole o link da postagem.");
      try { await handleAnalyze(platform, url); }
      catch (err) { alert(err.message); }
    });
  }

  /* RESULT */
  if (document.body.matches("[data-page='result']")) {
    loadResult();
  }

  /* HISTORY */
  if (document.body.matches("[data-page='history']")) {
    loadHistory();
  }

  /* LOGOUT opcional: elementos com data-action="logout" */
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action='logout']");
    if (!btn) return;
    clearToken();
    window.location.href = "/frontend/login.html";
  });
});
