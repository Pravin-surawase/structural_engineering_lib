/**
 * DesignView - Compact single beam design with live 3D preview.
 *
 * Responsive workbench: common inputs, 3D review, truthful results, and
 * contextual advanced actions.
 */
import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Calculator, CheckCircle, AlertCircle, Loader2, ChevronDown, ChevronRight, Shield, Lightbulb, Download, FileText, Ruler, RotateCcw, ArrowRight, Activity } from "lucide-react";
import { useExportBBS, useExportDXF, useExportReport } from "../../hooks/useExport";
import { useLoadAnalysis } from "../../hooks/useLoadAnalysis";
import type { LoadAnalysisRequest, LoadAnalysisResponse } from "../../api/client";
import type { BeamCrackWidthParams, BeamDesignResponse } from "../../api/client";
import { governingUtilization } from "../../api/client";
import { useDesignStore } from "../../store/designStore";
import { useLiveDesign } from "../../hooks/useLiveDesign";
import { useCodeChecks, useRebarSuggestions } from "../../hooks/useInsights";
import type { CheckDetail, SuggestionItem } from "../../hooks/useInsights";
import { ConnectionStatus } from "../ui/ConnectionStatus";
import { Viewport3D } from "../viewport/Viewport3D";
import { ParetoPanel } from "./ParetoPanel";
import { resolveComparisonDepthOffsetMm } from "./comparisonDepth";
import { formatPercent, formatRatio, formatSignedRatio, getTrustPresentation } from "../../utils/trustPresentation";
import { WorkbenchHeader } from "../workbench/WorkbenchHeader";
import { WorkbenchShell } from "../workbench/WorkbenchShell";
import { ResultLifecycleBadge } from "../workbench/ResultLifecycleBadge";
import { CatalogBeamInputPanel } from "../../features/catalog/CatalogBeamInputPanel";
import type { CatalogBeamTransportName } from "../../features/catalog/types";

/** Collapsible accordion section */
function AccordionSection({ title, children, defaultOpen = true }: { title: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="min-w-0 rounded-sm border border-ink/20 bg-white">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
        className="flex min-h-10 w-full items-center justify-between px-3.5 text-left text-sm font-semibold text-ink hover:bg-paper"
      >
        {title}
        {open ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
      </button>
      {open && <div className="px-3.5 pb-3.5 grid grid-cols-2 gap-2.5">{children}</div>}
    </div>
  );
}

export interface DesignViewProps {
  inputMode?: "manual" | "catalog";
}

export function DesignView({ inputMode = "manual" }: DesignViewProps) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { inputs, length } = useDesignStore();
  const [autoDesign, setAutoDesign] = useState(true);
  const [showResultDetails, setShowResultDetails] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showCompare, setShowCompare] = useState(false);
  const [loadCalcEnabled, setLoadCalcEnabled] = useState(false);
  const [loadCalcType, setLoadCalcType] = useState<'udl' | 'point'>('udl');
  const [loadCalcMagnitude, setLoadCalcMagnitude] = useState(20); // kN/m or kN
  const [loadCalcSupport, setLoadCalcSupport] = useState<'simply_supported' | 'cantilever'>('simply_supported');
  const [loadCalcPositionMm, setLoadCalcPositionMm] = useState(length / 2);
  const [loadCalculation, setLoadCalculation] = useState<{
    request: LoadAnalysisRequest;
    result: LoadAnalysisResponse;
  } | null>(null);
  const latestLoadRequest = useRef(0);

  const exportParams = {
    source: "quick-beam" as const,
    width: inputs.width,
    depth: inputs.depth,
    span_length: length,
    clear_cover: inputs.clear_cover ?? 40,
    fck: inputs.fck,
    fy: inputs.fy,
    moment: inputs.moment,
    shear: inputs.shear ?? 0,
    stirrup_dia_mm: inputs.stirrup_dia_mm ?? 8,
    main_bar_dia_mm: inputs.main_bar_dia_mm ?? 20,
    effective_depth: inputs.effective_depth,
  };
  const { mutate: exportBBS, isPending: bbsPending } = useExportBBS();
  const { mutate: exportDXF, isPending: dxfPending } = useExportDXF();
  const { mutate: exportReport, isPending: reportPending } = useExportReport();

  const { state, actions } = useLiveDesign({
    autoDesign,
    enabled: true,
  });
  const trust = state.result ? getTrustPresentation(state.result) : null;
  const canExport = Boolean(state.exportEligible && trust?.canExport);

  const codeChecks = useCodeChecks();
  const rebarSuggestions = useRebarSuggestions();
  const loadAnalysis = useLoadAnalysis();
  const combinedCase = (inputs.torsion ?? 0) > 0 || Boolean(inputs.include_serviceability);
  const comparisonDepthOffsetMm = resolveComparisonDepthOffsetMm({
    depthMm: inputs.depth,
    // A retained design result may belong to an older input revision. Only its
    // depth is safe to use when the lifecycle confirms it is current.
    effectiveDepthMm: state.resultLifecycle === "current"
      ? state.result?.effective_depth_used ?? inputs.effective_depth
      : inputs.effective_depth,
    clearCoverMm: inputs.clear_cover ?? 40,
    stirrupDiameterMm: inputs.stirrup_dia_mm ?? 8,
    mainBarDiameterMm: inputs.main_bar_dia_mm ?? 20,
  });
  const submittedLoadRequest = loadCalculation?.request;
  const submittedLoad = submittedLoadRequest?.loads[0];
  const loadAnalysisResult = loadCalculation?.result;
  const loadResultMatchesCurrentInputs = Boolean(
    submittedLoadRequest
      && submittedLoad
      && submittedLoadRequest.span_mm === length
      && submittedLoadRequest.support_condition === loadCalcSupport
      && submittedLoad.load_type === loadCalcType
      && submittedLoad.magnitude === loadCalcMagnitude
      && (loadCalcType !== 'point' || submittedLoad.position_mm === loadCalcPositionMm),
  );
  const minimumLoadMoment = loadAnalysisResult?.min_bm_knm;
  // Quick Beam admits only nonnegative sagging moment and has no tension-face
  // or station contract. Do not turn a hogging action into bottom tension steel.
  const cannotTransferLoadResult = minimumLoadMoment !== undefined && minimumLoadMoment < -1e-9;

  const spanMeters = Number((length / 1000).toFixed(2));
  const updateCatalogInput = (
    name: CatalogBeamTransportName,
    value: number | undefined,
  ) => {
    actions.updateInputs({ [name]: value });
  };
  const updateCrackWidthInput = (
    name: keyof BeamCrackWidthParams,
    value: string | number | undefined,
  ) => {
    actions.updateInputs({
      crack_width_params: {
        exposure_class: inputs.crack_width_params?.exposure_class ?? "moderate",
        ...inputs.crack_width_params,
        [name]: value,
      },
    });
  };

  // Auto-trigger code checks + rebar suggestions when design result changes
  useEffect(() => {
    if (!state.result || state.resultLifecycle !== "current") return;
    const r = state.result;
    if (!combinedCase) {
      codeChecks.mutate({
        beam: {
          b_mm: inputs.width,
          D_mm: inputs.depth,
          span_mm: length,
          fck_mpa: inputs.fck,
          fy_mpa: inputs.fy,
          mu_knm: inputs.moment,
          vu_kn: inputs.shear,
        },
        config: r.ast_total ? { ast_mm2: r.ast_total } : null,
      });
    }
    if (r.flexure?.ast_required) {
      rebarSuggestions.mutate({
        ast_required: r.flexure.ast_required,
        ast_provided: r.ast_total,
        b_mm: inputs.width,
        cover_mm: 40,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.result, state.resultLifecycle]);

  return (
    <div className="h-full pt-14">
      <WorkbenchShell
        header={(
          <WorkbenchHeader
            title="Quick beam design"
            projectName="Rectangular beam · IS 456:2000"
            primaryAction={(
              <button
                onClick={actions.triggerDesign}
                disabled={state.isDesigning}
                className="inline-flex min-h-10 items-center justify-center gap-2 rounded-sm bg-cobalt px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-cobalt-hover disabled:cursor-not-allowed disabled:opacity-50"
              >
                {state.isDesigning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calculator className="h-4 w-4" />}
                {state.isDesigning ? "Calculating…" : state.result ? "Recalculate" : "Design beam"}
              </button>
            )}
            secondaryActions={(
              <>
                <button
                  onClick={() => {
                    setShowCompare(!showCompare);
                    setShowResultDetails(true);
                  }}
                  disabled={!state.exportEligible || combinedCase}
                  title={combinedCase ? "Comparison automation does not carry torsion or serviceability inputs." : undefined}
                  aria-pressed={showCompare}
                  className="rounded-lg border border-white/10 px-3 py-2 text-xs text-zinc-300 hover:bg-white/5 disabled:opacity-40"
                >
                  Compare options
                </button>
                <button
                  onClick={actions.reset}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-2 text-xs text-zinc-300 hover:bg-white/5"
                >
                  <RotateCcw className="h-3.5 w-3.5" /> Reset
                </button>
              </>
            )}
          >
            <ResultLifecycleBadge lifecycle={state.resultLifecycle} />
            <ConnectionStatus
              status={state.connectionStatus}
              latency={state.latency}
              error={state.error}
              onReconnect={actions.reconnect}
              isFallbackActive={state.isFallbackActive}
            />
          </WorkbenchHeader>
        )}
      >
      {searchParams.get("recovery") === "result-required" ? (
        <div
          className="border-b border-amber-400/20 bg-amber-400/10 px-4 py-2 text-sm text-amber-100"
          role="status"
        >
          The saved result is missing or no longer matches these inputs. Review the values and run the design again.
        </div>
      ) : null}
      <div className="mx-auto grid min-w-0 max-w-7xl grid-cols-1 gap-5 p-4 sm:p-6 lg:grid-cols-[22rem_minmax(0,1fr)] lg:items-start">
      <section aria-labelledby="beam-inputs" className="min-w-0 rounded-sm border border-ink/20 bg-paper text-ink [--focus-color:var(--color-cobalt)] [color-scheme:light]">
        <div className="border-b border-ink/20 px-4 py-3">
          <h2 id="beam-inputs" className="text-base font-semibold text-ink">Beam inputs</h2>
        </div>

        <div className="space-y-3 p-4">
          <div className="flex items-center justify-between">
            <label className="flex min-h-9 items-center gap-2 text-sm text-ink/80">
              <input
                type="checkbox"
                checked={autoDesign}
                onChange={(e) => setAutoDesign(e.target.checked)}
                className="accent-blue-500 w-3.5 h-3.5"
              />
              Auto Design
            </label>
            {state.isDesigning && <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin" />}
          </div>

          {inputMode === "catalog" ? (
            <CatalogBeamInputPanel
              values={{
                width: inputs.width,
                depth: inputs.depth,
                effective_depth: inputs.effective_depth,
                clear_cover: inputs.clear_cover ?? 40,
                stirrup_dia_mm: inputs.stirrup_dia_mm ?? 8,
                main_bar_dia_mm: inputs.main_bar_dia_mm ?? 20,
                moment: inputs.moment,
                shear: inputs.shear ?? 0,
                fck: inputs.fck,
                fy: inputs.fy,
              }}
              onChange={updateCatalogInput}
              onUseManual={() => navigate("/workbench/quick/manual")}
            />
          ) : (
          <>
          <AccordionSection title="Dimensions">
            <InputField label="Width" value={inputs.width} onChange={(v) => actions.updateInputs({ width: v })} unit="mm" min={150} max={600} />
            <InputField label="Depth" value={inputs.depth} onChange={(v) => actions.updateInputs({ depth: v })} unit="mm" min={300} max={1200} />
            <InputField label="Span" value={spanMeters} onChange={(v) => actions.updateLength(v * 1000)} unit="m" min={1} max={15} step={0.5} />
            <InputField label="Cover" value={inputs.clear_cover ?? 40} onChange={(v) => actions.updateInputs({ clear_cover: v })} unit="mm" min={20} max={75} />
          </AccordionSection>

          <AccordionSection title="Materials">
            <DropdownField label="Concrete" value={inputs.fck} onChange={(v) => actions.updateInputs({ fck: v })} options={[20, 25, 30, 35, 40, 45, 50]} format={(v) => `M${v}`} />
            <DropdownField label="Steel" value={inputs.fy} onChange={(v) => actions.updateInputs({ fy: v })} options={[415, 500, 550]} format={(v) => `Fe${v}`} />
          </AccordionSection>

          <AccordionSection title="Design Forces">
            <InputField label="Moment (Mu)" value={inputs.moment} onChange={(v) => actions.updateInputs({ moment: v })} unit="kN·m" min={0} max={2000} />
            <InputField label="Shear (Vu)" value={inputs.shear ?? 0} onChange={(v) => actions.updateInputs({ shear: v })} unit="kN" min={0} max={1000} />

            {/* Load Calculator toggle */}
            <div className="col-span-2 flex items-center gap-2 px-1 pt-1">
              <label className="flex items-center gap-2 text-xs text-ink/80 cursor-pointer">
                <input
                  type="checkbox"
                  checked={loadCalcEnabled}
                  onChange={(e) => setLoadCalcEnabled(e.target.checked)}
                  className="accent-cyan-500 w-3.5 h-3.5"
                />
                <Activity className="w-3 h-3 text-cyan-400" />
                Load Calculator
              </label>
            </div>
            {loadCalcEnabled && (
              <>
                <DropdownField label="Support" value={loadCalcSupport} onChange={setLoadCalcSupport as (v: string | number) => void} options={['simply_supported', 'cantilever']} format={(v) => v === 'simply_supported' ? 'SS' : 'Cantilever'} />
                <DropdownField label="Load Type" value={loadCalcType} onChange={setLoadCalcType as (v: string | number) => void} options={['udl', 'point']} format={(v) => v === 'udl' ? 'UDL' : 'Point'} />
                <InputField label={loadCalcType === 'udl' ? 'w' : 'P'} value={loadCalcMagnitude} onChange={setLoadCalcMagnitude} unit={loadCalcType === 'udl' ? 'kN/m' : 'kN'} min={0.1} max={500} step={0.5} />
                {loadCalcType === 'point' && <InputField label="Load position" value={loadCalcPositionMm} onChange={setLoadCalcPositionMm} unit="mm" min={0} max={length} step={100} />}
                <div className="col-span-2 flex gap-2">
                  <button
                    onClick={() => {
                      const load = loadCalcType === 'udl'
                        ? { load_type: 'udl' as const, magnitude: loadCalcMagnitude }
                        : { load_type: 'point' as const, magnitude: loadCalcMagnitude, position_mm: loadCalcPositionMm };
                      const request: LoadAnalysisRequest = {
                        span_mm: length,
                        support_condition: loadCalcSupport,
                        loads: [load],
                        num_points: 51,
                      };
                      const requestNumber = latestLoadRequest.current + 1;
                      latestLoadRequest.current = requestNumber;
                      // Bind a result to the exact inputs submitted. An older network
                      // response must never become transferable after a later request.
                      loadAnalysis.mutate(request, {
                        onSuccess: (result) => {
                          if (latestLoadRequest.current === requestNumber) {
                            setLoadCalculation({ request, result });
                          }
                        },
                      });
                    }}
                    disabled={loadAnalysis.isPending}
                    className="flex-1 py-1.5 rounded-lg bg-cyan-600/20 border border-cyan-500/30 text-xs text-cobalt hover:bg-cobalt/15 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-40"
                  >
                    {loadAnalysis.isPending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Activity className="w-3 h-3" />}
                    Compute
                  </button>
                  {loadAnalysisResult && (
                    <button
                      onClick={() => {
                        const d = loadAnalysisResult;
                        const vuAbs = Math.max(Math.abs(d.max_sf_kn), Math.abs(d.min_sf_kn));
                        actions.updateInputs({ moment: d.max_bm_knm, shear: vuAbs });
                      }}
                      disabled={loadAnalysis.isPending || !loadResultMatchesCurrentInputs || cannotTransferLoadResult}
                      title={cannotTransferLoadResult ? "Quick Beam cannot represent hogging moment, tension face, or governing station. Keep the signed diagram and use a checked member workflow." : !loadResultMatchesCurrentInputs ? "Recompute after changing the load calculator inputs." : undefined}
                      className="flex-1 py-1.5 rounded-lg bg-emerald-600/20 border border-emerald-500/30 text-xs text-emerald-900 hover:bg-emerald-500/20 disabled:opacity-50 transition-colors flex items-center justify-center gap-1.5"
                    >
                      Use Values <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
                {loadAnalysis.error && (
                  <p className="col-span-2 text-xs text-rose-800" role="alert">
                    Load calculation failed. Check the current inputs and try again.
                  </p>
                )}
                {cannotTransferLoadResult && (
                  <p className="col-span-2 text-xs leading-4 text-amber-900" role="status">
                    Transfer held. The diagram includes {minimumLoadMoment.toFixed(1)} kN·m of hogging. Quick Beam cannot preserve its tension face or station.
                  </p>
                )}
                {loadAnalysisResult && !loadResultMatchesCurrentInputs && (
                  <p className="col-span-2 text-xs leading-4 text-amber-900" role="status">
                    Load inputs changed after this diagram was calculated. Recompute before using its values.
                  </p>
                )}
                {loadAnalysisResult && <MiniDiagram data={loadAnalysisResult} />}
              </>
            )}
            <InputField label="Torsion (Tu)" value={inputs.torsion ?? 0} onChange={(v) => actions.updateInputs({ torsion: v })} unit="kN·m" min={0} max={200} step={0.5} />
          </AccordionSection>

          <AccordionSection title="Serviceability" defaultOpen={false}>
            <label className="col-span-2 flex items-center gap-2 text-xs text-ink/80 cursor-pointer">
              <input
                type="checkbox"
                checked={inputs.include_serviceability ?? false}
                onChange={(e) => actions.updateInputs({ include_serviceability: e.target.checked })}
                className="accent-blue-500 w-3.5 h-3.5"
              />
              Include maintained Level-A deflection and crack-width checks
            </label>
            {inputs.include_serviceability && (
              <>
                <OptionalInputField label="Check span" value={inputs.span_mm} onChange={(v) => actions.updateInputs({ span_mm: v })} unit="mm" min={1} />
                <DropdownField label="Check support" value={inputs.support_condition ?? "simply_supported"} onChange={(v) => actions.updateInputs({ support_condition: v })} options={["simply_supported", "continuous", "cantilever"]} format={(v) => v.replaceAll("_", " ")} />
                <DropdownField label="Exposure" value={inputs.crack_width_params?.exposure_class ?? "moderate"} onChange={(v) => updateCrackWidthInput("exposure_class", v)} options={["mild", "moderate", "severe", "very_severe"]} format={(v) => v.replaceAll("_", " ")} />
                <OptionalInputField label="acr" value={inputs.crack_width_params?.acr_mm} onChange={(v) => updateCrackWidthInput("acr_mm", v)} unit="mm" min={0.1} />
                <OptionalInputField label="cmin" value={inputs.crack_width_params?.cmin_mm} onChange={(v) => updateCrackWidthInput("cmin_mm", v)} unit="mm" min={0.1} />
                <OptionalInputField label="h" value={inputs.crack_width_params?.h_mm} onChange={(v) => updateCrackWidthInput("h_mm", v)} unit="mm" min={0.1} />
                <OptionalInputField label="x" value={inputs.crack_width_params?.x_mm} onChange={(v) => updateCrackWidthInput("x_mm", v)} unit="mm" min={0.1} />
                <OptionalInputField label="fs,service" value={inputs.crack_width_params?.fs_service_nmm2} onChange={(v) => updateCrackWidthInput("fs_service_nmm2", v)} unit="N/mm²" min={0} />
                <p className="col-span-2 text-xs leading-4 text-ink/75">Span, crack geometry, and service stress are required explicitly. Empty values are not inferred from the 3D span or reinforcement.</p>
              </>
            )}
          </AccordionSection>
          </>
          )}
        </div>

        {state.isFallbackActive ? <p className="px-4 pb-4 text-xs text-ink/75">{state.transportExplanation}</p> : null}
      </section>

      <div className="min-w-0 space-y-5">
        <section aria-labelledby="beam-result" className="rounded-md border border-zinc-700 bg-zinc-900">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-700 px-4 py-3">
            <h2 id="beam-result" className="text-base font-semibold text-white">Beam result</h2>
            {state.result ? (
              <div className="relative">
                <button
                  type="button"
                  onClick={() => canExport && setShowExportMenu(!showExportMenu)}
                  disabled={!canExport}
                  aria-expanded={canExport && showExportMenu}
                  title={canExport ? "Export current passing design" : "Exports require a current-revision PASS result"}
                  className="flex min-h-9 items-center gap-1.5 rounded-sm border border-zinc-700 bg-zinc-950 px-3 text-sm text-zinc-200 hover:border-blue-300 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <Download className="w-3.5 h-3.5" />
                  Export
                  <ChevronDown className="w-3 h-3" />
                </button>
                {showExportMenu && canExport && (
                  <div className="absolute right-0 z-10 mt-1.5 w-48 rounded-md border border-zinc-700 bg-zinc-950 shadow-xl">
                    {[
                      { label: "Checked BBS (CSV)", blocked: combinedCase, icon: <Download className="w-3.5 h-3.5" />, loading: bbsPending, onClick: () => { exportBBS(exportParams); setShowExportMenu(false); } },
                      { label: "Checked DXF Drawing", blocked: combinedCase, icon: <Ruler className="w-3.5 h-3.5" />, loading: dxfPending, onClick: () => { exportDXF(exportParams); setShowExportMenu(false); } },
                      ...(["html", "json", "pdf"] as const).map((format) => ({
                        label: format === "pdf" ? "Calculation PDF" : `${format.toUpperCase()} Report`,
                        blocked: combinedCase && format === "pdf",
                        icon: <FileText className="w-3.5 h-3.5" />,
                        loading: reportPending,
                        onClick: () => {
                          if (!combinedCase && format !== "pdf") {
                            exportReport({ ...exportParams, format });
                            setShowExportMenu(false);
                            return;
                          }
                          exportReport({
                            width: inputs.width,
                            depth: inputs.depth,
                            fck: inputs.fck,
                            fy: inputs.fy,
                            moment: inputs.moment,
                            shear: inputs.shear ?? 0,
                            torsion: inputs.torsion ?? 0,
                            include_serviceability: inputs.include_serviceability ?? false,
                            ast_required: state.result?.flexure?.ast_required,
                            ast_provided: state.result?.ast_total,
                            utilization: state.result ? governingUtilization(state.result) ?? undefined : undefined,
                            is_safe: state.result?.success,
                            effective_depth: state.result?.effective_depth_used,
                            clear_cover: inputs.clear_cover,
                            stirrup_dia_mm: inputs.stirrup_dia_mm,
                            main_bar_dia_mm: inputs.main_bar_dia_mm,
                            span_mm: inputs.span_mm,
                            support_condition: inputs.support_condition,
                            crack_width_params: inputs.crack_width_params,
                            calculation_identity: trust!.calculationIdentity!,
                            format,
                          });
                          setShowExportMenu(false);
                        },
                      })),
                    ].map((item) => (
                      <button key={item.label} onClick={item.onClick} disabled={item.loading || !canExport || item.blocked}
                        title={item.blocked ? "This format cannot represent the checked governing layout." : undefined}
                        className="w-full flex items-center gap-2.5 px-3.5 py-2.5 text-xs text-white/60 hover:bg-white/5 hover:text-white/90 transition-colors disabled:opacity-40">
                        {item.loading ? <div className="w-3.5 h-3.5 rounded-full border border-white/30 border-t-white/70 animate-spin" /> : item.icon}
                        {item.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : null}
          </div>

          <div className="space-y-3 p-4">
            {state.error ? <p role="alert" className="rounded-sm border border-rose-400/40 bg-rose-400/10 p-3 text-sm text-rose-100">{state.error}</p> : null}
            {state.result && trust ? (
              <>
                {state.resultLifecycle !== "current" ? <p className="text-sm text-amber-200">Previous calculation. Recalculate to review the current inputs.</p> : null}
                <BeamResultSummary result={state.result} trust={trust} />
                {!canExport ? <p className="text-xs text-zinc-300">Export requires a current, supported passing result.</p> : null}
                {combinedCase ? <p className="text-xs text-zinc-300">Combined actions and serviceability results use the HTML or JSON report.</p> : null}
                <button type="button" aria-expanded={showResultDetails} onClick={() => setShowResultDetails(!showResultDetails)} className="flex min-h-9 items-center gap-2 rounded-sm text-sm font-semibold text-blue-200 hover:text-white">
                  {showResultDetails ? "Hide checks and evidence" : "Show checks and evidence"}
                  <ChevronDown size={16} className={showResultDetails ? "rotate-180" : undefined} aria-hidden="true" />
                </button>
                {showResultDetails ? (
                  <div className="space-y-3">
                    <BeamResultDetails result={state.result} trust={trust} />
                    {!combinedCase && <CodeChecksPanel data={codeChecks.data} isPending={codeChecks.isPending} />}
                    <RebarSuggestionsPanel data={rebarSuggestions.data} isPending={rebarSuggestions.isPending} />
                    {showCompare && !combinedCase ? <ParetoPanel spanMm={length} muKnm={inputs.moment} vuKn={inputs.shear ?? 0} effectiveDepthOffsetMm={comparisonDepthOffsetMm} /> : null}
                  </div>
                ) : null}
              </>
            ) : state.error ? null : (
              <p role="status" className="text-sm text-zinc-300">{state.isDesigning ? "Calculating…" : "Run a design to review the governing check and available exports."}</p>
            )}
          </div>
        </section>

        <section aria-labelledby="beam-preview" className="min-w-0 overflow-hidden rounded-md border border-zinc-700 bg-zinc-900">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-700 px-4 py-3">
            <h2 id="beam-preview" className="text-base font-semibold text-white">3D view</h2>
            {!state.result && !state.isDesigning ? (
              <button
                type="button"
                onClick={() => {
                  actions.updateInputs({ width: 300, depth: 500, fck: 25, fy: 500, moment: 120, shear: 75 });
                  actions.updateLength(5000);
                }}
                className="min-h-9 rounded-sm border border-zinc-700 px-3 text-xs font-semibold text-blue-200 hover:border-blue-300"
              >
                Load beam example
              </button>
            ) : null}
          </div>
          <div className="relative h-72 sm:h-96">
            <Viewport3D mode="design" forceMode />
          </div>
        </section>
      </div>
      </div>
      </WorkbenchShell>
    </div>
  );
}

type BeamTrust = ReturnType<typeof getTrustPresentation>;

function BeamResultSummary({ result, trust }: { result: BeamDesignResponse; trust: BeamTrust }) {
  const isPass = trust.status === "PASS";
  const isHeld = trust.status === "HOLD";
  const statusColor = isPass ? "text-emerald-200" : isHeld ? "text-amber-200" : "text-rose-200";
  const StatusIcon = isPass ? CheckCircle : AlertCircle;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className={'flex items-center gap-2 text-sm font-semibold ' + statusColor}>
            <StatusIcon size={18} className="shrink-0" aria-hidden="true" />
            Design {trust.status}
          </p>
          <p className="mt-1 break-words text-sm text-zinc-300">{result.message || "IS 456:2000"}</p>
        </div>
        <div className="text-right">
          <p className="font-mono text-xl font-semibold text-white">{formatPercent(trust.exactUtilization)}</p>
          <p className="text-xs text-zinc-300">Governing utilization</p>
        </div>
      </div>
      <dl className="grid grid-cols-2 gap-3 border-y border-zinc-700 py-3 text-sm sm:grid-cols-3">
        <div className="min-w-0">
          <dt className="text-xs text-zinc-400">Governing check</dt>
          <dd className="break-words text-zinc-100">{trust.governingCheck}</dd>
        </div>
        <div>
          <dt className="text-xs text-zinc-400">Utilization ratio</dt>
          <dd className="font-mono text-zinc-100">{formatRatio(trust.exactUtilization)}</dd>
        </div>
        <div>
          <dt className="text-xs text-zinc-400">Margin</dt>
          <dd className="font-mono text-zinc-100">{formatSignedRatio(trust.margin)}</dd>
        </div>
      </dl>
      {result.holds?.length ? (
        <ul className="list-disc space-y-1 pl-4 text-sm text-amber-200">
          {result.holds.map((hold) => <li key={hold}>{hold}</li>)}
        </ul>
      ) : null}
    </div>
  );
}

function BeamResultDetails({ result, trust }: { result: BeamDesignResponse; trust: BeamTrust }) {
  return (
    <div className="space-y-3">
      <p className="break-all font-mono text-xs text-zinc-300">
        Calculation ID {trust.calculationIdentity ?? "unavailable"}
      </p>
      {/* Cards row */}
      <div className="grid gap-2.5 sm:grid-cols-3">
        <ResultMiniCard title="Flexure" items={[
          { l: "Ast", v: `${result.flexure?.ast_required?.toFixed(0) || "-"} mm²` },
          { l: "xu", v: `${result.flexure?.xu?.toFixed(1) || "-"} mm` },
          { l: "Mu,cap", v: `${result.flexure?.moment_capacity?.toFixed(0) || "-"} kN·m` },
        ]} />
        <ResultMiniCard title="Shear" items={[
          { l: "τv", v: result.shear?.tau_v ? `${result.shear.tau_v.toFixed(2)} MPa` : "-" },
          { l: "Asv/s", v: result.shear ? `${result.shear.asv_required.toFixed(4)} ${result.shear.asv_required_unit}` : "-" },
          { l: "Sv", v: result.shear?.stirrup_spacing ? `${result.shear.stirrup_spacing} mm` : "-" },
        ]} />
        <ResultMiniCard title="Summary" items={[
          { l: "Ast total", v: `${result.ast_total?.toFixed(0) || "-"} mm²` },
          { l: "Asc", v: `${result.asc_total?.toFixed(0) || "0"} mm²` },
          { l: "Status", v: trust.status },
        ]} />
      </div>

      {result.combined_actions && result.torsion && (
        <div className="grid grid-cols-2 gap-2.5">
          <ResultMiniCard title="Original / Equivalent Actions" items={[
            { l: "Mu / Me", v: `${result.combined_actions.mu_knm.toFixed(1)} / ${result.combined_actions.me_knm.toFixed(1)} kN·m` },
            { l: "Vu / Ve", v: `${result.combined_actions.vu_kn.toFixed(1)} / ${result.combined_actions.ve_kn.toFixed(1)} kN` },
            { l: "Tu", v: `${result.combined_actions.tu_knm.toFixed(1)} kN·m` },
          ]} />
          <ResultMiniCard title={`Torsion · ${result.torsion.source}`} items={[
            { l: "Asv/s total", v: `${result.torsion.asv_total.toFixed(4)} mm²/mm` },
            { l: "Al", v: `${result.torsion.al_torsion.toFixed(1)} mm²` },
            { l: "Closed stirrups", v: result.torsion.requires_closed_stirrups ? "Required" : "Not required" },
          ]} />
          <p className="col-span-2 text-[10px] text-zinc-500">{Object.values(result.torsion.clause_refs).join(" · ")}</p>
        </div>
      )}

      {(result.deflection_check || result.crack_width_check) && (
        <div className="grid grid-cols-2 gap-2.5">
          {result.deflection_check && <ResultMiniCard title="Deflection" items={[
            { l: "Status", v: result.deflection_check.is_ok ? "PASS" : "FAIL" },
            { l: "L/d actual", v: result.deflection_check.span_depth_actual?.toFixed(2) ?? "-" },
            { l: "L/d allowable", v: result.deflection_check.span_depth_allowable?.toFixed(2) ?? "-" },
          ]} />}
          {result.crack_width_check && <ResultMiniCard title="Crack width" items={[
            { l: "Status", v: result.crack_width_check.is_ok ? "PASS" : "FAIL" },
            { l: "Calculated", v: result.crack_width_check.crack_width_mm == null ? "-" : `${result.crack_width_check.crack_width_mm.toFixed(3)} mm` },
            { l: "Limit", v: result.crack_width_check.crack_width_limit_mm == null ? "-" : `${result.crack_width_check.crack_width_limit_mm.toFixed(3)} mm` },
          ]} />}
        </div>
      )}

      {/* Warnings */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="p-2.5 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
          {result.warnings.map((w, i) => (
            <p key={i} className="text-xs text-yellow-400/80">• {w}</p>
          ))}
        </div>
      )}
    </div>
  );
}

function ResultMiniCard({ title, items }: { title: string; items: { l: string; v: string }[] }) {
  return (
    <div className="p-3 rounded-xl bg-white/[0.03] border border-white/8">
      <h4 className="text-[10px] font-semibold text-white/50 uppercase tracking-wider mb-2">{title}</h4>
      <div className="space-y-1.5">
        {items.map((item) => (
          <div key={item.l} className="flex flex-wrap justify-between gap-x-2 text-xs">
            <span className="text-zinc-400">{item.l}</span>
            <span className="text-white font-medium">{item.v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------- Code Checks Panel ---------- */

function CodeChecksPanel({ data, isPending }: { data: ReturnType<typeof useCodeChecks>["data"]; isPending: boolean }) {
  const [expanded, setExpanded] = useState(false);
  if (isPending) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.02] border border-white/5">
        <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin" />
        <span className="text-xs text-zinc-400">Running code checks...</span>
      </div>
    );
  }
  if (!data) return null;

  const passCount = data.checks.filter((c: CheckDetail) => c.passed).length;
  const totalCount = data.checks.length;
  const allPassed = data.passed;

  return (
    <div className={`rounded-xl border ${allPassed ? "bg-green-500/5 border-green-500/20" : "bg-red-500/5 border-red-500/20"}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2.5 px-3 py-2.5"
      >
        <Shield className={`w-4 h-4 ${allPassed ? "text-green-400" : "text-red-400"}`} />
        <span className="text-xs font-semibold text-white/80">
          Code Checks: {passCount}/{totalCount} passed
        </span>
        {data.governing_check && (
          <span className="ml-auto text-[10px] text-zinc-400 mr-2">Gov: {data.governing_check}</span>
        )}
        {expanded ? <ChevronDown className="w-3.5 h-3.5 text-zinc-400" /> : <ChevronRight className="w-3.5 h-3.5 text-zinc-400" />}
      </button>
      {expanded && (
        <div className="px-3 pb-3 space-y-1.5">
          {data.checks.map((check: CheckDetail) => (
            <div key={check.name} className="flex items-center gap-2 text-xs">
              {check.passed ? (
                <CheckCircle className="w-3.5 h-3.5 text-green-400 shrink-0" />
              ) : (
                <AlertCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
              )}
              <span className="text-white/70 flex-1">{check.name}</span>
              <span className="text-[10px] text-zinc-500">{check.clause}</span>
              {check.utilization != null && (
                <span className={`text-[10px] font-medium ${check.utilization <= 1 ? "text-green-400/70" : "text-red-400/70"}`}>
                  {(check.utilization * 100).toFixed(0)}%
                </span>
              )}
            </div>
          ))}
          {data.critical_failures.length > 0 && (
            <div className="mt-2 p-2 rounded-lg bg-red-500/10 border border-red-500/20">
              <p className="text-[10px] font-semibold text-red-400 mb-1">Critical Failures:</p>
              {data.critical_failures.map((f: string, i: number) => (
                <p key={i} className="text-[10px] text-red-400/70">• {f}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ---------- Rebar Suggestions Panel ---------- */

function RebarSuggestionsPanel({ data, isPending }: { data: ReturnType<typeof useRebarSuggestions>["data"]; isPending: boolean }) {
  const [expanded, setExpanded] = useState(false);
  if (isPending) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.02] border border-white/5">
        <Loader2 className="w-3.5 h-3.5 text-purple-400 animate-spin" />
        <span className="text-xs text-zinc-400">Finding rebar options...</span>
      </div>
    );
  }
  if (!data || data.suggestions.length === 0) return null;

  return (
    <div className="rounded-xl bg-purple-500/5 border border-purple-500/20">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2.5 px-3 py-2.5"
      >
        <Lightbulb className="w-4 h-4 text-purple-400" />
        <span className="text-xs font-semibold text-white/80">
          {data.suggestion_count} Rebar Option{data.suggestion_count !== 1 ? "s" : ""}
        </span>
        {data.max_savings_percent > 0 && (
          <span className="ml-1 px-1.5 py-0.5 text-[10px] font-medium bg-purple-500/20 text-purple-300 rounded">
            up to {data.max_savings_percent.toFixed(0)}% saving
          </span>
        )}
        {expanded ? <ChevronDown className="w-3.5 h-3.5 text-zinc-400 ml-auto" /> : <ChevronRight className="w-3.5 h-3.5 text-zinc-400 ml-auto" />}
      </button>
      {expanded && (
        <div className="px-3 pb-3 space-y-2">
          {data.suggestions.map((s: SuggestionItem) => (
            <div key={s.id} className="p-2.5 rounded-lg bg-white/[0.03] border border-white/8">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-xs font-semibold text-white/90">{s.title}</span>
                <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${
                  s.impact === "HIGH" ? "bg-green-500/20 text-green-300" :
                  s.impact === "MEDIUM" ? "bg-yellow-500/20 text-yellow-300" :
                  "bg-white/10 text-white/50"
                }`}>
                  {s.impact}
                </span>
                {s.savings_percent > 0 && (
                  <span className="text-[10px] text-green-400/70 ml-auto">-{s.savings_percent.toFixed(0)}% steel</span>
                )}
              </div>
              <p className="text-[10px] text-white/50 mb-1">{s.description}</p>
              <div className="flex gap-3 text-[10px] text-zinc-400">
                <span>{s.suggested_config.bar_count}Ø{s.suggested_config.bar_dia_mm}mm</span>
                <span>Ast: {s.suggested_config.ast_provided_mm2.toFixed(0)} mm²</span>
                {s.suggested_config.excess_mm2 > 0 && (
                  <span>+{s.suggested_config.excess_mm2.toFixed(0)} mm² excess</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ---------- Input Components ---------- */

function InputField({ label, value, onChange, unit, min, max, step = 1, disabled = false }: {
  label: string; value: number; onChange: (v: number) => void; unit: string;
  min?: number; max?: number; step?: number; disabled?: boolean;
}) {
  const fieldId = `design-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
  return (
    <div>
      <label htmlFor={fieldId} className="mb-1 block text-xs font-medium text-ink/80">
        {label}
      </label>
      <div className="relative">
        <input
          id={fieldId}
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={min}
          max={max}
          step={step}
          disabled={disabled}
          aria-label={`${label} in ${unit}`}
          className="min-h-10 w-full rounded-sm border border-ink/25 bg-white px-2.5 pr-10 text-sm text-ink disabled:opacity-50"
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-ink/75" aria-hidden="true">
          {unit}
        </span>
      </div>
    </div>
  );
}

function OptionalInputField({ label, value, onChange, unit, min, max, step = 1 }: {
  label: string; value: number | undefined; onChange: (v: number | undefined) => void;
  unit: string; min?: number; max?: number; step?: number;
}) {
  const fieldId = `design-optional-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
  return (
    <div>
      <label htmlFor={fieldId} className="mb-1 block text-xs font-medium text-ink/80">{label}</label>
      <div className="relative">
        <input
          id={fieldId}
          type="number"
          value={value ?? ""}
          onChange={(event) => onChange(event.target.value === "" ? undefined : Number(event.target.value))}
          min={min}
          max={max}
          step={step}
          aria-label={`${label} in ${unit}`}
          className="min-h-10 w-full rounded-sm border border-ink/25 bg-white px-2.5 pr-12 text-sm text-ink"
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-ink/75" aria-hidden="true">{unit}</span>
      </div>
    </div>
  );
}

function DropdownField<T extends string | number>({ label, value, onChange, options, format }: {
  label: string; value: T; onChange: (v: T) => void; options: T[]; format: (v: T) => string;
}) {
  const fieldId = `design-dropdown-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
  return (
    <div>
      <label htmlFor={fieldId} className="mb-1 block text-xs font-medium text-ink/80">
        {label}
      </label>
      <select
        id={fieldId}
        value={String(value)}
        onChange={(e) => {
          const raw = e.target.value;
          // If options are numbers, parse as number; otherwise keep as string
          const parsed = typeof options[0] === 'number' ? Number(raw) : raw;
          onChange(parsed as T);
        }}
        aria-label={label}
        className="min-h-10 w-full cursor-pointer rounded-sm border border-ink/25 bg-white px-2.5 text-sm text-ink"
      >
        {options.map((opt) => (
          <option key={String(opt)} value={String(opt)}>{format(opt)}</option>
        ))}
      </select>
    </div>
  );
}

/* ---------- Mini BMD/SFD Diagram ---------- */

function MiniDiagram({ data }: { data: LoadAnalysisResponse }) {
  const w = 260;
  const h = 60;
  const pad = 4;

  const drawPath = (values: number[]) => {
    const maxAbs = Math.max(...values.map(Math.abs), 0.01);
    const n = values.length;
    return values
      .map((v, i) => {
        const x = pad + ((w - 2 * pad) * i) / (n - 1);
        const y = h / 2 - (v / maxAbs) * (h / 2 - pad);
        return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  };

  return (
    <div className="col-span-2 space-y-1 rounded-sm border border-zinc-700 bg-ink p-2">
      <div className="flex flex-wrap justify-between gap-1 px-1 text-xs text-zinc-300">
        <span>Mu,max = <span className="text-cyan-300 font-semibold">{data.max_bm_knm.toFixed(1)}</span> kN·m</span>
        <span>Mu,min = <span className="text-cyan-300 font-semibold">{data.min_bm_knm.toFixed(1)}</span> kN·m</span>
      </div>
      <svg width={w} height={h} className="w-full" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
        {/* Zero line */}
        <line x1={pad} y1={h / 2} x2={w - pad} y2={h / 2} stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
        {/* BMD */}
        <path d={drawPath(data.bmd_knm)} fill="none" stroke="#22d3ee" strokeWidth="1.5" opacity="0.8" />
        {/* SFD */}
        <path d={drawPath(data.sfd_kn)} fill="none" stroke="#a78bfa" strokeWidth="1" opacity="0.5" strokeDasharray="3,2" />
      </svg>
      <div className="flex gap-3 justify-center">
        <span className="text-[9px] text-cyan-400/60 flex items-center gap-1"><span className="w-3 h-0.5 bg-cyan-400 inline-block rounded" /> BMD</span>
        <span className="text-[9px] text-violet-400/60 flex items-center gap-1"><span className="w-3 h-0.5 bg-violet-400 inline-block rounded border-dashed" /> SFD</span>
      </div>
    </div>
  );
}
