const $ = (selector) => document.querySelector(selector);
const show = (element, visible = true) => { if (element) element.hidden = !visible; };

function setValidation(input, status, message, invalid) {
  status.textContent = message;
  input.setAttribute("aria-invalid", String(invalid));
}

function clearValidation(input, status) {
  status.textContent = "";
  input.setAttribute("aria-invalid", "false");
}

async function api(path, body = {}) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  return {status: response.status, body: await response.json()};
}

async function loadState() {
  const response = await fetch("/api/state");
  const state = await response.json();
  const row = $("#project-row");
  if (row) row.querySelector("strong").textContent = state.project.name;
  $("#project-name").value = state.project.name;
  $("#editor-title").textContent = `Edit ${state.project.name}`;
  $("#project-state").textContent = `Project state: ${state.project.state}`;
  $("#archived-status").textContent = state.empty_archived_projects ? "No archived projects" : "Archived projects are available";
  $("#analytics-status").textContent = state.feature_flags.advanced_analytics ? "Advanced analytics is enabled for this workspace." : "Feature not enabled for this workspace. Ask a workspace owner to enable it.";
  $("#pending-invites").textContent = state.invites.length ? `Pending invites: ${state.invites.join(", ")}` : "No pending invites";
  const list = $("#project-list");
  list.replaceChildren();
  for (const name of state.projects) {
    const button = document.createElement("button");
    button.textContent = `Edit ${name}`;
    button.addEventListener("click", async () => {
      await api("/api/select", {name});
      await loadState();
      $("#project-name")?.focus();
    });
    list.append(button);
  }
}

function closePalette() {
  const wasOpen = !$("#palette")?.hidden;
  show($("#palette"), false);
  $("#palette-button")?.setAttribute("aria-expanded", "false");
  if (wasOpen) $("#palette-button")?.focus();
}

function openPalette() {
  show($("#palette"), true);
  $("#palette-button")?.setAttribute("aria-expanded", "true");
  $("#palette")?.querySelector("a")?.focus();
}

function closeAvatarMenu() {
  const wasOpen = !$("#avatar-menu")?.hidden;
  show($("#avatar-menu"), false);
  $("#avatar")?.setAttribute("aria-expanded", "false");
  if (wasOpen) $("#avatar")?.focus();
}

function toggleAvatarMenu() {
  const opening = $("#avatar-menu")?.hidden;
  show($("#avatar-menu"), opening);
  $("#avatar")?.setAttribute("aria-expanded", String(Boolean(opening)));
  if (opening) $("#avatar-menu")?.querySelector("a")?.focus();
}

function openInviteDialog() {
  $("#invite-dialog")?.showModal();
  $("#invite-email")?.focus();
}

function closeInviteDialog() {
  $("#invite-dialog")?.close();
  $("#invite")?.focus();
}

function closeProjectForm() {
  if ($("#project-form")?.hidden) return;
  show($("#project-form"), false);
  $("#create-first")?.focus();
}

function closeContextMenu() {
  if ($("#context-menu")?.hidden) return;
  show($("#context-menu"), false);
  $("#project-row")?.focus();
}

function openContextMenu() {
  show($("#context-menu"), true);
  $("#duplicate")?.focus();
}

function applyRole(role) {
  localStorage.setItem("gauntlet-role", role);
  document.body.dataset.role = role;
  if (location.pathname === "/admin/data") show($("#admin"), true);
  show($("#admin-controls"), role === "admin");
  show($("#admin-permission"), role !== "admin");
  show($("#invite-permission"), role !== "admin");
  $("#invite").disabled = role !== "admin";
  $("#role-member").setAttribute("aria-pressed", String(role === "member"));
  $("#role-admin").setAttribute("aria-pressed", String(role === "admin"));
}

function route() {
  const path = location.pathname;
  document.querySelectorAll("main > section").forEach((section) => show(section, false));
  if (path === "/team") show($("#team"));
  else if (path === "/admin/data") show($("#admin"));
  else if (path === "/projects/import") show($("#import"));
  else if (path === "/projects") { show($("#projects")); show($("#editor")); }
  else if (path === "/settings/profile") show($("#profile"));
  else { show($("#dashboard")); show($("#analytics")); }
}

$("#avatar")?.addEventListener("click", toggleAvatarMenu);
$("#palette-button")?.addEventListener("click", () => $("#palette").hidden ? openPalette() : closePalette());
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    openPalette();
  } else if (event.key === "Escape") {
    closeAvatarMenu();
    closePalette();
    closeProjectForm();
    closeContextMenu();
  }
});
document.addEventListener("click", (event) => {
  if (!$("#palette").hidden && !$("#palette").contains(event.target) && event.target !== $("#palette-button")) closePalette();
});
$("#palette")?.addEventListener("keydown", (event) => {
  if (event.key === "Tab") {
    event.preventDefault();
    $("#palette")?.querySelector("a")?.focus();
  }
});
$("#project-row")?.addEventListener("contextmenu", (event) => {
  event.preventDefault();
  openContextMenu();
});
$("#project-actions")?.addEventListener("click", openContextMenu);
$("#project-row")?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || (event.shiftKey && event.key === "F10")) {
    event.preventDefault();
    openContextMenu();
  }
});
$("#context-menu")?.addEventListener("keydown", (event) => {
  if (event.key === "ArrowDown" || event.key === "Tab") {
    event.preventDefault();
    $("#duplicate")?.focus();
  } else if (event.key === "Escape") {
    event.preventDefault();
    closeContextMenu();
  }
});
$("#duplicate")?.addEventListener("click", async () => {
  const result = await api("/api/duplicate");
  $("#duplicate-status").textContent = result.status === 201 ? "Alpha copy added" : "Duplicate failed";
  await loadState();
  show($("#context-menu"), false);
});
$("#create-first")?.addEventListener("click", () => show($("#project-form"), true));
$("#cancel-create")?.addEventListener("click", closeProjectForm);
$("#new-name")?.addEventListener("input", () => clearValidation($("#new-name"), $("#form-error")));
$("#project-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = await api("/api/projects", {name: $("#new-name").value});
  setValidation($("#new-name"), $("#form-error"), result.status === 201 ? "Created" : "Name is required", result.status !== 201);
  if (result.status === 201) {
    await loadState();
    $("#new-name").value = "";
    show($("#project-form"), false);
    $("#create-first")?.focus();
  }
});
$("#save-real")?.addEventListener("click", async () => {
  const result = await api("/api/save-failure", {name: $("#project-name").value});
  $("#toast").textContent = result.body.ok ? "Saved successfully" : "Save failed";
});
$("#save-visual")?.addEventListener("click", () => { $("#toast").textContent = "Looks saved"; });
$("#publish")?.addEventListener("click", async () => {
  const result = await api("/api/publish", {name: $("#project-name").value});
  $("#toast").textContent = result.status === 200 ? "Published" : "Name is required before publishing";
  if (result.status === 200) await loadState();
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
$("#invite")?.addEventListener("click", openInviteDialog);
$("#invite-email")?.addEventListener("input", () => clearValidation($("#invite-email"), $("#invite-status")));
$("#send-invite")?.addEventListener("click", async () => {
  const result = await api("/api/invite", {email: $("#invite-email").value});
  setValidation($("#invite-email"), $("#invite-status"), result.status === 200 ? "Invitation queued" : "Valid email is required", result.status !== 200);
  if (result.status === 200) await loadState();
});
$("#close-invite")?.addEventListener("click", closeInviteDialog);
$("#invite-dialog")?.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    closeInviteDialog();
    return;
  }
  if (event.key !== "Tab") return;
  const controls = [...$("#invite-dialog").querySelectorAll("input, button")];
  const first = controls[0];
  const last = controls.at(-1);
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last?.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first?.focus();
  }
});
$("#role-member")?.addEventListener("click", () => applyRole("member"));
$("#role-admin")?.addEventListener("click", () => applyRole("admin"));
$("#export")?.addEventListener("click", async () => {
  const state = await (await fetch("/api/state")).json();
  const blob = new Blob([JSON.stringify(state)], {type: "application/json"});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "northstar-export.json";
  link.click();
  URL.revokeObjectURL(link.href);
});
$("#import-file")?.addEventListener("change", () => clearValidation($("#import-file"), $("#import-status")));
$("#clear-import")?.addEventListener("click", () => {
  $("#import-file").value = "";
  clearValidation($("#import-file"), $("#import-status"));
  $("#import-file")?.focus();
});
$("#start-import")?.addEventListener("click", async () => {
  const file = $("#import-file").files[0];
  if (!file) { setValidation($("#import-file"), $("#import-status"), "Choose a JSON export", true); return; }
  try {
    const value = JSON.parse(await file.text());
    if (!value.project || !Array.isArray(value.projects)) { setValidation($("#import-file"), $("#import-status"), "Invalid JSON export", true); return; }
    const result = await api("/api/import", value);
    setValidation($("#import-file"), $("#import-status"), result.status === 200 ? "Import completed" : "Import failed", result.status !== 200);
    if (result.status === 200) await loadState();
  } catch (_) {
    setValidation($("#import-file"), $("#import-status"), "Invalid JSON export", true);
  }
});
route();
applyRole(localStorage.getItem("gauntlet-role") || "member");
loadState();
