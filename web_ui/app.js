const state = {
  runs: [],
  selectedRunId: null,
  selectedRun: null,
  runtime: null,
  selectedReasoner: "scripted_nemotron",
};

const SCENARIO_LABELS = {
  haas_ops_marketplace: "HaaS Ops Review",
};

function titleCase(text) {
  return String(text || "")
    .split(/[_\s-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatScenarioId(scenarioId) {
  return SCENARIO_LABELS[scenarioId] || titleCase(scenarioId);
}

function formatStatus(status) {
  const normalized = String(status || "").toLowerCase();
  const labels = {
    created: "Created",
    running: "Running",
    waiting_human: "Waiting Human",
    completed: "Completed",
    failed: "Failed",
  };
  return labels[normalized] || titleCase(normalized);
}

function statusClass(status) {
  return String(status || "").toLowerCase().replaceAll("_", "-");
}

function formatPhase(phase) {
  return titleCase(phase);
}

function formatBackend(backend) {
  const normalized = String(backend || "").toLowerCase();
  const labels = {
    scripted_nemotron: "Offline Nemotron Script",
    nim: "NVIDIA NIM",
  };
  return labels[normalized] || titleCase(normalized);
}

function summarizeRun(run) {
  const findings = run.findings?.length || 0;
  if (run.status === "completed") {
    return `${findings} leads summarized in final ops report`;
  }
  if (run.status === "waiting_human") {
    return `Paused for operator decision in ${formatPhase(run.phase)}`;
  }
  return `${findings} lead decisions recorded so far`;
}

function visibleNemotronModels(models) {
  return (models || []).filter((model) => {
    const text = String(model);
    return (
      text.startsWith("nvidia/nemotron-3-super-") ||
      text.startsWith("nvidia/nemotron-3-nano-")
    );
  });
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `Request failed: ${response.status}`);
  }
  return data;
}

function el(id) {
  return document.getElementById(id);
}

function formatDate(text) {
  if (!text) return "";
  return text.replace("T", " ").replace("+00:00", " UTC");
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function syncRuntime(runtime) {
  if (!runtime) return;
  state.runtime = runtime;
  if (!state.selectedReasoner) {
    state.selectedReasoner = runtime.default_reasoner || "scripted_nemotron";
  }
  if (runtime.nim?.connected && state.selectedReasoner !== "nim") {
    state.selectedReasoner = "nim";
  }
  renderInferencePanel();
  renderToolbarLabels();
}

async function loadRuntime() {
  const data = await api("/api/runtime");
  syncRuntime(data.runtime);
}

async function loadRuns() {
  const data = await api("/api/runs");
  state.runs = data.runs.slice().sort((a, b) => {
    return String(b.updated_at || "").localeCompare(String(a.updated_at || ""));
  });
  syncRuntime(data.runtime);
  renderRuns();
  el("run-count-pill").textContent = `${state.runs.length} runs loaded`;

  if (!state.selectedRunId && state.runs.length > 0) {
    state.selectedRunId = state.runs[0].run_id;
  }
  if (state.selectedRunId) {
    await loadRunDetail(state.selectedRunId);
  } else {
    renderEmptyPanels();
  }
}

async function loadRunDetail(runId) {
  state.selectedRunId = runId;
  const data = await api(`/api/runs/${runId}`);
  state.selectedRun = data;
  syncRuntime(data.runtime);
  renderRuns();
  renderRunDetail();
  renderCheckpoints();
}

function selectedReasoner() {
  const checked = document.querySelector('input[name="reasoner"]:checked');
  return checked?.value || state.selectedReasoner || "scripted_nemotron";
}

function resolveModelSelection() {
  const custom = el("nim-model-custom")?.value?.trim();
  if (custom) return custom;
  return el("nim-model-select")?.value || state.runtime?.nim?.model_name || "";
}

async function createRun(autoAnswer) {
  const reasoner = selectedReasoner();
  const payload = {
    scenario_id: "haas_ops_marketplace",
    auto_answer: autoAnswer,
    reasoner,
  };
  if (reasoner === "nim") {
    payload.nim_model = resolveModelSelection();
  }
  const data = await api("/api/runs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  state.selectedRunId = data.run.run_id;
  state.selectedRun = data;
  syncRuntime(data.runtime);
  await loadRuns();
}

async function resumeRun() {
  if (!state.selectedRunId) return;
  const data = await api(`/api/runs/${state.selectedRunId}/resume`, {
    method: "POST",
    body: JSON.stringify({}),
  });
  state.selectedRun = data;
  syncRuntime(data.runtime);
  renderRunDetail();
  renderCheckpoints();
  await loadRuns();
}

async function answerCheckpoint(checkpointId) {
  const form = document.querySelector(`[data-checkpoint-form="${checkpointId}"]`);
  const decision = form.querySelector("select").value;
  const notes = form.querySelector("textarea").value;
  const data = await api(`/api/checkpoints/${checkpointId}/answer`, {
    method: "POST",
    body: JSON.stringify({ decision, notes }),
  });
  state.selectedRun = data;
  syncRuntime(data.runtime);
  renderRunDetail();
  renderCheckpoints();
  await loadRuns();
}

async function connectNim() {
  const apiKey = el("nim-api-key")?.value?.trim() || "";
  const baseUrl = el("nim-base-url")?.value?.trim() || state.runtime?.nim?.base_url || "";
  const modelName = resolveModelSelection();
  const data = await api("/api/nim/connect", {
    method: "POST",
    body: JSON.stringify({
      api_key: apiKey,
      base_url: baseUrl,
      model_name: modelName,
    }),
  });
  if (!state.runtime) state.runtime = {};
  state.runtime.nim = data.nim;
  state.selectedReasoner = "nim";
  renderInferencePanel();
  renderToolbarLabels();
  const keyField = el("nim-api-key");
  if (keyField) keyField.value = "";
}

async function disconnectNim() {
  const data = await api("/api/nim/disconnect", {
    method: "POST",
    body: JSON.stringify({}),
  });
  if (!state.runtime) state.runtime = {};
  state.runtime.nim = data.nim;
  if (!data.nim.connected) {
    state.selectedReasoner = "scripted_nemotron";
  }
  renderInferencePanel();
  renderToolbarLabels();
}

function renderRuns() {
  const container = el("runs-list");
  if (state.runs.length === 0) {
    container.innerHTML = `<div class="empty-state">No runs yet. Start a demo run.</div>`;
    return;
  }

  container.innerHTML = state.runs.map((run) => `
    <button class="run-card ${run.run_id === state.selectedRunId ? "selected" : ""}" data-run-id="${run.run_id}">
      <div class="run-card-top">
        <span class="mono-sm">${escapeHtml(run.run_id)}</span>
        <span class="status-pill ${escapeHtml(statusClass(run.status))}">${escapeHtml(formatStatus(run.status))}</span>
      </div>
      <div class="run-card-body">
        <div class="run-title">${escapeHtml(formatScenarioId(run.scenario_id))}</div>
        <div class="run-meta">${escapeHtml(formatBackend(run.reasoner_backend))} · ${escapeHtml(formatPhase(run.phase))}</div>
        <div class="run-summary">${escapeHtml(summarizeRun(run))}</div>
        <div class="run-meta">${escapeHtml(formatDate(run.updated_at))}</div>
      </div>
    </button>
  `).join("");

  container.querySelectorAll("[data-run-id]").forEach((button) => {
    button.addEventListener("click", () => loadRunDetail(button.dataset.runId));
  });
}

function renderRunDetail() {
  const container = el("run-detail");
  const selected = state.selectedRun;
  if (!selected) {
    renderEmptyPanels();
    return;
  }

  const run = selected.run;
  const report = run.final_report
    ? `<pre class="report-block">${escapeHtml(run.final_report)}</pre>`
    : `<div class="empty-state">No final report yet. Resume the run or answer the pending checkpoint.</div>`;

  container.innerHTML = `
    <div class="detail-header">
      <div>
        <div class="detail-title">${escapeHtml(run.title)}</div>
        <div class="detail-sub">${escapeHtml(selected.scenario.objective)}</div>
      </div>
      <button class="btn-help compact" id="resume-run-btn" ${run.status === "completed" ? "disabled" : ""}>${run.status === "completed" ? "Run Complete" : "Resume Run"}</button>
    </div>

    <div class="detail-note">${escapeHtml(selected.next_step)}</div>

    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">Status</div>
        <div class="metric-value">${escapeHtml(formatStatus(run.status))}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Phase</div>
        <div class="metric-value">${escapeHtml(formatPhase(run.phase))}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Engine</div>
        <div class="metric-value metric-value-sm">${escapeHtml(formatBackend(run.reasoner_backend))}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Lead Progress</div>
        <div class="metric-value">${run.clause_index} / ${selected.scenario.clause_total}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Guardrails</div>
        <div class="metric-value">${run.metrics.guardrail_interventions || 0}</div>
      </div>
    </div>

    <div class="detail-section">
      <div class="lab acc">Runtime</div>
      <div class="meta-pills">
        <span class="option-pill">${escapeHtml(run.target_model)}</span>
        <span class="option-pill">${escapeHtml(run.inference_base_url || "offline-bundled-runtime")}</span>
      </div>
    </div>

    <div class="detail-section">
      <div class="lab acc">Lead Decisions</div>
      <div class="finding-list">
        ${run.findings.length === 0 ? `<div class="empty-state">The run has not analyzed marketplace leads yet.</div>` : run.findings.map((finding) => `
          <div class="finding-card">
            <div class="finding-top">
              <div class="finding-title">${escapeHtml(finding.title)}</div>
              <div class="risk-pill">risk ${finding.risk_level}/10</div>
            </div>
            <div class="finding-copy">${escapeHtml(finding.summary)}</div>
            <div class="finding-copy mint">${escapeHtml(finding.recommendation)}</div>
          </div>
        `).join("")}
      </div>
    </div>

    <div class="detail-section">
      <div class="lab acc">Recent Events</div>
      <div class="event-list">
        ${selected.events.slice(-8).map((event) => `
          <div class="event-row">
            <div class="event-kind">${escapeHtml(titleCase(event.kind))}</div>
            <div class="event-message">${escapeHtml(event.message)}</div>
            <div class="event-time">${escapeHtml(formatDate(event.ts))}</div>
          </div>
        `).join("")}
      </div>
    </div>

    <div class="detail-section">
      <div class="lab acc">Final Report</div>
      ${report}
    </div>
  `;

  el("event-count").textContent = String(selected.events.length);
  el("run-status-chip").textContent = formatStatus(run.status);
  const resumeButton = container.querySelector("#resume-run-btn");
  if (run.status !== "completed") {
    resumeButton.addEventListener("click", async () => {
      try {
        await resumeRun();
      } catch (error) {
        window.alert(error.message);
      }
    });
  }
}

function renderCheckpoints() {
  const container = el("checkpoint-panel");
  const selected = state.selectedRun;
  if (!selected) {
    container.innerHTML = `<div class="empty-state">Select a run to inspect checkpoints.</div>`;
    return;
  }
  const pending = selected.pending_checkpoints;
  if (pending.length === 0) {
    container.innerHTML = `<div class="empty-state">No pending checkpoints. The run can continue or is already complete.</div>`;
    return;
  }

  container.innerHTML = pending.map((checkpoint) => `
    <form class="checkpoint-card" data-checkpoint-form="${checkpoint.checkpoint_id}">
      <div class="checkpoint-id">${escapeHtml(checkpoint.checkpoint_id)}</div>
      <div class="checkpoint-title">${escapeHtml(checkpoint.title)}</div>
      <div class="checkpoint-question">${escapeHtml(checkpoint.question)}</div>
      <div class="checkpoint-options">${checkpoint.options.map((option) => `
        <span class="option-pill">${escapeHtml(titleCase(option))}</span>
      `).join("")}</div>
      <label class="field-label">Decision</label>
      <select>
        ${checkpoint.options.map((option) => `<option value="${escapeHtml(option)}">${escapeHtml(titleCase(option))}</option>`).join("")}
      </select>
      <label class="field-label">Notes</label>
      <textarea placeholder="Add operator notes for this decision..."></textarea>
      <button type="submit" class="btn-help compact wide">Submit Checkpoint</button>
    </form>
  `).join("");

  container.querySelectorAll("[data-checkpoint-form]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await answerCheckpoint(form.dataset.checkpointForm);
      } catch (error) {
        window.alert(error.message);
      }
    });
  });
}

function renderInferencePanel() {
  const container = el("inference-panel");
  const runtime = state.runtime;
  if (!runtime) {
    container.innerHTML = `<div class="empty-state">Loading runtime configuration...</div>`;
    return;
  }

  const nim = runtime.nim || {};
  const isNim = (state.selectedReasoner || runtime.default_reasoner) === "nim";
  const connectLabel = nim.connected ? "Connected" : "Connect NIM";
  const modelOptions = visibleNemotronModels(nim.models).map((model) => `
    <option value="${escapeHtml(model)}" ${model === nim.model_name ? "selected" : ""}>${escapeHtml(model)}</option>
  `).join("");

  container.innerHTML = `
    <div class="inference-block">
      <div class="reasoner-toggle">
        <label class="toggle-card ${!isNim ? "selected" : ""}">
          <input type="radio" name="reasoner" value="scripted_nemotron" ${!isNim ? "checked" : ""} />
          <span class="toggle-title">Offline Demo</span>
          <span class="toggle-copy">No network. Best for deterministic judging.</span>
        </label>
        <label class="toggle-card ${isNim ? "selected" : ""}">
          <input type="radio" name="reasoner" value="nim" ${isNim ? "checked" : ""} />
          <span class="toggle-title">NVIDIA NIM</span>
          <span class="toggle-copy">Connect a hosted open-source model with your API key.</span>
        </label>
      </div>

      <div class="detail-section tight">
        <div class="lab acc">Session Status</div>
        <div class="meta-pills">
          <span class="option-pill ${nim.connected ? "option-pill-live" : ""}">${nim.connected ? "Connected" : "Not Connected"}</span>
          <span class="option-pill">${escapeHtml(nim.source || "none")}</span>
        </div>
        <div class="runtime-banner ${nim.connected ? "runtime-banner-live" : ""}">
          ${nim.connected ? "NIM session is ready. New runs will use the selected hosted Nemotron model." : "No active NIM session. Offline demo remains available."}
        </div>
        <div class="inference-copy">${nim.connected ? `Active model: ${nim.model_name}` : "Enter an NVIDIA API key, choose a model, and connect before starting a live NIM run."}</div>
        <div class="inference-copy subtle">${nim.key_hint ? `Credential hint: ${nim.key_hint}` : "API key is kept in host memory only and is not written to the SQLite runtime."}</div>
      </div>

      <label class="field-label">Base URL</label>
      <input id="nim-base-url" class="text-input" value="${escapeHtml(nim.base_url || "")}" placeholder="https://integrate.api.nvidia.com/v1" />

      <label class="field-label">Model</label>
      <select id="nim-model-select">${modelOptions}</select>

      <label class="field-label">Custom Model Override</label>
      <input id="nim-model-custom" class="text-input" placeholder="Optional: enter any NVIDIA catalog model id" />

      <label class="field-label">NVIDIA API Key</label>
      <input id="nim-api-key" class="text-input" type="password" placeholder="nvapi-..." />

      <div class="toolbar stacked">
        <button class="btn-help compact wide" id="nim-connect-btn" ${nim.connected ? "disabled" : ""}>${connectLabel}</button>
        <button class="btn-skip compact wide" id="nim-disconnect-btn" ${nim.connected ? "" : "disabled"}>Disconnect</button>
      </div>
    </div>
  `;

  container.querySelectorAll('input[name="reasoner"]').forEach((input) => {
    input.addEventListener("change", () => {
      state.selectedReasoner = input.value;
      renderInferencePanel();
      renderToolbarLabels();
    });
  });

  el("nim-connect-btn")?.addEventListener("click", async () => {
    try {
      await connectNim();
    } catch (error) {
      window.alert(error.message);
    }
  });

  el("nim-disconnect-btn")?.addEventListener("click", async () => {
    try {
      await disconnectNim();
    } catch (error) {
      window.alert(error.message);
    }
  });
}

function renderEmptyPanels() {
  el("run-detail").innerHTML = `Select a run to inspect status, checkpoints, events, and report.`;
  el("checkpoint-panel").innerHTML = `Select a run to answer pending checkpoints.`;
  el("event-count").textContent = "0";
  el("run-status-chip").textContent = "Idle";
}

function wireToolbar() {
  el("new-run-btn").addEventListener("click", async () => {
    try {
      await createRun(false);
    } catch (error) {
      window.alert(error.message);
    }
  });
  el("new-auto-run-btn").addEventListener("click", async () => {
    try {
      await createRun(true);
    } catch (error) {
      window.alert(error.message);
    }
  });
  el("refresh-btn").addEventListener("click", async () => {
    try {
      await loadRuns();
    } catch (error) {
      window.alert(error.message);
    }
  });
}

function renderToolbarLabels() {
  const reasoner = state.selectedReasoner || "scripted_nemotron";
  const primary = el("new-run-btn");
  const secondary = el("new-auto-run-btn");
  if (!primary || !secondary) return;
  if (reasoner === "nim") {
    primary.textContent = "Start NIM Run";
    secondary.textContent = "Start Auto NIM Run";
  } else {
    primary.textContent = "Start Demo Run";
    secondary.textContent = "Start Auto Run";
  }
}

async function init() {
  wireToolbar();
  try {
    await loadRuntime();
    await loadRuns();
    renderToolbarLabels();
  } catch (error) {
    el("run-detail").innerHTML = `<div class="empty-state">Failed to load dashboard: ${escapeHtml(error.message)}</div>`;
  }
}

init();
