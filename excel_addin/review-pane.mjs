import { projectCalculationReview, REVIEW_LIMITS } from "./review-core.mjs";
import { writeCalculationReview, verifyCalculationReview, readCalculationReviewComments, officeErrorDetail } from "./taskpane-office.mjs";

export function initializeCalculationReviewPane(officeApi, excelApi, documentApi = document) {
  const file = documentApi.getElementById("w3-review-file");
  const preview = documentApi.getElementById("w3-review-preview");
  const publish = documentApi.getElementById("w3-review-publish");
  const verify = documentApi.getElementById("w3-review-verify");
  const comments = documentApi.getElementById("w3-review-comments");
  const status = documentApi.getElementById("w3-review-status");
  let projection = null;
  let revision = 0;
  let busy = false;
  function buttons(value) {
    busy = value;
    preview.disabled = value;
    file.disabled = value;
    publish.disabled = value || !projection;
    verify.disabled = value || !projection;
    comments.disabled = value;
  }
  file.addEventListener("change", () => { revision += 1; projection = null; buttons(busy); status.textContent = "Verify the selected saved dossier before publication."; });
  preview.addEventListener("click", async () => {
    projection = null;
    const current = revision;
    buttons(true);
    try {
      if (!officeApi.context.requirements.isSetSupported("ExcelApi", "1.16")) throw new Error("ExcelApi 1.16 typed literal cells are required.");
      const selected = file.files?.[0];
      if (!selected || selected.size > REVIEW_LIMITS.bytes * 3) throw new Error("Select one bounded exported W3 review transport JSON.");
      const checked = await projectCalculationReview(JSON.parse(await selected.text()));
      if (current !== revision) throw new Error("The selected input changed during verification.");
      projection = checked;
      status.textContent = `VERIFIED SAVED EVIDENCE · revision ${checked.revision} · ${checked.projectedRows} rows · dossier ${checked.dossierSha256}. No current ETABS state or professional approval is inferred.`;
    } catch (error) { status.textContent = `BLOCKED · ${officeErrorDetail(error)}`; }
    finally { buttons(false); }
  });
  async function act(operation) {
    buttons(true);
    try {
      if (!projection) throw new Error("Verify a saved review transport first.");
      const result = await operation(excelApi, projection);
      status.textContent = `COMMITTED / RECONCILED · ${JSON.stringify(result)} · Review comments are not professional approval.`;
    } catch (error) { status.textContent = `BLOCKED · ${officeErrorDetail(error)}`; }
    finally { buttons(false); }
  }
  publish.addEventListener("click", () => act(writeCalculationReview));
  verify.addEventListener("click", () => act(verifyCalculationReview));
  comments.addEventListener("click", async () => {
    buttons(true);
    try {
      const value = await readCalculationReviewComments(excelApi);
      const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: "application/json" }));
      const link = documentApi.createElement("a");
      link.href = url;
      link.download = "calculation-review-comments.json";
      link.click();
      URL.revokeObjectURL(url);
      status.textContent = "Revision-bound user comments exported separately; no calculation bytes were changed.";
    } catch (error) { status.textContent = `BLOCKED · ${officeErrorDetail(error)}`; }
    finally { buttons(false); }
  });
  buttons(false);
}
