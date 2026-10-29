/**
 * Smart Business Idea Generator · Main Application JS
 * IBM Granite AI · Multi-Agent System
 */

"use strict";

// ── State ──────────────────────────────────────────────────────────────────
const State = {
  ideas: [],
  trends: {},
  profile: {},
  ethicsReport: {},
  selectedIdea: null,
  currentRoadmap: null,
  compareIds: new Set(),
  charts: {},
  mediaRecorder: null,
  audioChunks: [],
  isRecording: false,
};

// ── API Helpers ────────────────────────────────────────────────────────────
async function apiFetch(url, options = {}) {
  const defaults = {
    headers: { "Content-Type": "application/json" },
  };
  const config = { ...defaults, ...options };
  if (config.body && typeof config.body !== "string" && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
    if (config.body instanceof FormData) delete config.headers["Content-Type"];
  }
  const res = await fetch(url, config);
  return res;
}

// ── Toast ──────────────────────────────────────────────────────────────────
function showToast(message, type = "info", duration = 3500) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.style.display = "block";
  setTimeout(() => { toast.style.display = "none"; }, duration);
}

// ── Tab Switching ──────────────────────────────────────────────────────────
function switchTab(tabName) {
  document.querySelectorAll(".tab-section").forEach(s => (s.style.display = "none"));
  document.querySelectorAll(".nav-pill").forEach(p => p.classList.remove("active"));
  document.getElementById(`tab-${tabName}`).style.display = "block";
  document.querySelector(`[data-tab="${tabName}"]`).classList.add("active");

  if (tabName === "saved") loadSavedIdeas();
  if (tabName === "dashboard" && State.ideas.length > 0) renderDashboard();
}

document.querySelectorAll(".nav-pill").forEach(pill => {
  pill.addEventListener("click", () => switchTab(pill.dataset.tab));
});

// ── Pipeline Status ────────────────────────────────────────────────────────
const PIPELINE_STEPS = ["rag", "trend", "idea", "feasibility", "ethics"];

function resetPipeline() {
  PIPELINE_STEPS.forEach(step => {
    const el = document.getElementById(`step-${step}`);
    if (!el) return;
    el.classList.remove("active", "done");
    el.querySelector(".step-status").textContent = "⏳";
  });
}

function activateStep(step) {
  const el = document.getElementById(`step-${step}`);
  if (!el) return;
  el.classList.add("active");
  el.querySelector(".step-status").textContent = "⚙️";
}

function completeStep(step) {
  const el = document.getElementById(`step-${step}`);
  if (!el) return;
  el.classList.remove("active");
  el.classList.add("done");
  el.querySelector(".step-status").textContent = "✅";
}

// ── Profile Form Submit → Generate ────────────────────────────────────────
document.getElementById("profileForm").addEventListener("submit", async e => {
  e.preventDefault();
  await generateIdeas();
});

async function generateIdeas() {
  const profile = collectProfile();
  if (!profile.name || !profile.interests || !profile.skills) {
    showError("Please fill in Name, Interests, and Skills to continue.");
    return;
  }
  State.profile = profile;

  // UI: Loading state
  const btn = document.getElementById("generateBtn");
  const btnText = document.getElementById("generateBtnText");
  const spinner = document.getElementById("generateSpinner");
  btn.disabled = true;
  btnText.textContent = "AI Agents Working...";
  spinner.style.display = "block";
  hideError();
  resetPipeline();

  // Simulate progressive pipeline activation
  const stepDelays = [200, 800, 1600, 2400, 3200];
  PIPELINE_STEPS.forEach((step, i) => {
    setTimeout(() => activateStep(step), stepDelays[i]);
  });

  try {
    const res = await apiFetch("/api/generate", {
      method: "POST",
      body: JSON.stringify({ profile }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Generation failed.");
    }

    // Complete all steps
    PIPELINE_STEPS.forEach(step => completeStep(step));

    State.ideas = data.ideas || [];
    State.trends = data.trends || {};
    State.ethicsReport = data.ethics_report || {};

    showToast(`✨ Generated ${State.ideas.length} personalised ideas!`, "success");

    // Switch to dashboard
    switchTab("dashboard");
    renderDashboard();
  } catch (err) {
    showError(err.message || "Something went wrong. Please try again.");
    resetPipeline();
  } finally {
    btn.disabled = false;
    btnText.textContent = "✨ Generate My Business Ideas";
    spinner.style.display = "none";
  }
}

function collectProfile() {
  return {
    name: document.getElementById("name").value.trim(),
    interests: document.getElementById("interests").value.trim(),
    skills: document.getElementById("skills").value.trim(),
    budget: document.getElementById("budget").value,
    industry: document.getElementById("industry").value,
    target_audience: document.getElementById("target_audience").value.trim(),
    business_goals: document.getElementById("business_goals").value.trim(),
    location: document.getElementById("location").value.trim(),
    experience: document.getElementById("experience").value,
  };
}

function showError(msg) {
  const el = document.getElementById("inputError");
  el.textContent = msg;
  el.style.display = "block";
}
function hideError() {
  document.getElementById("inputError").style.display = "none";
}

// ── Dashboard Rendering ────────────────────────────────────────────────────
function renderDashboard() {
  const hasIdeas = State.ideas.length > 0;
  document.getElementById("ideasSection").style.display = hasIdeas ? "block" : "none";
  document.getElementById("noDashboard").style.display = hasIdeas ? "none" : "block";
  if (!hasIdeas) return;

  document.getElementById("ideasSubtitle").textContent =
    `${State.ideas.length} ideas personalised for ${State.profile.name || "you"} · IBM Granite AI`;

  renderIdeaCards();
  renderCharts();
  renderTrendsSummary();
  renderEthicsReport();
  renderIdeaMap();
}

// ── Idea Cards ─────────────────────────────────────────────────────────────
function renderIdeaCards() {
  const grid = document.getElementById("ideasGrid");
  grid.innerHTML = "";
  State.ideas.forEach(idea => {
    grid.appendChild(createIdeaCard(idea));
  });
}

function createIdeaCard(idea) {
  const card = document.createElement("div");
  card.className = "idea-card";
  card.dataset.ideaId = idea.id;

  const overall = idea.overall_score || 0;
  const colorFor = s => s >= 80 ? "#24a148" : s >= 60 ? "#1192e8" : s >= 40 ? "#f1c21b" : "#da1e28";
  const recClass = {
    "Highly Recommended": "rec-highly",
    "Recommended": "rec-recommended",
    "Consider Carefully": "rec-consider",
    "Challenging": "rec-challenging",
  }[idea.recommendation] || "rec-recommended";

  card.innerHTML = `
    <div style="position:absolute;top:12px;left:12px;z-index:10">
      <input type="checkbox" class="compare-check-input" data-id="${idea.id}"
        title="Select for comparison" onchange="toggleCompare('${idea.id}', this)" />
    </div>
    <div class="idea-card-header">
      <div class="idea-category-badge">${idea.category || "Startup"}</div>
      <div class="idea-icon">${idea.icon || "💡"}</div>
      <h3>${escHtml(idea.title || "Business Idea")}</h3>
      <div class="idea-tagline">${escHtml(idea.tagline || "")}</div>
    </div>
    <div class="idea-card-body">
      <div class="recommendation-badge ${recClass}">${idea.recommendation || "Recommended"}</div>
      <div class="idea-meta">
        <div class="idea-meta-item">
          <div class="meta-label">Overall</div>
          <div class="meta-value" style="color:${colorFor(overall)}">${overall}</div>
        </div>
        <div class="idea-meta-item">
          <div class="meta-label">Timeline</div>
          <div class="meta-value" style="font-size:11px;margin-top:3px">${escHtml(idea.estimated_timeline || "TBD")}</div>
        </div>
      </div>
      <div class="idea-scores">
        ${scoreBar("Feasibility", idea.feasibility_score, "#1192e8")}
        ${scoreBar("Impact", idea.impact_score, "#a56eff")}
        ${scoreBar("Innovation", idea.innovation_score, "#24a148")}
        ${scoreBar("Market", idea.market_potential_score, "#f1c21b")}
      </div>
      <div class="idea-problem">
        <strong>Problem</strong>
        ${escHtml(idea.problem || "")}
      </div>
    </div>
    <div class="idea-card-footer">
      <button class="btn btn-sm btn-outline" style="flex:1" onclick="viewIdea('${idea.id}')">👁 View</button>
      <button class="btn btn-sm" style="flex:1;background:var(--primary);color:#fff" onclick="openRoadmap('${idea.id}')">🗺 Roadmap</button>
      <button class="btn btn-sm btn-outline" onclick="saveIdea('${idea.id}')" title="Save idea">🔖</button>
    </div>
  `;
  return card;
}

function scoreBar(label, value, color) {
  const v = value || 0;
  return `<div class="score-bar-row">
    <span class="score-label">${label}</span>
    <div class="score-bar-bg"><div class="score-bar-fill" style="width:${v}%;background:${color}"></div></div>
    <span class="score-val">${v}</span>
  </div>`;
}

function toggleCompare(ideaId, checkbox) {
  if (checkbox.checked) {
    State.compareIds.add(ideaId);
  } else {
    State.compareIds.delete(ideaId);
  }
  if (State.compareIds.size >= 2) {
    showToast(`${State.compareIds.size} ideas selected for comparison. Use Compare in dashboard.`, "info");
  }
}

// ── Sort Ideas ─────────────────────────────────────────────────────────────
function sortIdeas(by) {
  if (by === "score") {
    State.ideas.sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0));
  } else if (by === "category") {
    State.ideas.sort((a, b) => (a.category || "").localeCompare(b.category || ""));
  }
  renderIdeaCards();
  showToast("Ideas sorted!", "info", 1500);
}

// ── Charts ─────────────────────────────────────────────────────────────────
function renderCharts() {
  renderRadarChart();
  renderTrendsChart();
  renderRankingChart();
  renderDimensionChart();
}

function destroyChart(id) {
  if (State.charts[id]) { State.charts[id].destroy(); delete State.charts[id]; }
}

function renderRadarChart() {
  destroyChart("radar");
  const ctx = document.getElementById("radarChart").getContext("2d");
  const labels = State.ideas.map(i => truncate(i.title || "Idea", 18));
  const datasets = [
    { label: "Feasibility", data: State.ideas.map(i => i.feasibility_score || 0), borderColor: "#1192e8", backgroundColor: "rgba(17,146,232,.1)" },
    { label: "Impact", data: State.ideas.map(i => i.impact_score || 0), borderColor: "#a56eff", backgroundColor: "rgba(165,110,255,.1)" },
    { label: "Innovation", data: State.ideas.map(i => i.innovation_score || 0), borderColor: "#24a148", backgroundColor: "rgba(36,161,72,.1)" },
  ];
  State.charts["radar"] = new Chart(ctx, {
    type: "bar",
    data: { labels, datasets },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { position: "top" } },
      scales: { y: { beginAtZero: true, max: 100 } },
    },
  });
}

function renderTrendsChart() {
  destroyChart("trends");
  const ctx = document.getElementById("trendsChart").getContext("2d");
  const trendScores = State.trends?.trend_scores || {
    "AI Integration": 90, "Sustainability": 75, "Remote/Digital": 85,
    "Health & Wellness": 70, "Personalisation": 80,
  };
  const labels = Object.keys(trendScores);
  const data = Object.values(trendScores);
  const colors = ["#1192e8", "#a56eff", "#24a148", "#f1c21b", "#da1e28", "#0043ce", "#198038"];

  State.charts["trends"] = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderWidth: 2, borderColor: "#fff" }],
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { position: "right" } },
    },
  });
}

function renderRankingChart() {
  destroyChart("ranking");
  const ctx = document.getElementById("rankingChart").getContext("2d");
  const sorted = [...State.ideas].sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0));
  const labels = sorted.map(i => truncate(i.title || "Idea", 20));
  const data = sorted.map(i => i.overall_score || 0);
  const bgColors = data.map(v => v >= 80 ? "#24a148" : v >= 65 ? "#1192e8" : v >= 50 ? "#f1c21b" : "#da1e28");

  State.charts["ranking"] = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Overall Score", data, backgroundColor: bgColors, borderRadius: 6 }],
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true, max: 100 } },
    },
  });
}

function renderDimensionChart() {
  destroyChart("dimension");
  const ctx = document.getElementById("dimensionChart").getContext("2d");
  const labels = ["Feasibility", "Impact", "Innovation", "Market Potential", "Risk (inv.)"];
  const avg = key => Math.round(State.ideas.reduce((s, i) => s + (i[key] || 0), 0) / (State.ideas.length || 1));
  const data = [
    avg("feasibility_score"), avg("impact_score"), avg("innovation_score"),
    avg("market_potential_score"), 100 - avg("risk_score"),
  ];

  State.charts["dimension"] = new Chart(ctx, {
    type: "radar",
    data: {
      labels,
      datasets: [{
        label: "Average Scores",
        data,
        borderColor: "#0f62fe",
        backgroundColor: "rgba(15,98,254,.15)",
        pointBackgroundColor: "#0f62fe",
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } },
    },
  });
}

// ── Trends Summary ─────────────────────────────────────────────────────────
function renderTrendsSummary() {
  const card = document.getElementById("trendsSummary");
  const content = document.getElementById("trendsContent");
  const t = State.trends;
  if (!t || !t.hot_trends) { card.style.display = "none"; return; }

  card.style.display = "block";
  content.innerHTML = `
    <div class="trends-grid">
      <div class="trend-item">
        <h4>🔥 Hot Trends</h4>
        <ul>${(t.hot_trends || []).map(tr => `<li>${escHtml(tr)}</li>`).join("")}</ul>
      </div>
      <div class="trend-item">
        <h4>⚡ Emerging Technologies</h4>
        <ul>${(t.emerging_technologies || []).map(et => `<li>${escHtml(et)}</li>`).join("")}</ul>
      </div>
      <div class="trend-item">
        <h4>🎯 Market Gaps</h4>
        <ul>${(t.market_gaps || []).map(mg => `<li>${escHtml(mg)}</li>`).join("")}</ul>
      </div>
      <div class="trend-item">
        <h4>👥 Consumer Shifts</h4>
        <ul>${(t.consumer_shifts || []).map(cs => `<li>${escHtml(cs)}</li>`).join("")}</ul>
      </div>
    </div>
    <div style="margin-top:16px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="trend-item">
        <h4>🏢 Competitive Landscape</h4>
        <p style="font-size:13px">${escHtml(t.competitive_landscape || "")}</p>
      </div>
      <div class="trend-item">
        <h4>📈 Growth Forecast</h4>
        <p style="font-size:13px">${escHtml(t.growth_forecast || "")}</p>
      </div>
    </div>
  `;
}

// ── Ethics Report ──────────────────────────────────────────────────────────
function renderEthicsReport() {
  const card = document.getElementById("ethicsCard");
  const content = document.getElementById("ethicsContent");
  const r = State.ethicsReport;
  if (!r || !r.overall_ethics_rating) { card.style.display = "none"; return; }

  card.style.display = "block";
  const ratingColor = { "Excellent": "#24a148", "Good": "#1192e8", "Fair": "#f1c21b", "Needs Review": "#da1e28" };
  content.innerHTML = `
    <div style="margin-bottom:12px">
      <span style="padding:4px 14px;border-radius:12px;background:${ratingColor[r.overall_ethics_rating] || "#1192e8"};color:#fff;font-size:13px;font-weight:700">
        ${r.overall_ethics_rating}
      </span>
      <span style="margin-left:10px;font-size:13px;color:var(--text-muted)">${escHtml(r.compliance_notes || "")}</span>
    </div>
    <div class="ethics-grid">
      <div class="ethics-item">
        <h4>✅ Positive Impacts</h4>
        <ul>${(r.positive_impacts || []).map(p => `<li>${escHtml(p)}</li>`).join("")}</ul>
      </div>
      <div class="ethics-item">
        <h4>⚠️ Considerations</h4>
        <ul>${(r.considerations || []).map(c => `<li>${escHtml(c)}</li>`).join("")}</ul>
      </div>
      <div class="ethics-item">
        <h4>💡 Recommendations</h4>
        <ul>${(r.recommendations || []).map(rec => `<li>${escHtml(rec)}</li>`).join("")}</ul>
      </div>
    </div>
  `;
}

// ── Mind Map ───────────────────────────────────────────────────────────────
function renderIdeaMap() {
  const map = document.getElementById("ideaMap");
  map.innerHTML = "";

  const center = document.createElement("div");
  center.className = "map-node map-node-center";
  center.textContent = `💼 ${State.profile.name || "Your"} Business Hub`;
  map.appendChild(center);

  const typeClasses = {
    "Startup": "map-node-startup",
    "Product": "map-node-product",
    "Research": "map-node-research",
    "Social Enterprise": "map-node-social",
    "Digital": "map-node-digital",
  };

  State.ideas.forEach(idea => {
    const node = document.createElement("div");
    const cls = typeClasses[idea.category] || "map-node-startup";
    node.className = `map-node ${cls}`;
    node.innerHTML = `${idea.icon || "💡"}<br><strong>${escHtml(truncate(idea.title || "", 24))}</strong><br><small>${idea.category}</small>`;
    node.title = idea.tagline || idea.title;
    node.onclick = () => viewIdea(idea.id);
    map.appendChild(node);
  });
}

// ── View Idea Modal ────────────────────────────────────────────────────────
function viewIdea(ideaId) {
  const idea = State.ideas.find(i => i.id === ideaId) || State.ideas.find(i => i.save_id === ideaId);
  if (!idea) return;
  State.selectedIdea = idea;

  document.getElementById("modalTitle").textContent = `${idea.icon || "💡"} ${idea.title}`;

  const body = document.getElementById("modalBody");
  body.innerHTML = `
    <div class="idea-detail-grid">
      <div class="detail-section detail-hero">
        <div class="detail-hero-inner">
          <div style="font-size:40px;margin-bottom:8px">${idea.icon || "💡"}</div>
          <h3>${escHtml(idea.title)}</h3>
          <p>${escHtml(idea.tagline || "")}</p>
          <div class="score-chips" style="justify-content:center;margin-top:12px">
            <span class="score-chip chip-feasibility">Feasibility: ${idea.feasibility_score || 0}</span>
            <span class="score-chip chip-impact">Impact: ${idea.impact_score || 0}</span>
            <span class="score-chip chip-innovation">Innovation: ${idea.innovation_score || 0}</span>
            <span class="score-chip chip-market">Market: ${idea.market_potential_score || 0}</span>
            <span class="score-chip chip-overall">⭐ Overall: ${idea.overall_score || 0}/100</span>
          </div>
        </div>
      </div>
      <div class="detail-section">
        <h4>🎯 Problem</h4>
        <p>${escHtml(idea.problem || "")}</p>
      </div>
      <div class="detail-section">
        <h4>💡 Solution</h4>
        <p>${escHtml(idea.solution || "")}</p>
      </div>
      <div class="detail-section">
        <h4>👥 Target Market</h4>
        <p>${escHtml(idea.target_market || "")}</p>
      </div>
      <div class="detail-section">
        <h4>💰 Revenue Model</h4>
        <p>${escHtml(idea.revenue_model || "")}</p>
      </div>
      <div class="detail-section">
        <h4>⚡ Unique Value</h4>
        <p>${escHtml(idea.unique_value || "")}</p>
      </div>
      <div class="detail-section">
        <h4>📅 Timeline & Cost</h4>
        <p><strong>Launch:</strong> ${escHtml(idea.estimated_timeline || "TBD")}</p>
        <p><strong>Startup Cost:</strong> ${escHtml(idea.startup_cost_estimate || "TBD")}</p>
        <p><strong>Budget Fit:</strong> ${escHtml(idea.budget_fit || "Medium")}</p>
      </div>
      <div class="detail-section">
        <h4>🚀 First Steps</h4>
        <ul>${(idea.initial_steps || []).map(s => `<li>${escHtml(s)}</li>`).join("")}</ul>
      </div>
      <div class="detail-section">
        <h4>🛠️ Required Skills</h4>
        <ul>${(idea.required_skills || []).map(s => `<li>${escHtml(s)}</li>`).join("")}</ul>
      </div>
      <div class="detail-section">
        <h4>⚠️ Key Risks</h4>
        <ul>${(idea.key_risks || []).map(r => `<li>${escHtml(r)}</li>`).join("")}</ul>
      </div>
      <div class="detail-section">
        <h4>✅ Success Factors</h4>
        <ul>${(idea.success_factors || []).map(f => `<li>${escHtml(f)}</li>`).join("")}</ul>
      </div>
    </div>

    <div style="margin-top:16px" class="card" style="background:var(--surface2)">
      <h4 style="margin-bottom:10px;font-size:13px;font-weight:700">💬 Ask the AI about this idea</h4>
      <div style="display:flex;gap:8px">
        <input type="text" id="ideaQueryInput" placeholder="e.g. How do I find my first customers?" style="flex:1" />
        <button class="btn btn-primary btn-sm" onclick="askAboutIdea()">Ask</button>
      </div>
      <div id="ideaQueryResponse" style="margin-top:10px;font-size:13px;color:var(--text-muted);line-height:1.6"></div>
    </div>
  `;

  document.getElementById("modalSaveBtn").onclick = () => saveIdea(idea.id);
  document.getElementById("modalRefineBtn").onclick = () => { closeModal("ideaModal"); openRefine(idea.id); };
  document.getElementById("modalRoadmapBtn").onclick = () => { closeModal("ideaModal"); openRoadmap(idea.id); };

  openModal("ideaModal");
}

async function askAboutIdea() {
  const query = document.getElementById("ideaQueryInput").value.trim();
  if (!query || !State.selectedIdea) return;
  const respEl = document.getElementById("ideaQueryResponse");
  respEl.innerHTML = '<span class="pulsing">Thinking...</span>';
  try {
    const res = await apiFetch("/api/ask", {
      method: "POST",
      body: JSON.stringify({ idea: State.selectedIdea, query, profile: State.profile }),
    });
    const data = await res.json();
    respEl.textContent = data.answer || data.error || "No response received.";
  } catch (err) {
    respEl.textContent = "Error: " + err.message;
  }
}

// ── Refine Idea ────────────────────────────────────────────────────────────
async function openRefine(ideaId) {
  const idea = State.ideas.find(i => i.id === ideaId);
  if (!idea) return;
  State.selectedIdea = idea;

  document.getElementById("refineBody").innerHTML =
    '<div class="loading-state"><div class="spinner-lg"></div><p>IBM Granite is deeply analysing your idea...</p></div>';
  openModal("refineModal");

  try {
    const res = await apiFetch("/api/refine", {
      method: "POST",
      body: JSON.stringify({ idea, profile: State.profile }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    renderRefinement(data.refinement, idea);
  } catch (err) {
    document.getElementById("refineBody").innerHTML = `<div class="alert alert-error">Refinement failed: ${escHtml(err.message)}</div>`;
  }
}

function renderRefinement(r, idea) {
  const gtm = r.go_to_market || {};
  const pricing = r.pricing_strategy || {};
  const html = `
    <div style="margin-bottom:16px;padding:16px;background:linear-gradient(135deg,var(--primary),var(--accent));color:#fff;border-radius:var(--radius-sm)">
      <h3 style="font-size:1.2rem;margin-bottom:6px">${escHtml(r.refined_title || idea.title)}</h3>
    </div>
    <div class="refinement-grid">
      <div class="ref-section ref-full">
        <h4>🎤 Elevator Pitch</h4>
        <p>${escHtml(r.elevator_pitch || "")}</p>
      </div>
      <div class="ref-section ref-full">
        <h4>🔍 Detailed Solution</h4>
        <p>${escHtml(r.detailed_solution || "")}</p>
      </div>
      <div class="ref-section">
        <h4>🛠️ MVP Features</h4>
        <ul>${(r.mvp_features || []).map(f => `<li style="font-size:13px;padding:2px 0 2px 12px;position:relative"><span style="position:absolute;left:0;color:var(--primary)">→</span>${escHtml(f)}</li>`).join("")}</ul>
      </div>
      <div class="ref-section">
        <h4>💰 Pricing Strategy</h4>
        <p><strong>${escHtml(pricing.model || "")}</strong></p>
        <ul>${(pricing.tiers || []).map(t => `<li style="font-size:12px;padding:2px 0">${escHtml(t)}</li>`).join("")}</ul>
      </div>
      <div class="ref-section ref-full">
        <h4>🗓️ Go-to-Market Phases</h4>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:8px">
          <div style="padding:10px;background:var(--primary-light);border-radius:8px;font-size:12px"><strong>Phase 1 (0-3mo)</strong><br>${escHtml(gtm.phase_1 || "")}</div>
          <div style="padding:10px;background:#ede8ff;border-radius:8px;font-size:12px"><strong>Phase 2 (3-6mo)</strong><br>${escHtml(gtm.phase_2 || "")}</div>
          <div style="padding:10px;background:#defbe6;border-radius:8px;font-size:12px"><strong>Phase 3 (6-12mo)</strong><br>${escHtml(gtm.phase_3 || "")}</div>
        </div>
      </div>
      <div class="ref-section">
        <h4>📣 Marketing Channels</h4>
        <ul>${(r.marketing_channels || []).map(c => `<li style="font-size:13px;padding:2px 0 2px 12px;position:relative"><span style="position:absolute;left:0;color:var(--primary)">→</span>${escHtml(c)}</li>`).join("")}</ul>
      </div>
      <div class="ref-section">
        <h4>🤝 Key Partnerships</h4>
        <ul>${(r.partnerships || []).map(p => `<li style="font-size:13px;padding:2px 0 2px 12px;position:relative"><span style="position:absolute;left:0;color:var(--accent)">→</span>${escHtml(p)}</li>`).join("")}</ul>
      </div>
      <div class="ref-section">
        <h4>👥 Team Requirements</h4>
        <ul>${(r.team_requirements || []).map(t => `<li style="font-size:13px;padding:2px 0 2px 12px;position:relative"><span style="position:absolute;left:0;color:var(--success)">→</span>${escHtml(t)}</li>`).join("")}</ul>
      </div>
      <div class="ref-section">
        <h4>💸 Funding Strategy</h4>
        <p style="font-size:13px">${escHtml(r.funding_strategy || "")}</p>
      </div>
      <div class="ref-section ref-full">
        <h4>🏆 Year 1 Milestones</h4>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          ${(r.year_1_milestones || []).map((m, i) => `
            <div style="flex:1;min-width:150px;padding:12px;background:${["var(--primary-light)","#defbe6","#ede8ff"][i%3]};border-radius:8px;font-size:12px">
              <div style="font-weight:700;margin-bottom:4px">Milestone ${i+1}</div>${escHtml(m)}</div>`).join("")}
        </div>
      </div>
    </div>
  `;
  document.getElementById("refineBody").innerHTML = html;
}

// ── Roadmap ────────────────────────────────────────────────────────────────
async function openRoadmap(ideaId) {
  const idea = State.ideas.find(i => i.id === ideaId) || State.ideas.find(i => i.save_id === ideaId);
  if (!idea) return;
  State.selectedIdea = idea;

  document.getElementById("roadmapBody").innerHTML =
    '<div class="loading-state"><div class="spinner-lg"></div><p>Generating your personalised 12-month roadmap...</p></div>';
  openModal("roadmapModal");

  try {
    const res = await apiFetch("/api/roadmap", {
      method: "POST",
      body: JSON.stringify({ idea, profile: State.profile }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    State.currentRoadmap = data.roadmap;
    renderRoadmap(data.roadmap, idea);
  } catch (err) {
    document.getElementById("roadmapBody").innerHTML = `<div class="alert alert-error">Roadmap generation failed: ${escHtml(err.message)}</div>`;
  }
}

function renderRoadmap(r, idea) {
  const phases = r.phases || [];
  const phaseHtml = phases.map(p => `
    <div class="roadmap-phase">
      <div class="phase-header">
        <div class="phase-number">Phase ${p.phase}</div>
        <div class="phase-name">${escHtml(p.name || "")}</div>
        <div class="phase-months">Months ${p.months}</div>
        <span class="phase-theme">${escHtml(p.theme || "")}</span>
      </div>
      <div style="font-size:11px;font-weight:700;color:var(--text-muted);margin-bottom:4px">KEY ACTIONS</div>
      <ul class="phase-actions">${(p.key_actions || []).map(a => `<li>${escHtml(a)}</li>`).join("")}</ul>
      <div style="margin-top:8px;font-size:11px"><strong>Budget:</strong> ${escHtml(p.budget_estimate || "")}</div>
      <div class="phase-milestone">🏁 ${escHtml(p.milestone || "")}</div>
    </div>
  `).join("");

  const html = `
    <div style="margin-bottom:20px;padding:16px;background:linear-gradient(135deg,var(--primary),var(--accent));color:#fff;border-radius:var(--radius-sm)">
      <h3 style="font-size:1.2rem;margin-bottom:4px">${escHtml(r.roadmap_title || "")}</h3>
      <p style="opacity:.9;font-size:13px">${escHtml(r.vision || "")}</p>
      <div style="margin-top:8px;font-size:12px;background:rgba(255,255,255,.15);padding:6px 12px;border-radius:8px;display:inline-block">
        💰 Total Budget: ${escHtml(r.total_budget_estimate || "")}
      </div>
    </div>
    <div class="roadmap-phases">${phaseHtml}</div>
    <div class="roadmap-footer">
      <div class="roadmap-footer-item">
        <h4>🔑 Key Resources</h4>
        <ul>${(r.key_resources || []).map(k => `<li style="font-size:12px;padding:2px 0">• ${escHtml(k)}</li>`).join("")}</ul>
      </div>
      <div class="roadmap-footer-item">
        <h4>🛡️ Risk Mitigation</h4>
        <ul>${(r.risk_mitigation || []).map(rm => `<li style="font-size:12px;padding:2px 0">• ${escHtml(rm)}</li>`).join("")}</ul>
      </div>
      <div class="roadmap-footer-item">
        <h4>🚀 Year 2 Vision</h4>
        <p style="font-size:12px">${escHtml(r.year_2_vision || "")}</p>
      </div>
    </div>
  `;
  document.getElementById("roadmapBody").innerHTML = html;
}

function exportRoadmapTxt() {
  if (!State.currentRoadmap) { showToast("No roadmap to export.", "error"); return; }
  const r = State.currentRoadmap;
  let txt = `${r.roadmap_title || "Innovation Roadmap"}\n${"=".repeat(60)}\n`;
  txt += `Vision: ${r.vision || ""}\n\n`;
  (r.phases || []).forEach(p => {
    txt += `\n--- ${p.name} (Months ${p.months}) ---\n`;
    txt += `Theme: ${p.theme}\n`;
    txt += `Budget: ${p.budget_estimate}\n`;
    txt += `Key Actions:\n${(p.key_actions || []).map(a => `  • ${a}`).join("\n")}\n`;
    txt += `Milestone: ${p.milestone}\n`;
  });
  txt += `\nTotal Budget: ${r.total_budget_estimate}`;
  const blob = new Blob([txt], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = "roadmap.txt"; a.click();
  URL.revokeObjectURL(url);
}

// ── Save & Load Ideas ──────────────────────────────────────────────────────
async function saveIdea(ideaId) {
  const idea = State.ideas.find(i => i.id === ideaId);
  if (!idea) return;
  try {
    const res = await apiFetch("/api/save", { method: "POST", body: JSON.stringify({ idea }) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    showToast("💾 Idea saved successfully!", "success");
  } catch (err) {
    showToast("Failed to save: " + err.message, "error");
  }
}

async function loadSavedIdeas() {
  try {
    const res = await apiFetch("/api/saved");
    const data = await res.json();
    const saved = data.saved_ideas || [];
    const grid = document.getElementById("savedIdeasGrid");
    const noSaved = document.getElementById("noSaved");

    if (saved.length === 0) {
      grid.innerHTML = "";
      noSaved.style.display = "block";
      return;
    }
    noSaved.style.display = "none";
    // Temporarily merge saved into State.ideas for card rendering
    const prevIdeas = State.ideas;
    State.ideas = saved;
    grid.innerHTML = "";
    saved.forEach(idea => {
      const card = createIdeaCard(idea);
      // Override footer to show delete option
      const footer = card.querySelector(".idea-card-footer");
      footer.innerHTML = `
        <button class="btn btn-sm btn-outline" style="flex:1" onclick="viewSavedIdea('${idea.save_id}')">👁 View</button>
        <button class="btn btn-sm btn-danger" style="flex:1" onclick="deleteSaved('${idea.save_id}')">🗑 Delete</button>
      `;
      grid.appendChild(card);
    });
    State.ideas = prevIdeas;
  } catch (err) {
    showToast("Failed to load saved ideas.", "error");
  }
}

async function deleteSaved(saveId) {
  if (!confirm("Delete this saved idea?")) return;
  try {
    const res = await apiFetch(`/api/saved/${saveId}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Delete failed");
    showToast("Idea deleted.", "info");
    loadSavedIdeas();
  } catch (err) {
    showToast("Failed to delete.", "error");
  }
}

function viewSavedIdea(saveId) {
  // Load saved ideas, then show detail
  apiFetch("/api/saved").then(r => r.json()).then(data => {
    const idea = (data.saved_ideas || []).find(i => i.save_id === saveId);
    if (!idea) return;
    const prevIdeas = State.ideas;
    if (!State.ideas.find(i => i.save_id === saveId)) {
      State.ideas = [...State.ideas, idea];
    }
    viewIdea(saveId);
    State.ideas = prevIdeas;
  });
}

async function exportSaved() {
  const res = await apiFetch("/api/saved");
  const data = await res.json();
  if (!data.saved_ideas?.length) { showToast("No saved ideas to export.", "error"); return; }
  exportIdeasData(data.saved_ideas, "txt");
}

// ── Export ─────────────────────────────────────────────────────────────────
function showExportOptions() {
  openModal("exportModal");
}

async function exportIdeas(format) {
  closeModal("exportModal");
  try {
    const res = await apiFetch(`/api/export/${format}`, {
      method: "POST",
      body: JSON.stringify({ ideas: State.ideas, profile: State.profile }),
    });
    if (!res.ok) throw new Error("Export failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `business_ideas.${format}`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`Ideas exported as ${format.toUpperCase()}!`, "success");
  } catch (err) {
    showToast("Export failed: " + err.message, "error");
  }
}

function exportIdeasData(ideas, format) {
  let content = "Smart Business Idea Generator\nPowered by IBM Granite\n\n";
  ideas.forEach((idea, i) => {
    content += `${i+1}. ${idea.title}\n${"─".repeat(40)}\n`;
    content += `Category: ${idea.category}\nScore: ${idea.overall_score}/100\n`;
    content += `Problem: ${idea.problem}\nSolution: ${idea.solution}\n\n`;
  });
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = "saved_ideas.txt"; a.click();
  URL.revokeObjectURL(url);
}

// ── Compare ────────────────────────────────────────────────────────────────
// Button in dashboard header triggers compare
function compareSelected() {
  if (State.compareIds.size < 2) { showToast("Select at least 2 ideas using the checkboxes.", "error"); return; }
  const selectedIdeas = State.ideas.filter(i => State.compareIds.has(i.id));
  renderCompare(selectedIdeas);
}

function renderCompare(ideas) {
  if (!ideas || ideas.length < 2) { showToast("Select at least 2 ideas.", "error"); return; }
  const dims = ["feasibility_score", "impact_score", "innovation_score", "market_potential_score", "overall_score"];
  const labels = ["Feasibility", "Impact", "Innovation", "Market", "Overall"];

  const rows = dims.map((d, i) => `
    <tr>
      <td><strong>${labels[i]}</strong></td>
      ${ideas.map(idea => `<td style="text-align:center;font-weight:700;color:${(idea[d]||0)>=75?"var(--success)":"var(--text)"}">${idea[d] || 0}</td>`).join("")}
    </tr>
  `).join("");

  const html = `
    <table class="compare-table">
      <thead>
        <tr>
          <th>Dimension</th>
          ${ideas.map(i => `<th>${escHtml(i.icon || "💡")} ${escHtml(i.title || "Idea")}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
        ${rows}
        <tr>
          <td><strong>Category</strong></td>
          ${ideas.map(i => `<td>${escHtml(i.category || "")}</td>`).join("")}
        </tr>
        <tr>
          <td><strong>Timeline</strong></td>
          ${ideas.map(i => `<td>${escHtml(i.estimated_timeline || "")}</td>`).join("")}
        </tr>
        <tr>
          <td><strong>Startup Cost</strong></td>
          ${ideas.map(i => `<td>${escHtml(i.startup_cost_estimate || "")}</td>`).join("")}
        </tr>
        <tr>
          <td><strong>Recommendation</strong></td>
          ${ideas.map(i => `<td><strong>${escHtml(i.recommendation || "")}</strong></td>`).join("")}
        </tr>
      </tbody>
    </table>
    <div class="compare-chart-wrap">
      <canvas id="compareChartCanvas" height="120"></canvas>
    </div>
  `;
  document.getElementById("compareBody").innerHTML = html;
  openModal("compareModal");

  // Render comparison chart
  const ctx = document.getElementById("compareChartCanvas").getContext("2d");
  new Chart(ctx, {
    type: "radar",
    data: {
      labels,
      datasets: ideas.map((idea, idx) => ({
        label: idea.title || `Idea ${idx+1}`,
        data: dims.map(d => idea[d] || 0),
        borderColor: ["#1192e8","#a56eff","#24a148","#f1c21b"][idx % 4],
        backgroundColor: ["rgba(17,146,232,.1)","rgba(165,110,255,.1)","rgba(36,161,72,.1)","rgba(241,194,27,.1)"][idx % 4],
        borderWidth: 2,
      })),
    },
    options: {
      responsive: true,
      scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } },
    },
  });
}

// ── Chat ───────────────────────────────────────────────────────────────────
async function sendChatMessage() {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  addChatMessage("user", message);
  input.value = "";

  const thinkingId = addChatMessage("bot", '<span class="pulsing">IBM Granite is thinking...</span>');

  try {
    const res = await apiFetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, profile: State.profile }),
    });
    const data = await res.json();
    updateChatMessage(thinkingId, data.response || data.error || "No response.");
  } catch (err) {
    updateChatMessage(thinkingId, "Connection error. Please try again.");
  }
}

function addChatMessage(role, html) {
  const messages = document.getElementById("chatMessages");
  const id = "msg_" + Date.now();
  const avatar = role === "bot" ? "🤖" : "👤";
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.id = id;
  div.innerHTML = `<span class="msg-avatar">${avatar}</span><div class="msg-bubble">${html}</div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return id;
}

function updateChatMessage(id, text) {
  const el = document.getElementById(id);
  if (!el) return;
  const bubble = el.querySelector(".msg-bubble");
  if (bubble) bubble.innerHTML = text.replace(/\n\n/g, "<br><br>").replace(/\n/g, "<br>");
  document.getElementById("chatMessages").scrollTop = document.getElementById("chatMessages").scrollHeight;
}

function sendQuickPrompt(prompt) {
  document.getElementById("chatInput").value = prompt;
  sendChatMessage();
}

document.getElementById("chatInput").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChatMessage(); }
});

// ── Image Upload ───────────────────────────────────────────────────────────
document.getElementById("imageInput").addEventListener("change", async e => {
  const file = e.target.files[0];
  if (!file) return;

  const preview = document.getElementById("imagePreview");
  const img = document.createElement("img");
  img.src = URL.createObjectURL(file);
  preview.innerHTML = "";
  preview.appendChild(img);
  preview.style.display = "block";

  const form = new FormData();
  form.append("image", file);
  try {
    const res = await fetch("/api/upload/image", { method: "POST", body: form });
    const data = await res.json();
    if (data.keywords) {
      const kw = data.keywords.join(", ");
      const interestsEl = document.getElementById("interests");
      if (!interestsEl.value.includes(kw)) {
        interestsEl.value = interestsEl.value ? `${interestsEl.value}, ${kw}` : kw;
      }
    }
    showToast("🖼️ Image analysed! Keywords added to your interests.", "success");
  } catch (err) {
    showToast("Image upload failed.", "error");
  }
});

// ── Voice Recording ────────────────────────────────────────────────────────
async function toggleRecording() {
  const btn = document.getElementById("recordBtn");
  const status = document.getElementById("audioStatus");

  if (!State.isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      State.mediaRecorder = new MediaRecorder(stream);
      State.audioChunks = [];
      State.mediaRecorder.ondataavailable = e => State.audioChunks.push(e.data);
      State.mediaRecorder.onstop = uploadRecording;
      State.mediaRecorder.start();
      State.isRecording = true;
      btn.textContent = "⏹ Stop Recording";
      btn.style.background = "var(--danger)";
      status.textContent = "🔴 Recording...";
    } catch (err) {
      showToast("Microphone access denied. Please allow microphone access.", "error");
    }
  } else {
    State.mediaRecorder.stop();
    State.mediaRecorder.stream.getTracks().forEach(t => t.stop());
    State.isRecording = false;
    btn.textContent = "Start Recording";
    btn.style.background = "";
    status.textContent = "Processing...";
  }
}

async function uploadRecording() {
  const blob = new Blob(State.audioChunks, { type: "audio/webm" });
  const form = new FormData();
  form.append("audio", blob, "recording.webm");
  try {
    const res = await fetch("/api/upload/audio", { method: "POST", body: form });
    const data = await res.json();
    if (data.transcript) {
      document.getElementById("business_goals").value = data.transcript;
      document.getElementById("audioStatus").textContent = "✅ Voice input added!";
      showToast("🎙️ Voice transcribed and added to your goals!", "success");
    }
  } catch (err) {
    document.getElementById("audioStatus").textContent = "Transcription failed.";
  }
}

document.getElementById("audioInput").addEventListener("change", async e => {
  const file = e.target.files[0];
  if (!file) return;
  const form = new FormData();
  form.append("audio", file);
  document.getElementById("audioStatus").textContent = "Transcribing...";
  try {
    const res = await fetch("/api/upload/audio", { method: "POST", body: form });
    const data = await res.json();
    if (data.transcript) {
      document.getElementById("business_goals").value = data.transcript;
      document.getElementById("audioStatus").textContent = "✅ Voice transcribed!";
      showToast("Voice input processed!", "success");
    }
  } catch {
    document.getElementById("audioStatus").textContent = "Transcription failed.";
  }
});

// ── Modal Helpers ──────────────────────────────────────────────────────────
function openModal(id) { document.getElementById(id).style.display = "flex"; document.body.style.overflow = "hidden"; }
function closeModal(id) { document.getElementById(id).style.display = "none"; document.body.style.overflow = ""; }
document.addEventListener("keydown", e => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal").forEach(m => { if (m.style.display !== "none") closeModal(m.id); });
  }
});

// ── Utility ────────────────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return "";
  return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function truncate(str, n) { return str.length > n ? str.slice(0, n) + "…" : str; }

// ── Dashboard Compare Button ───────────────────────────────────────────────
// Add compare button to dashboard header actions
document.addEventListener("DOMContentLoaded", () => {
  const actions = document.querySelector(".dashboard-actions");
  if (actions) {
    const compareBtn = document.createElement("button");
    compareBtn.className = "btn btn-sm btn-outline";
    compareBtn.textContent = "⚖️ Compare Selected";
    compareBtn.onclick = compareSelected;
    actions.insertBefore(compareBtn, actions.firstChild);
  }

  // Check API health
  fetch("/api/health").then(r => r.json()).then(data => {
    if (data.status !== "ok") {
      document.getElementById("apiStatus").innerHTML = '<span class="status-dot error"></span> Offline';
    }
  }).catch(() => {
    document.getElementById("apiStatus").innerHTML = '<span class="status-dot error"></span> Offline';
  });
});

// ── Drag & Drop for images ─────────────────────────────────────────────────
const imageZone = document.getElementById("imageUploadZone");
imageZone.addEventListener("dragover", e => { e.preventDefault(); imageZone.style.borderColor = "var(--primary)"; });
imageZone.addEventListener("dragleave", () => { imageZone.style.borderColor = ""; });
imageZone.addEventListener("drop", e => {
  e.preventDefault();
  imageZone.style.borderColor = "";
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) {
    const dt = new DataTransfer();
    dt.items.add(file);
    document.getElementById("imageInput").files = dt.files;
    document.getElementById("imageInput").dispatchEvent(new Event("change"));
  }
});
