let inputMechanism = "programmatic";
function viewportClass() { return innerWidth < 700 ? "mobile" : innerWidth < 1050 ? "tablet" : "desktop"; }
function visibleSurface() { return [...document.querySelectorAll("main section")].find(section => !section.hidden)?.id || "page"; }
function receipt(event) {
  fetch("/api/activity", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(event), keepalive: true}).catch(() => {});
}
function base() { return {route: location.pathname, role: document.body.dataset.permission || "editor", viewport_class: viewportClass(), surface: visibleSurface()}; }
function descriptor(control) { return {identity: (control.getAttribute("aria-label") || control.textContent || control.value || control.name || control.tagName).trim().replace(/\s+/g, " ").slice(0, 160), type: control.type || control.getAttribute("role") || control.tagName.toLowerCase()}; }
document.addEventListener("pointerdown", () => { inputMechanism = "pointer"; }, true);
document.addEventListener("keydown", () => { inputMechanism = "keyboard"; }, true);
document.addEventListener("click", event => {
  const control = event.target.closest("button, input, a");
  if (control) receipt({...base(), event_type: "activation", control: descriptor(control), input_mechanism: event.detail === 0 ? "keyboard" : inputMechanism, behavior: control.id || control.className || control.name});
}, true);
document.addEventListener("input", event => {
  const control = event.target.closest("input, textarea, select");
  if (control) receipt({...base(), event_type: "input", control: descriptor(control), input_mechanism: inputMechanism, behavior: control.id || control.name});
}, true);
