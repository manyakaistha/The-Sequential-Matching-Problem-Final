const state = {
  config: null,
  run: null,
  events: [],
  eventsCursor: 0,
  selectedMemberId: null,
  memberFilter: "all",
  playTimer: null,
  transitionBusy: false,
  operationToken: 0,
  compareRuns: {},
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const dom = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

function shortId(id) {
  return id ? `…${id.slice(-6)}` : "—";
}

function humanField(field) {
  const names = {
    age_min: "minimum age", age_max: "maximum age", who_to_meet: "who to meet",
    relationship_structure: "relationship structure", smoking: "smoking", partner_smoking: "partner smoking",
    has_children: "children", partner_children: "partner children", wants_children: "children plans",
    acceptable_zones: "acceptable zones", schedule: "schedule",
  };
  return names[field] || field.replaceAll("_", " ");
}

function initials(member) {
  const code = member.member_id.replace("syn_", "");
  return code.slice(0, 2).toUpperCase();
}

function showView(name) {
  ["overview", "simulation", "compare"].forEach((view) => {
    const section = $(`#${view}-view`);
    section.classList.toggle("is-hidden", view !== name);
  });
  $$(".nav-link").forEach((button) => button.classList.toggle("is-active", button.dataset.nav === name));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function setMessage(message, isError = false, target = "#run-message") {
  const node = $(target);
  if (!node) return;
  node.textContent = message || "";
  node.classList.toggle("is-error", isError);
}

let toastTimer;
function toast(message) {
  const node = $("#toast");
  node.textContent = message;
  node.classList.add("is-visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove("is-visible"), 3200);
}

async function api(path, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }
  let response;
  try {
    response = await fetch(path, { ...options, headers });
  } catch (error) {
    const networkError = new Error("The service is waking up or the network is unavailable.");
    networkError.network = true;
    throw networkError;
  }
  let payload = null;
  if (response.status !== 204) {
    try { payload = await response.json(); } catch (_) { payload = null; }
  }
  if (!response.ok) {
    const error = new Error(payload?.error?.message || `Request failed (${response.status}).`);
    error.status = response.status;
    error.code = payload?.error?.code;
    throw error;
  }
  return payload;
}

function setBusy(busy) {
  state.transitionBusy = busy;
  ["#next-phase", "#next-day", "#finish-button", "#export-button"].forEach((selector) => {
    const node = $(selector);
    if (node) node.disabled = busy;
  });
  const compare = $("#start-compare");
  if (compare) compare.disabled = busy;
}

async function startRun(policy = "greedy", presetId = "public-101-development") {
  stopPlay();
  const operationToken = state.operationToken;
  setBusy(true);
  setMessage("Creating a fresh synthetic episode…");
  try {
    const run = await api("/api/v1/runs", { method: "POST", body: { preset_id: presetId, policy } });
    if (operationToken !== state.operationToken) return;
    state.run = run;
    state.events = [];
    state.eventsCursor = 0;
    state.selectedMemberId = null;
    showView("simulation");
    renderRun();
    await loadEvents();
    setMessage("Ready. The first phase is questioning; no day has advanced yet.");
  } catch (error) {
    setMessage(error.message, true);
    toast(error.message);
  } finally {
    setBusy(false);
  }
}

async function loadEvents() {
  if (!state.run) return;
  try {
    const result = await api(`/api/v1/runs/${encodeURIComponent(state.run.run_id)}/events?after=${state.eventsCursor}&limit=100`);
    state.events.push(...result.events);
    state.eventsCursor = result.next_cursor;
    renderTimeline();
  } catch (error) {
    if (error.status === 410) handleExpired();
  }
}

function handleExpired() {
  stopPlay();
  setMessage("This run expired from the in-memory store. Start a new public preset to continue.", true);
  toast("Run expired — a fresh episode is ready from the overview.");
  state.run = null;
  showView("overview");
}

async function advance(steps = 1) {
  if (!state.run || state.transitionBusy || state.run.status === "complete") return;
  const operationToken = state.operationToken;
  setBusy(true);
  try {
    const result = await api(`/api/v1/runs/${encodeURIComponent(state.run.run_id)}/advance`, {
      method: "POST",
      body: { expected_revision: state.run.revision, steps, idempotency_key: `web-${state.run.run_id}-${state.run.revision}-${crypto.randomUUID()}` },
    });
    if (operationToken !== state.operationToken) return;
    state.run = result;
    renderRun();
    await loadEvents();
    if (state.run.status === "complete") {
      stopPlay();
      setMessage("Follow-up is complete. The funnel now shows final observed outcomes for this episode.");
    } else {
      setMessage(steps > 1 ? `Advanced ${steps} bounded phases.` : "Phase advanced. Read the released trace below.");
    }
  } catch (error) {
    if (error.status === 409) {
      setMessage("This run changed in another tab or request. Refreshing its public snapshot…", true);
      await refreshRun();
    } else if (error.status === 410) {
      handleExpired();
    } else {
      setMessage(error.message, true);
      toast(error.message);
    }
  } finally {
    setBusy(false);
  }
}

async function refreshRun() {
  if (!state.run) return;
  try {
    state.run = await api(`/api/v1/runs/${encodeURIComponent(state.run.run_id)}`);
    renderRun();
    await loadEvents();
  } catch (error) {
    if (error.status === 410) handleExpired();
    else setMessage(error.message, true);
  }
}

async function nextDay() {
  if (!state.run) return;
  const steps = state.run.phase === "ask" && state.run.day < 60 ? 2 : 1;
  await advance(steps);
}

async function finishEpisode() {
  if (!state.run || state.transitionBusy) return;
  const operationToken = state.operationToken;
  setBusy(true);
  setMessage("Finishing in bounded four-phase requests…");
  try {
    let guard = 0;
    while (state.run.status !== "complete" && guard < 40) {
      const result = await api(`/api/v1/runs/${encodeURIComponent(state.run.run_id)}/advance`, {
        method: "POST",
        body: { expected_revision: state.run.revision, steps: 4, idempotency_key: `finish-${state.run.run_id}-${state.run.revision}` },
      });
      if (operationToken !== state.operationToken) return;
      state.run = result;
      renderRun();
      guard += 1;
      if (guard % 3 === 0) setMessage(`Finishing episode… ${state.run.day} / 100 days observed.`);
    }
    await loadEvents();
    setMessage(state.run.status === "complete" ? "Episode complete. Outcomes are now mature through the 40-day follow-up." : "Finish paused at the bounded request limit; continue when ready.");
  } catch (error) {
    if (error.status === 410) handleExpired();
    else setMessage(error.message, true);
  } finally {
    setBusy(false);
  }
}

function stopPlay() {
  if (state.playTimer) window.clearTimeout(state.playTimer);
  state.playTimer = null;
  const button = $("#play-button");
  if (button) button.setAttribute("aria-pressed", "false");
  if ($("#play-icon")) $("#play-icon").textContent = "▶";
  if ($("#play-label")) $("#play-label").textContent = "Play";
}

async function playLoop() {
  if (!state.run || state.run.status === "complete" || !state.playTimer) return;
  await advance(1);
  if (state.run && state.run.status !== "complete" && state.playTimer) state.playTimer = window.setTimeout(playLoop, 1100);
  else stopPlay();
}

function togglePlay() {
  if (state.playTimer) { stopPlay(); return; }
  if (!state.run || state.run.status === "complete") return;
  const button = $("#play-button");
  button.setAttribute("aria-pressed", "true");
  $("#play-icon").textContent = "Ⅱ";
  $("#play-label").textContent = "Pause";
  state.playTimer = window.setTimeout(playLoop, 80);
}

function renderRun() {
  const run = state.run;
  if (!run) return;
  const preset = state.config?.presets.find((item) => item.id === run.preset_id);
  $("#run-preset-label").textContent = preset?.label || run.preset_id;
  $("#run-policy").textContent = run.policy.replace("_", " ").toUpperCase();
  $("#run-id").textContent = `RUN ${shortId(run.run_id)} · REV ${run.revision}`;
  $("#day-label").textContent = `DAY ${String(run.day).padStart(2, "0")}`;
  const phaseNames = { ask: "Questioning", match: "Matching", followup: "Follow-up", complete: "Complete" };
  $("#phase-label").textContent = phaseNames[run.phase] || run.phase;
  $("#phase-detail").textContent = run.phase === "ask" ? "Observe and ask before matching" : run.phase === "match" ? "Choose a non-overlapping feasible batch" : run.phase === "followup" ? "Let delayed feedback mature" : "All public outcomes observed";
  $$(".phase-step").forEach((step) => {
    const phase = step.dataset.phaseStep;
    const currentIndex = ["ask", "match", "followup"].indexOf(run.phase === "complete" ? "followup" : run.phase);
    const phaseIndex = ["ask", "match", "followup"].indexOf(phase);
    step.classList.toggle("is-current", phase === (run.phase === "complete" ? "followup" : run.phase));
    step.classList.toggle("is-done", phaseIndex < currentIndex);
  });
  const metrics = run.metrics;
  $("#metric-budget").textContent = String(run.state.ask_budget_remaining ?? 12);
  $("#metric-budget-sub").textContent = run.phase === "ask" ? "units remaining today" : "units at last questioning phase";
  $("#budget-fill").style.width = `${Math.max(0, Math.min(100, (12 - (run.state.ask_budget_remaining ?? 12)) / 12 * 100))}%`;
  $("#metric-assignments").textContent = String(metrics.assignments);
  $("#metric-dates").textContent = String(metrics.dates);
  $("#metric-msmi").textContent = String(metrics.mutual_second_meeting_intention);
  $("#metric-msmi-sub").textContent = metrics.status === "final" ? "final qualified outcomes" : "provisional outcome count";
  $("#metric-coverage").textContent = `${Math.round(metrics.coverage * 100)}%`;
  $("#metric-coverage-sub").textContent = `${metrics.served_members} served / ${metrics.arrived_members} arrived`;
  $("#member-count").textContent = String(run.state.members.filter((member) => member.available).length);
  renderMembers();
  renderLatestAction();
  renderFunnel();
  if (state.selectedMemberId) loadInspection(state.selectedMemberId);
}

function renderMembers() {
  if (!state.run) return;
  const members = state.run.state.members || [];
  const search = ($( "#member-search")?.value || "").trim().toLowerCase();
  const rows = members.filter((member) => {
    if (state.memberFilter === "available" && !member.available) return false;
    if (!search) return true;
    return [member.member_id, member.zone, member.gender, member.available ? "available" : "waiting"].some((value) => String(value).toLowerCase().includes(search));
  }).sort((a, b) => Number(b.available) - Number(a.available) || a.arrived_day - b.arrived_day || a.member_id.localeCompare(b.member_id));
  const body = $("#member-table-body");
  body.replaceChildren();
  rows.forEach((member, index) => {
    const row = document.createElement("tr");
    row.className = `member-row${state.selectedMemberId === member.member_id ? " is-selected" : ""}`;
    row.tabIndex = 0;
    row.setAttribute("role", "button");
    row.setAttribute("aria-label", `Inspect synthetic member ${shortId(member.member_id)}`);
    row.addEventListener("click", () => selectMember(member.member_id));
    row.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); selectMember(member.member_id); } });
    const identity = document.createElement("td");
    const name = dom("div", "member-name");
    name.append(dom("span", `avatar ${index % 3 === 1 ? "alt" : index % 3 === 2 ? "warm" : ""}`, initials(member)));
    const identityText = document.createElement("span");
    identityText.append(dom("span", "member-id", shortId(member.member_id)));
    name.append(identityText); identity.append(name);
    const ageZone = document.createElement("td");
    ageZone.append(dom("span", "member-zone", `${member.age} · ${member.zone.replace("zone_", "zone ")}`));
    const fields = document.createElement("td");
    const unknown = Object.entries(member.fields).filter(([key, value]) => ["age_min", "age_max", "who_to_meet", "relationship_structure", "smoking", "partner_smoking", "has_children", "partner_children", "wants_children", "acceptable_zones", "schedule"].includes(key) && value === null).length;
    fields.append(dom("span", `field-state ${unknown ? "needs" : "ready"}`, `${unknown ? `${unknown} hard fields missing` : "hard fields known"}`));
    const availability = document.createElement("td");
    availability.append(dom("span", `availability ${member.available ? "ready" : "busy"}`, member.available ? "available" : "waiting"));
    row.append(identity, ageZone, fields, availability); body.append(row);
  });
  $("#member-table-note").textContent = `${rows.length} matching public records shown. Select a row to inspect reciprocal eligibility; unknown is never treated as rejection.`;
}

async function selectMember(memberId) {
  state.selectedMemberId = memberId;
  renderMembers();
  await loadInspection(memberId);
}

async function loadInspection(memberId) {
  if (!state.run) return;
  try {
    const result = await api(`/api/v1/runs/${encodeURIComponent(state.run.run_id)}/members/${encodeURIComponent(memberId)}/inspection`);
    renderInspector(result);
  } catch (error) {
    if (error.status === 410) handleExpired();
    else setMessage(error.message, true);
  }
}

function renderInspector(data) {
  const member = state.run.state.members.find((item) => item.member_id === data.member_id);
  const content = $("#inspector-content"); content.replaceChildren(); content.className = "inspector-detail";
  const head = dom("div", "inspector-member"); head.append(dom("span", "avatar alt", initials(member)), dom("div"));
  const text = head.lastChild; text.append(dom("h3", "", `Member ${shortId(member.member_id)}`), dom("p", "", `${member.age} · ${member.gender} · ${member.zone.replace("zone_", "zone ")}`));
  content.append(head);
  const summary = dom("div", "inspector-summary");
  const missing = Object.entries(member.fields).filter(([key, value]) => ["age_min", "age_max", "who_to_meet", "relationship_structure", "smoking", "partner_smoking", "has_children", "partner_children", "wants_children", "acceptable_zones", "schedule"].includes(key) && value === null).map(([key]) => key);
  summary.append(dom("div", "mini-stat", ""), dom("div", "mini-stat", ""));
  summary.children[0].append(dom("span", "", "hard fields missing"), dom("strong", "", String(missing.length)));
  summary.children[1].append(dom("span", "", "current status"), dom("strong", "", member.available ? "available" : "waiting"));
  content.append(summary);
  if (missing.length) {
    content.append(dom("p", "inspector-label", "Clarification needed"));
    const list = dom("div", "eligibility-list");
    missing.forEach((field) => list.append(dom("div", "eligibility-item needs", `${humanField(field)} is not observable yet`)));
    content.append(list);
  }
  content.append(dom("p", "inspector-label", "Focused candidate view"));
  const candidates = dom("div", "eligibility-list");
  data.candidates.slice(0, 12).forEach((candidate) => {
    const item = dom("button", `eligibility-item ${candidate.status === "feasible" ? "feasible" : candidate.status === "needs_clarification" ? "needs" : "infeasible"}`);
    item.type = "button";
    const missingText = candidate.missing?.length ? ` · missing ${candidate.missing.slice(0, 2).map((entry) => humanField(entry.split(":").pop())).join(", ")}` : "";
    item.textContent = `${shortId(candidate.member_id)} · ${candidate.status.replaceAll("_", " ")}${missingText}`;
    item.addEventListener("click", () => selectMember(candidate.member_id));
    candidates.append(item);
  });
  content.append(candidates);
  content.append(dom("p", "inspector-note", "Reasons are translated from the kit’s public eligibility checks. A soft match cannot override an infeasible hard constraint."));
}

function renderLatestAction() {
  const target = $("#latest-action"); target.replaceChildren();
  const action = state.run?.recent_action;
  if (!action) { target.append(dom("p", "empty-copy", "Start the run to reveal the policy’s first action.")); return; }
  const callout = dom("div", "action-callout");
  callout.append(dom("span", "action-icon", action.phase === "ask" ? "?" : action.phase === "match" ? "↗" : "◷"));
  const copy = dom("div");
  const title = action.phase === "ask" ? "Questions applied" : action.phase === "match" ? "Batch advanced" : "Follow-up released";
  copy.append(dom("h3", "", title));
  let detail = "The public observation was refreshed without advancing the simulator day.";
  if (action.phase === "match") detail = `${action.pairs?.length || 0} selected pair${action.pairs?.length === 1 ? "" : "s"}; each member is used at most once.`;
  if (action.phase === "followup") detail = "No new introductions are made after day 60; delayed feedback can still arrive.";
  copy.append(dom("p", "", detail));
  if (action.asks?.length) {
    const tags = dom("div", "action-tags");
    action.asks.slice(0, 6).forEach((ask) => tags.append(dom("span", "action-tag", `${shortId(ask.member_id)} · ${ask.field} · ${ask.field === "constraints" ? 3 : 1}u`)));
    copy.append(tags);
  }
  if (action.pairs?.length) {
    const tags = dom("div", "action-tags");
    action.pairs.slice(0, 6).forEach((pair) => tags.append(dom("span", "action-tag", `${shortId(pair[0])} ↔ ${shortId(pair[1])}`)));
    copy.append(tags);
  }
  callout.append(copy); target.append(callout);
}

function renderFunnel() {
  const target = $("#outcome-funnel"); target.replaceChildren();
  const funnel = state.run?.state.outcome_funnel || [];
  const max = Math.max(1, ...funnel.map((item) => item.value));
  funnel.forEach((item) => {
    const row = dom("div", "funnel-row");
    row.title = item.definition;
    const label = dom("span", "funnel-label", item.label); row.append(label, dom("span", "funnel-value", String(item.value)));
    const track = dom("div", "funnel-track"); const fill = dom("span"); fill.style.width = `${Math.max(2, item.value / max * 100)}%`; track.append(fill); row.append(track); target.append(row);
  });
}

function renderTimeline() {
  const target = $("#timeline"); target.replaceChildren();
  const events = state.events.slice(-8).reverse();
  if (!events.length) { target.append(dom("p", "empty-copy", "Events will appear here as the episode advances.")); return; }
  events.forEach((event) => {
    const item = dom("article", `timeline-item ${event.event_type}`);
    item.append(dom("span", "timeline-day", `day ${String(event.day).padStart(2, "0")} · ${event.phase}`));
    let title = "Policy action"; let description = "Public action recorded.";
    if (event.event_type === "feedback_released") { title = "Feedback released"; const feedback = event.payload.feedback; description = `${feedback.event.replaceAll("_", " ")} · ${feedback.value === null ? "no response yet" : String(feedback.value)}`; }
    else if (event.payload.phase === "ask") { title = "Clarification phase"; description = `${event.payload.asks?.length || 0} question${event.payload.asks?.length === 1 ? "" : "s"} applied; refreshed state is public.`; }
    else if (event.payload.phase === "match") { title = "Matching phase"; description = `${event.payload.pairs?.length || 0} introduction${event.payload.pairs?.length === 1 ? "" : "s"} selected.`; }
    else if (event.payload.phase === "followup") { title = "Follow-up day"; description = "Empty introductions; the simulator released any mature feedback."; }
    item.append(dom("h3", "", title), dom("p", "", description)); target.append(item);
  });
}

async function startComparison() {
  setBusy(true); setMessage("", false, "#compare-message");
  const policies = ["greedy", "no_asks", "random"];
  try {
    const created = await Promise.all(policies.map((policy) => api("/api/v1/runs", { method: "POST", body: { preset_id: "public-101-development", policy } })));
    state.compareRuns = Object.fromEntries(created.map((run) => [run.policy, run]));
    renderCompareCards();
    let guard = 0;
    while (Object.values(state.compareRuns).some((run) => run.status !== "complete") && guard < 40) {
      const pairs = Object.entries(state.compareRuns).filter(([, run]) => run.status !== "complete");
      const advanced = await Promise.all(pairs.map(async ([policy, run]) => [policy, await api(`/api/v1/runs/${encodeURIComponent(run.run_id)}/advance`, { method: "POST", body: { expected_revision: run.revision, steps: 4, idempotency_key: `compare-${policy}-${run.revision}` } })]));
      advanced.forEach(([policy, run]) => { state.compareRuns[policy] = run; });
      guard += 1; renderCompareCards();
      setMessage(`Running three isolated arms… ${Math.min(100, Math.round((guard * 4) / 100 * 100))}%`, false, "#compare-message");
    }
    renderCompareCards();
    setMessage("Illustrative episode complete. Read the values with the single-episode caveat below.", false, "#compare-message");
  } catch (error) {
    setMessage(error.message, true, "#compare-message");
  } finally { setBusy(false); }
}

function renderCompareCards() {
  const policies = ["greedy", "no_asks", "random"];
  $$(".compare-card").forEach((card, index) => {
    const run = state.compareRuns[policies[index]];
    if (!run) return;
    const stateLabel = card.querySelector(".compare-state"); if (stateLabel) stateLabel.textContent = run.status === "complete" ? "complete" : `day ${run.day}`;
    const placeholder = card.querySelector(".compare-placeholder");
    if (placeholder) {
      placeholder.className = "compare-result";
      placeholder.replaceChildren(dom("strong", "", String(run.metrics.mutual_second_meeting_intention)), dom("span", "", `${Math.round(run.metrics.coverage * 100)}% coverage`));
    }
  });
}

async function exportRun() {
  if (!state.run) return;
  try {
    const payload = await api(`/api/v1/runs/${encodeURIComponent(state.run.run_id)}/export`);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob); const anchor = document.createElement("a");
    anchor.href = url; anchor.download = `sequential-matching-${state.run.run_id}.json`; anchor.click(); URL.revokeObjectURL(url);
    toast("Public export downloaded.");
  } catch (error) { setMessage(error.message, true); }
}

async function resetRun() {
  state.operationToken += 1;
  if (!state.run) { stopPlay(); setBusy(false); showView("overview"); return; }
  const runId = state.run.run_id;
  stopPlay(); setBusy(true);
  try { await api(`/api/v1/runs/${encodeURIComponent(runId)}`, { method: "DELETE" }); } catch (_) { /* expired runs can still be replaced */ }
  state.run = null; state.events = []; state.eventsCursor = 0; state.selectedMemberId = null; showView("overview"); setBusy(false);
}

async function init() {
  try {
    state.config = await api("/api/v1/config");
  } catch (error) {
    toast(error.message);
    setMessage(error.message, true);
  }
  $("#start-demo").addEventListener("click", () => startRun());
  $("#next-phase").addEventListener("click", () => advance(1));
  $("#next-day").addEventListener("click", nextDay);
  $("#play-button").addEventListener("click", togglePlay);
  $("#finish-button").addEventListener("click", finishEpisode);
  $("#reset-button").addEventListener("click", resetRun);
  $("#export-button").addEventListener("click", exportRun);
  $("#start-compare").addEventListener("click", startComparison);
  $("#member-search").addEventListener("input", renderMembers);
  $$(".filter-button").forEach((button) => button.addEventListener("click", () => { state.memberFilter = button.dataset.filter; $$(".filter-button").forEach((item) => item.classList.toggle("is-active", item === button)); renderMembers(); }));
  $$("[data-nav]").forEach((button) => button.addEventListener("click", () => showView(button.dataset.nav)));
  document.addEventListener("visibilitychange", () => { if (document.hidden) stopPlay(); });
}

init();
