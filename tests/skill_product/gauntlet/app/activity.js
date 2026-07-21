let lastInputMechanism = "programmatic";

function viewportClass() {
  if (window.innerWidth < 768) return "mobile";
  if (window.innerWidth < 1100) return "tablet";
  return "desktop";
}

function controlDescriptor(element) {
  const identity = (element.getAttribute("aria-label") || element.textContent || element.id || element.name || element.tagName).trim().replace(/\s+/g, " ").slice(0, 160);
  const type = element.getAttribute("role") || element.getAttribute("type") || element.tagName.toLowerCase();
  return {identity, type};
}

function containingSurface(element) {
  const surface = element.closest("dialog, [role='dialog'], [role='menu'], form, main > section");
  return surface?.getAttribute("aria-label") || surface?.id || surface?.getAttribute("role") || "page";
}

function activity(event) {
  fetch("/api/activity", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(event),
    keepalive: true
  }).catch(() => {});
}

function context() {
  return {
    route: location.pathname,
    role: document.body.dataset.role || localStorage.getItem("gauntlet-role") || "member",
    viewport_class: viewportClass()
  };
}

document.addEventListener("pointerdown", (event) => {
  lastInputMechanism = "pointer";
  const control = event.target.closest("button, a, input, select, textarea, [role]");
  if (control?.matches(":disabled")) activity({...context(), event_type: "blocked", control: controlDescriptor(control), surface: containingSurface(control), reason: "disabled"});
}, true);
document.addEventListener("keydown", () => { lastInputMechanism = "keyboard"; }, true);
document.addEventListener("click", (event) => {
  const control = event.target.closest("button, a, input, select, textarea, [role='menuitem']");
  if (!control || control.matches(":disabled")) return;
  activity({...context(), event_type: "activation", control: controlDescriptor(control), input_mechanism: event.detail === 0 ? "keyboard" : lastInputMechanism, surface: containingSurface(control), behavior: control.id || control.getAttribute("href") || control.getAttribute("name") || control.tagName.toLowerCase()});
}, true);
document.addEventListener("input", (event) => {
  const control = event.target.closest("input, select, textarea");
  if (control) activity({...context(), event_type: "input", control: controlDescriptor(control), input_mechanism: lastInputMechanism, surface: containingSurface(control)});
}, true);
document.addEventListener("contextmenu", (event) => {
  const control = event.target.closest("button, article, [role]");
  if (control) activity({...context(), event_type: "activation", control: controlDescriptor(control), input_mechanism: "secondary-pointer", surface: containingSurface(control), behavior: "open-context-menu"});
}, true);
const safetySeen = new WeakSet();
function noteSafetyBoundary(event) {
  const control = event.target.closest("button.danger");
  if (!control || safetySeen.has(control)) return;
  safetySeen.add(control);
  activity({...context(), event_type: "avoided", control: controlDescriptor(control), surface: containingSurface(control), reason: "authorization-required"});
}
document.addEventListener("pointerover", noteSafetyBoundary, true);
document.addEventListener("focusin", noteSafetyBoundary, true);
