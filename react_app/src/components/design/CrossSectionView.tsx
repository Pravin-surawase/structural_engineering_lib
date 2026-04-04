/**
 * CrossSectionView - 2D SVG rendering of beam cross-section.
 *
 * Shows concrete outline, rebar positions (circles), stirrup loop, and dimensions.
 */

interface CrossSectionViewProps {
  width: number;        // mm
  depth: number;        // mm
  cover: number;        // mm
  astRequired: number;  // mm² (for bar count calculation)
  stirrupDia?: number;  // mm
  /** Override calculated bar diameter (mm) — use actual design value when available */
  barDia?: number;
  /** Override calculated bar count — use actual design value when available */
  barCount?: number;
  /** Required compression steel mm² — used to compute top bar count matching 3D geometry */
  ascRequired?: number;
  /** Utilization ratio (0–1+) — colors bars: ≤0.85 emerald, ≤1.0 amber, >1.0 rose */
  utilization?: number;
  className?: string;
}

export function CrossSectionView({
  width,
  depth,
  cover,
  astRequired,
  stirrupDia = 8,
  barDia: barDiaProp,
  barCount: barCountProp,
  ascRequired,
  utilization,
  className = "",
}: CrossSectionViewProps) {
  // Scale to fit SVG viewport
  const padding = 60;
  const svgW = 400;
  const svgH = (depth / width) * (svgW - 2 * padding) + 2 * padding;
  const scale = (svgW - 2 * padding) / width;
  const bW = width * scale;
  const bH = depth * scale;
  const bX = padding;
  const bY = padding;

  const coverScaled = cover * scale;
  const stirrupR = stirrupDia * scale;

  // Stirrup rectangle (inside cover)
  const stX = bX + coverScaled;
  const stY = bY + coverScaled;
  const stW = bW - 2 * coverScaled;
  const stH = bH - 2 * coverScaled;

  // Bar diameter: use provided value or estimate from Ast
  const barDia = barDiaProp ?? 16;
  const barArea = Math.PI * (barDia / 2) ** 2;
  const numBars = barCountProp ?? Math.max(2, Math.ceil(astRequired / barArea));
  const barR = (barDia / 2) * scale;

  // Bar fill color based on utilization
  const barFill  = utilization == null ? "#c87533"
    : utilization > 1.0  ? "#f43f5e"   // rose  — overstressed
    : utilization > 0.85 ? "#f59e0b"   // amber — near limit
    : "#10b981";                        // emerald — good
  const barStroke = utilization == null ? "#e0a060"
    : utilization > 1.0  ? "#fb7185"
    : utilization > 0.85 ? "#fbbf24"
    : "#34d399";

  // Position bars along bottom (tension) and possibly top (compression)
  const tensionBars = Math.min(numBars, 6);
  // Top bar count: use ascRequired (matches 3D geometry API formula) or fall back to 30% of tension
  const compressionBars = ascRequired != null && ascRequired > 0
    ? Math.min(Math.max(2, Math.ceil(ascRequired / barArea)), 6)
    : Math.min(2, Math.ceil(numBars * 0.3));

  const barY_bottom = bY + bH - coverScaled - stirrupR - barR;
  const barY_top = bY + coverScaled + stirrupR + barR;

  const getBarPositions = (count: number, y: number) => {
    if (count <= 1) return [{ x: bX + bW / 2, y }];
    const startX = bX + coverScaled + stirrupR + barR;
    const endX = bX + bW - coverScaled - stirrupR - barR;
    const spacing = (endX - startX) / (count - 1);
    return Array.from({ length: count }, (_, i) => ({
      x: startX + i * spacing,
      y,
    }));
  };

  const bottomBars = getBarPositions(tensionBars, barY_bottom);
  const topBars = getBarPositions(compressionBars, barY_top);

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <svg
        width={svgW}
        height={svgH}
        viewBox={`0 0 ${svgW} ${svgH}`}
        className="max-w-full"
      >
        {/* Background */}
        <rect width={svgW} height={svgH} fill="transparent" />

        {/* Concrete outline */}
        <rect
          x={bX} y={bY} width={bW} height={bH}
          fill="#2a2a2e" stroke="#555" strokeWidth={2} rx={3}
        />

        {/* Stirrup loop */}
        <rect
          x={stX} y={stY} width={stW} height={stH}
          fill="none" stroke="#a06020" strokeWidth={stirrupR * 0.8} rx={2}
          strokeDasharray="none"
        />

        {/* Bottom bars (tension) — colored by utilization */}
        {bottomBars.map((bar, i) => (
          <circle
            key={`bottom-${i}`}
            cx={bar.x} cy={bar.y} r={barR}
            fill={barFill} stroke={barStroke} strokeWidth={1}
          />
        ))}

        {/* Top bars (compression) — always copper, not utilization-colored */}
        {topBars.map((bar, i) => (
          <circle
            key={`top-${i}`}
            cx={bar.x} cy={bar.y} r={barR * 0.85}
            fill="#c87533" stroke="#e0a060" strokeWidth={1}
          />
        ))}

        {/* Dimension: width */}
        <DimensionLine
          x1={bX} y1={bY + bH + 25} x2={bX + bW} y2={bY + bH + 25}
          label={`${width} mm`}
        />

        {/* Dimension: depth */}
        <DimensionLine
          x1={bX - 25} y1={bY} x2={bX - 25} y2={bY + bH}
          label={`${depth} mm`}
          vertical
        />

        {/* Cover dimension */}
        <line x1={bX} y1={barY_bottom} x2={bX + coverScaled + stirrupR + barR} y2={barY_bottom} stroke="#666" strokeWidth={0.5} strokeDasharray="3,3" />
        <text x={bX + 4} y={barY_bottom - 4} fill="#a1a1aa" fontSize={9}>
          {cover}mm cover
        </text>

        {/* Bar labels */}
        <text x={bX + bW + 8} y={barY_bottom + 4} fill={barFill} fontSize={10} fontWeight="bold">
          {tensionBars}-T{barDia}
        </text>
        {compressionBars > 0 && (
          <text x={bX + bW + 8} y={barY_top + 4} fill="#c87533" fontSize={10}>
            {compressionBars}-T{barDia}
          </text>
        )}

        {/* Utilization badge (top-right of beam) */}
        {utilization != null && (
          <>
            <rect x={bX + bW - 42} y={bY + 6} width={40} height={16} rx={4}
              fill={barFill + "33"} stroke={barFill + "88"} strokeWidth={1} />
            <text x={bX + bW - 22} y={bY + 18} fill={barFill} fontSize={9}
              textAnchor="middle" fontWeight="bold">
              {(utilization * 100).toFixed(0)}%
            </text>
          </>
        )}
      </svg>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-4 text-xs text-white/50">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: barFill }} />
          <span>T{barDia} tension</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-[#c87533]" />
          <span>T{barDia} compression</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-1 bg-[#a06020]" />
          <span>Stirrup ⌀{stirrupDia}</span>
        </div>
        {utilization != null && (
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: barFill + "55", border: `1px solid ${barFill}88` }} />
            <span className="font-medium" style={{ color: barFill }}>
              {utilization > 1.0 ? "Overstressed" : utilization > 0.85 ? "Near limit" : "OK"}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

function DimensionLine({ x1, y1, x2, y2, label, vertical = false }: {
  x1: number; y1: number; x2: number; y2: number; label: string; vertical?: boolean;
}) {
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;

  return (
    <g>
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#666" strokeWidth={1} />
      {/* End ticks */}
      {vertical ? (
        <>
          <line x1={x1 - 4} y1={y1} x2={x1 + 4} y2={y1} stroke="#666" strokeWidth={1} />
          <line x1={x1 - 4} y1={y2} x2={x1 + 4} y2={y2} stroke="#666" strokeWidth={1} />
          <text x={midX - 8} y={midY} fill="#999" fontSize={10} textAnchor="end" dominantBaseline="middle" transform={`rotate(-90, ${midX - 8}, ${midY})`}>
            {label}
          </text>
        </>
      ) : (
        <>
          <line x1={x1} y1={y1 - 4} x2={x1} y2={y1 + 4} stroke="#666" strokeWidth={1} />
          <line x1={x2} y1={y1 - 4} x2={x2} y2={y1 + 4} stroke="#666" strokeWidth={1} />
          <text x={midX} y={midY + 14} fill="#999" fontSize={10} textAnchor="middle">
            {label}
          </text>
        </>
      )}
    </g>
  );
}
