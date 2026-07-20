const $ = (selector) => document.querySelector(selector);
const show = (element, visible = true) => { if (element) element.hidden = !visible; };

async function api(path, body = {}) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  return {status: response.status, body: await response.json()};
}

function route() {
  const path = location.pathname;
  document.querySelectorAll("main > section").forEach((section) => show(section, false));
  if (path === "/team") show($("#team"));
  else if (path === "/admin/data") show($("#admin"));
  else if (path === "/projects/import") show($("#import"));
  else if (path === "/projects") { show($("#projects")); show($("#editor")); }
  else if (path === "/settings/profile") show($("#editor"));
  else { show($("#dashboard")); show($("#analytics")); }
}

$("#avatar")?.addEventListener("click", () => show($("#avatar-menu"), $("#avatar-menu").hidden));
$("#palette-button")?.addEventListener("click", () => show($("#palette"), true));
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    show($("#palette"), true);
  }
});
$("#project-row")?.addEventListener("contextmenu", (event) => {
  event.preventDefault();
  show($("#context-menu"), true);
});
$("#create-first")?.addEventListener("click", () => show($("#project-form"), true));
$("#project-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = await api("/api/projects", {name: $("#new-name").value});
  $("#form-error").textContent = result.status === 201 ? "Created" : "Name is required";
});
$("#save-real")?.addEventListener("click", async () => {
  const result = await api("/api/save-failure", {name: $("#project-name").value});
  $("#toast").textContent = result.body.ok ? "Saved successfully" : "Save failed";
});
$("#save-visual")?.addEventListener("click", () => { $("#toast").textContent = "Looks saved"; });
$("#publish")?.addEventListener("click", async () => {
  const result = await api("/api/publish");
  $("#toast").textContent = result.status === 200 ? "Published" : "Name is required before publishing";
});
$("#stale")?.addEventListener("click", async () => {
  await api("/api/stale");
  $("#toast").textContent = "Session expired";
  const retry = document.createElement("button");
  retry.textContent = "Reauthenticate";
  retry.addEventListener("click", async () => {
    await api("/api/reauthenticate");
    $("#toast").textContent = "Session restored";
    retry.remove();
  });
  $("#toast").after(retry);
});
$("#invite")?.addEventListener("click", () => $("#invite-dialog").showModal());
$("#close-invite")?.addEventListener("click", () => $("#invite-dialog").close());
$("#export")?.addEventListener("click", () => {
  const blob = new Blob([JSON.stringify({project: "Alpha"})], {type: "application/json"});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "northstar-export.json";
  link.click();
  URL.revokeObjectURL(link.href);
});
route();
