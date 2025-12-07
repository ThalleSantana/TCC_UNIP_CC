console.log("✅ app.js carregado com sucesso");

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
  console.log("LOGIN RESPONSE ===>", data);

  // ✅ salva token e redireciona
  setToken(data.access_token);
  window.location.href = "/frontend/html/post.html";
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
  window.location.href = "/frontend/html/login.html";
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
  if (!res.ok) {
    const err = await safeJson(res);
    throw new Error(err.detail || "Erro ao solicitar redefinição.");
  }
  alert("Se este e-mail estiver cadastrado, você receberá as instruções.");
  window.location.href = "/frontend/html/login.html";
}

/* ============================
   Analise
============================ */

async function safeJson(res) {
    try { return await res.json(); }
    catch { return {}; }
}

async function handleAnalyze(url) {
  try {
    console.log("[handleAnalyze] Enviando para /posts/analyze:", url);
    console.log("Payload enviado:", JSON.stringify({ url }));

    const res = await fetch("/posts/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ url, platform: "youtube" })
    });

    const data = await safeJson(res);
    console.log("[/posts/analyze retorno]", data);

    if (!res.ok) {
      console.error("Erro na requisição:", {
        status: res.status,
        statusText: res.statusText,
        body: data
      });

      return;
    }

    localStorage.setItem("last_analysis_id", data.analysis_id);

    localStorage.setItem("analysis_data", JSON.stringify(data.summary));

    window.location.href = "/frontend/html/result.html";

  } catch (e) {
    console.error("Erro na análise (catch):", e);
    alert("Erro inesperado ao analisar.");
  }
}

/* ======== Botão Analisar ======== */
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector("[data-action='analyze']");
  btn.onclick = () => {
    let url = document.getElementById("post-url").value.trim();

    if (!url.startsWith("http")) {
      url = "https://" + url;
    }

    const isValidYoutube = /^https?:\/\/(www\.)?(youtube\.com|youtu\.be)\/.+/.test(url);
    if (!isValidYoutube) {
      alert("Insira um link válido do YouTube.");
      return;
    }

    handleAnalyze(url);
  };
});

/* ---------------------------
   CARREGAR RESULTADO
--------------------------- */
async function loadResult() {
  const id = localStorage.getItem("last_analysis_id");
  if (!id) return;

  const res = await fetch(`/analysis/${id}`, { headers: { ...authHeaders() } });
  if (!res.ok) {
    if (res.status === 401) return (window.location.href = "/frontend/html/login.html");
    const err = await safeJson(res);
    console.warn("Erro ao carregar resultado:", err);
    return;
  }
  const data = await res.json();

  const positive = data.summary_positive;
  const neutral = data.summary_neutral;
  const negative = data.summary_negative;
  const total = positive + neutral + negative;

  document.getElementById("totalCount").textContent = `Total: ${total}`;

  const ctx = document.getElementById("sentimentChart").getContext("2d");
  new Chart(ctx, {
    type: "pie",
    data: {
      labels: [
        `Positivos (${((positive / total) * 100).toFixed(1)}%)`,
        `Neutros (${((neutral / total) * 100).toFixed(1)}%)`,
        `Negativos (${((negative / total) * 100).toFixed(1)}%)`
      ],
      datasets: [{
        data: [positive, neutral, negative],
        backgroundColor: ["#22c55e", "#facc15", "#ef4444"],
        borderColor: "#fff",
        borderWidth: 2
      }]
    },
    options: {
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#374151",
            font: {
              size: 14
            }
          }
        }
      }
    }
  });

  const positiveBox = qs("[data-comments-positive] .mt-4");
  const neutralBox = qs("[data-comments-neutral] .mt-4");
  const negativeBox = qs("[data-comments-negative] .mt-4");

  [positiveBox, neutralBox, negativeBox].forEach(box => box.innerHTML = "");

  (data.comments || []).forEach(c => {
    const wrapper = document.createElement("div");
    wrapper.className = "flex items-center gap-3 rounded-md bg-surface-secondary p-3";

    const icon = document.createElement("span");
    icon.className = "h-6 w-6";
    icon.innerHTML = getIcon(c.label);

    const text = document.createElement("span");
    text.className = "font-medium text-text-primary";
    text.textContent = c.text;

    wrapper.appendChild(icon);
    wrapper.appendChild(text);

    if (c.label === "positive") positiveBox.appendChild(wrapper);
    else if (c.label === "neutral") neutralBox.appendChild(wrapper);
    else if (c.label === "negative") negativeBox.appendChild(wrapper);
  });
}

function getIcon(label) {
  if (label === "positive") {
    return `
      <svg class="text-[var(--positive)]" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24">
        <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
        <line x1="9" x2="9.01" y1="9" y2="9"></line>
        <line x1="15" x2="15.01" y1="9" y2="9"></line>
        <circle cx="12" cy="12" r="10"></circle>
      </svg>`;
  }

  if (label === "neutral") {
    return `
      <svg class="text-yellow-500" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="8" x2="16" y1="15" y2="15"></line>
        <line x1="9" x2="9.01" y1="9" y2="9"></line>
        <line x1="15" x2="15.01" y1="9" y2="9"></line>
      </svg>`;
  }

  if (label === "negative") {
  return `
    <svg class="text-[var(--negative)]" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10"></circle>
      <path d="M8 15c1-1 2.5-1.5 4-1.5s3 .5 4 1.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <line x1="9" x2="9.01" y1="9" y2="9"></line>
      <line x1="15" x2="15.01" y1="9" y2="9"></line>
    </svg>
  `;
}

  return "";
}

/* ---------------------------
   HISTÓRICO
--------------------------- */
async function loadHistory() {
  const token = getToken();
  if (!token) {
    window.location.href = "/frontend/html/login.html";
    return;
  }

  const res = await fetch(`/analysis/`, { headers: { ...authHeaders() } });
  if (!res.ok) {
    if (res.status === 401) {
      clearToken();
      window.location.href = "/frontend/html/login.html";
      return;
    }
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
    window.location.href = "/frontend/html/result.html";
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
  const loginForm = qs("[data-form='login']");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = loginForm.querySelector("input[name='email']").value.trim();
      const password = loginForm.querySelector("input[name='password']").value;
      try { await handleLogin(email, password); }
      catch (err) { 
      }
    });
  }

  /* REGISTER */
  if (document.body.matches("[data-page='register']")) {
    const form = document.getElementById("register-form");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const first_name = form.first_name.value.trim();
        const last_name = form.last_name.value.trim();
        const email = form.email.value.trim();
        const password = form.password.value;
        const confirm = form.confirm_password.value;
        if (password !== confirm) return alert("As senhas não coincidem!");
        try { await handleRegister(first_name, last_name, email, password); }
        catch (err) { 
        }
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
        catch (err) { 
        }
      });
    }
  }

  /* HOME / ANALISAR */
const analyzeBtn = qs("[data-action='analyze']");
if (analyzeBtn) {
  analyzeBtn.addEventListener("click", async () => {
    const url = qs("[data-input='url']").value.trim();

    const platformInput = document.querySelector("[data-input='platform']");
    const platform = platformInput ? platformInput.value : "youtube";

    if (!url) return alert("Cole o link do vídeo do YouTube.");

    try {
      await handleAnalyze(platform, url);
    } catch (err) {
      console.error(err);
      alert(err.message || "Erro ao analisar comentários do YouTube.");
    }
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
    window.location.href = "/frontend/html/login.html";
  });
});

/* ---------------------------
   REDEFINIÇÃO DE SENHA (confirmação)
--------------------------- */
async function handleResetConfirm(token, new_password){
  const res = await fetch(`/auth/reset-password-confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password })
  });
  if(!res.ok){
    const err = await safeJson(res);
    throw new Error(err.detail || "Erro ao redefinir senha.");
  }
  return await res.json();
}
