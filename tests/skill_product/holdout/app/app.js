const $ = selector => document.querySelector(selector);
let step = "welcome";
let draft = {name: "", branch: ""};

function context() { return {route: location.pathname, role: document.body.dataset.permission || "editor", viewport_class: viewportClass(), surface: step}; }
function show(next) {
  document.querySelectorAll("main section").forEach(section => { section.hidden = section.id !== next; });
  const before = step;
  step = next;
  const route = next === "welcome" ? "/welcome" : next === "complete" ? "/complete" : "/onboarding";
  history.pushState({}, "", route);
  receipt({...context(), event_type: "transition", before_state: before, after_state: next, behavior: "step-change", outcome: "shown"});
}
async function api(path, body = {}) {
  const response = await fetch(path, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
  const result = await response.json();
  receipt({...context(), event_type: "transition", before_state: "request", after_state: `status-${response.status}`, behavior: path.replace("/api/", ""), outcome: result.error || (result.ok ? "ok" : "completed")});
  return {status: response.status, body: result};
}
function updateReview() { $("#review-name").textContent = draft.name; $("#review-path").textContent = draft.branch; }

$("#start").addEventListener("click", () => show("identity"));
$("#identity-next").addEventListener("click", () => {
  const name = $("#workspace-name").value.trim();
  if (!name) { $("#name-status").textContent = "Workspace name is required"; return; }
  draft.name = name; $("#name-status").textContent = ""; show("branch");
});
$("#branch-next").addEventListener("click", async () => {
  const selected = $("input[name='path']:checked");
  if (!selected) { $("#path-status").textContent = "Choose a setup path"; return; }
  draft.branch = selected.value; $("#path-status").textContent = "";
  await api("/api/draft", draft); updateReview(); show("review");
});
document.querySelectorAll(".back").forEach(button => button.addEventListener("click", () => show(step === "review" ? "branch" : "identity")));
document.querySelectorAll(".cancel").forEach(button => button.addEventListener("click", () => { draft = {name: "", branch: ""}; $("#workspace-name").value = ""; show("welcome"); }));
$("#revoke").addEventListener("click", async () => { await api("/api/revoke"); document.body.dataset.permission = "viewer"; $("#permission").textContent = "Viewer access"; });
$("#expire").addEventListener("click", async () => { await api("/api/expire"); location.reload(); });
$("#submit").addEventListener("click", async () => {
  $("#submit-status").textContent = "Creating workspace…";
  const result = await api("/api/submit");
  $("#submit-status").textContent = result.status === 201 ? "Workspace created" : "Submitted successfully";
  if (result.status === 201) show("complete");
});
document.addEventListener("keydown", event => {
  if (event.ctrlKey && event.key === "Enter") {
    event.preventDefault();
    receipt({...context(), event_type: "activation", control: {identity: "Continue", type: "keyboard"}, input_mechanism: "keyboard", behavior: "ctrl-enter"});
    if (step === "identity") $("#identity-next").click(); else if (step === "branch") $("#branch-next").click(); else if (step === "review") $("#submit").click();
  }
});
receipt({...context(), event_type: "route_visit", state: "loaded"});
if (sessionStorage.getItem("waypoint-visited")) receipt({...context(), event_type: "reload_reentry", before_state: "prior-session", after_state: step, outcome: "flow-restarted"});
sessionStorage.setItem("waypoint-visited", "yes");
