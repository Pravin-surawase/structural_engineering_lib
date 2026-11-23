(() => {
  "use strict";

  const allowedExtensions = new Set(["csv", "xlsx", "json", "e2k", "edb"]);
  const selectedFiles = new Map();
  let generation = 0;
  let canReview = false;
  let report = null;

  const byId = (id) => document.getElementById(id);
  const elements = {
    input: byId("file-input"),
    dropZone: byId("drop-zone"),
    choose: byId("choose-button"),
    sample: byId("sample-button"),
    files: byId("file-list"),
    preview: byId("preview-button"),
    checks: byId("run-checks-button"),
    download: byId("review-button"),
    status: byId("status-panel"),
    previewPanel: byId("preview-panel"),
    reviewPanel: byId("review-panel"),
    tables: byId("tables"),
    previewSummary: byId("preview-summary"),
    reviewSummary: byId("review-summary"),
    reviewRows: byId("review-rows"),
    edbGuidance: byId("edb-guidance"),
    edbName: byId("edb-name"),
    itemTemplate: byId("file-item-template"),
  };

  function text(tag, value, className = "") {
    const node = document.createElement(tag);
    node.textContent = value;
    if (className) node.className = className;
    return node;
  }

  function extension(name) {
    return name.includes(".") ? name.split(".").pop().toLowerCase() : "";
  }

  function isModel(file) {
    return extension(file.name) === "edb";
  }

  function status(message, kind = "") {
    elements.status.hidden = !message;
    elements.status.className = `status-panel ${kind}`;
    elements.status.textContent = message;
  }

  function resetResults() {
    canReview = false;
    report = null;
    elements.checks.disabled = true;
    elements.download.disabled = true;
    elements.previewPanel.hidden = true;
    elements.reviewPanel.hidden = true;
  }

  function renderFiles() {
    elements.files.replaceChildren();
    const files = [...selectedFiles.values()];
    if (!files.length)
      elements.files.append(text("li", "No files selected.", "empty-state"));
    for (const [key, file] of selectedFiles) {
      const item =
        elements.itemTemplate.content.firstElementChild.cloneNode(true);
      item.querySelector(".file-name").textContent = file.name;
      item.querySelector(".file-meta").textContent = isModel(file)
        ? "ETABS model name only"
        : `${Math.max(1, Math.ceil(file.size / 1024))} KB`;
      const remove = item.querySelector(".remove-file");
      remove.setAttribute("aria-label", `Remove ${file.name}`);
      remove.addEventListener("click", () => {
        generation += 1;
        selectedFiles.delete(key);
        resetResults();
        status("");
        renderFiles();
        elements.choose.focus();
      });
      elements.files.append(item);
    }
    const model = files.find(isModel);
    elements.edbGuidance.hidden = !model;
    elements.edbName.textContent = model?.name || "";
    elements.preview.disabled = !files.some((file) => !isModel(file));
  }

  function addFiles(files) {
    if (!files.length) return;
    generation += 1;
    resetResults();
    const errors = [];
    for (const file of files) {
      if (!allowedExtensions.has(extension(file.name))) {
        errors.push(`${file.name} is outside the supported file types.`);
        continue;
      }
      const key = isModel(file) ? "selected-edb" : file.name.toLowerCase();
      const count = [...selectedFiles.values()].filter(
        (item) => !isModel(item),
      ).length;
      if (
        !isModel(file) &&
        (file.size > 2000000 || (count >= 8 && !selectedFiles.has(key)))
      ) {
        errors.push(
          `${file.name} exceeds the demo limit of eight exports at 2 MB each.`,
        );
        continue;
      }
      // Preserve only the name for a native model. Its File never enters the request.
      selectedFiles.set(key, isModel(file) ? { name: file.name } : file);
    }
    status(errors.join(" "), errors.length ? "error" : "");
    renderFiles();
  }

  elements.choose.addEventListener("click", () => elements.input.click());
  elements.input.addEventListener("change", () => {
    addFiles(elements.input.files);
    elements.input.value = "";
  });
  for (const type of ["dragenter", "dragover"]) {
    elements.dropZone.addEventListener(type, (event) => {
      event.preventDefault();
      elements.dropZone.classList.add("drag-over");
    });
  }
  for (const type of ["dragleave", "drop"]) {
    elements.dropZone.addEventListener(type, (event) => {
      event.preventDefault();
      elements.dropZone.classList.remove("drag-over");
    });
  }
  elements.dropZone.addEventListener("drop", (event) =>
    addFiles(event.dataTransfer.files),
  );

  async function encodeFile(file) {
    const bytes = new Uint8Array(await file.arrayBuffer());
    let binary = "";
    for (const byte of bytes) binary += String.fromCharCode(byte);
    return { name: file.name, data: btoa(binary) };
  }

  async function request(mode) {
    if (mode === "review" && !canReview) return;
    const requestGeneration = ++generation;
    resetResults();
    status(
      mode === "sample" ? "Opening the sample floor…" : "Reading local files…",
    );
    try {
      let response;
      if (mode === "sample") {
        response = await fetch("/api/sample");
      } else {
        const files = await Promise.all(
          [...selectedFiles.values()]
            .filter((file) => !isModel(file))
            .map(encodeFile),
        );
        if (requestGeneration !== generation) return;
        response = await fetch("/api/intake", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ files, mode }),
        });
      }
      const payload = await response.json();
      if (requestGeneration !== generation) return;
      if (!response.ok || payload.kind === "error") {
        throw new Error(payload.message || "Unable to read the local intake.");
      }
      if (payload.kind === "tables") renderTables(payload);
      else if (payload.kind === "review")
        renderReview(payload.result, Boolean(payload.sample));
      else throw new Error("The demo received an unknown intake response.");
    } catch (error) {
      if (requestGeneration === generation) status(error.message, "error");
    }
  }

  function renderTables(payload) {
    elements.previewPanel.hidden = false;
    elements.tables.replaceChildren();
    elements.previewSummary.textContent = `${payload.tables.length} source table(s)`;
    for (const table of payload.tables) {
      const card = document.createElement("article");
      card.className = "table-card";
      const shown = table.rows.slice(0, 30);
      const caption = table.worksheet
        ? `${table.file} · ${table.worksheet}`
        : table.file;
      card.append(text("h3", table.title || caption));
      card.append(
        text(
          "p",
          `${caption} · ${shown.length} shown · ${table.row_count} source records`,
        ),
      );
      const grid = document.createElement("table");
      const head = grid.createTHead().insertRow();
      head.append(text("th", "Row"));
      for (const column of table.headers)
        head.append(text("th", column || "—"));
      const body = grid.createTBody();
      for (const [index, values] of shown.entries()) {
        const row = body.insertRow();
        row.append(
          text(
            "td",
            table.first_row_number === null
              ? "—"
              : table.first_row_number + index,
          ),
        );
        for (const value of values) row.append(text("td", value));
      }
      const scroll = document.createElement("div");
      scroll.className = "table-scroll";
      scroll.append(grid);
      card.append(scroll);
      elements.tables.append(card);
    }
    const issues = payload.issues.map((issue) => issue.message).join(" ");
    status(
      `Intake preview only. Add the matching manifest to run ETABS checks. ${issues}`.trim(),
      "warning",
    );
  }

  function governingDetail(member) {
    const values = Object.values(member.evaluation?.governing || {});
    const controlling = values
      .filter((item) => item && Number.isFinite(item.utilization))
      .sort((left, right) => right.utilization - left.utilization)[0];
    if (controlling) return controlling;
    return member.evaluation?.governing || {};
  }

  function showMember(member) {
    const row = elements.reviewRows.insertRow();
    const evaluation = member.evaluation || {};
    const state = evaluation.engineering_status || "NOT_EVALUATED";
    const governing = governingDetail(member);
    const sourceId = governing.source_row_id || "";
    const match = /^(beam|column):[0-9a-f]{64}:(\d+)$/.exec(sourceId);
    const source = match
      ? `${match[1] === "beam" ? "Beam" : "Column"} table · row ${match[2]}`
      : sourceId || governing.source_row_number || "—";
    const sourceCell = text("td", source);
    if (sourceId) sourceCell.title = sourceId;
    const geometry = member.geometry || {};
    const section = geometry.section || {};
    const width = geometry.b_mm ?? section.width_mm;
    const depth = geometry.D_mm ?? section.depth_mm;
    const identity = text("td", member.member_id);
    if (width && depth)
      identity.append(text("small", `${width} × ${depth} mm`, "member-note"));
    const action = member.signed_actions?.[0];
    if (action?.mu_knm !== undefined) {
      identity.append(
        text(
          "small",
          `M ${action.mu_knm} kN·m · V ${action.vu_kn} kN`,
          "member-note",
        ),
      );
    }
    const statusCell = text(
      "td",
      state.replaceAll("_", " "),
      `status-${state.toLowerCase().replaceAll("_", "-")}`,
    );
    if (evaluation.reason) statusCell.title = evaluation.reason;
    row.append(
      identity,
      statusCell,
      sourceCell,
      text("td", governing.combination ?? "—"),
      text("td", governing.station_mm ?? "—"),
    );
  }

  function renderReview(result, sample) {
    elements.reviewPanel.hidden = false;
    elements.reviewSummary.replaceChildren();
    elements.reviewRows.replaceChildren();
    const counts = result.summary.engineering_statuses;
    const stats = [
      ["Members", result.members.length],
      ["Passed", counts.PASS || 0],
      ["Failed", counts.FAIL || 0],
      ["Not evaluated", counts.NOT_EVALUATED || 0],
    ];
    for (const [label, count] of stats) {
      const card = document.createElement("div");
      card.className = "summary-card";
      card.append(text("strong", count), text("span", label));
      elements.reviewSummary.append(card);
    }
    result.members.forEach(showMember);

    if (result.intake_status !== "ACCEPTED") {
      const issues = result.issues.map((issue) => issue.message).join(" ");
      status(
        `Intake ${result.intake_status.toLowerCase()}. ${issues}`,
        "error",
      );
      return;
    }
    const checkProfile =
      result.profile.startsWith("prepared-") ||
      result.profile === "etabs-paired";
    canReview = checkProfile && result.mode === "preview";
    elements.checks.disabled = !canReview;
    if (checkProfile && result.mode === "review") {
      report = result;
      elements.download.disabled = false;
      const details = result.members.flatMap(
        (member) => member.evaluation?.issues || [],
      );
      const message = details.map((issue) => issue.message).join(" ");
      status(
        sample
          ? "Synthetic sample checked."
          : `Review package ready. ${message}`.trim(),
      );
    } else {
      status(
        canReview
          ? "Preview ready. Run checks when the inputs match."
          : "Snapshot preview only. The exported snapshot does not evaluate member checks.",
      );
    }
  }

  elements.preview.addEventListener("click", () => request("preview"));
  elements.checks.addEventListener("click", () => request("review"));
  elements.sample.addEventListener("click", () => request("sample"));
  elements.download.addEventListener("click", () => {
    if (!report) return;
    const data = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json",
    });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(data);
    link.download = "floor-review.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  });
})();
