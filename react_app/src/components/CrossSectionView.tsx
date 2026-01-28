/**
 * CrossSectionView - 2D SVG rendering of beam cross-section.
 *
 * Shows concrete outline, rebar positions (circles), stirrup loop, and dimensions.
 */

interface CrossSectionViewProps {
  width: number;    // mm
  depth: number;    // mm
  cover: number;    // mm
  astRequired: number;  // mm² (for bar count calculation)
  stirrupDia?: number;  // mm
  className?: string;
}

export function CrossSectionView({
  width,
  depth,
  cover,
  astRequired,
  stirrupDia = 8,
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

  // Calculate bar count from Ast (assuming 16mm bars)
  const barDia = 16;
  const barArea = Math.PI * (barDia / 2) ** 2;
  const numBars = Math.max(2, Math.ceil(astRequired / barArea));
  const barR = (barDia / 2) * scale;

  // Position bars along bottom (tension) and possibly top (compression)
  const tensionBars = Math.min(numBars, 6);
  const compressionBars = Math.min(2, Math.ceil(numBars * 0.3));

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

        {/* Bottom bars (tension) */}
        {bottomBars.map((bar, i) => (
          <circle
            key={`bottom-${i}`}
            cx={bar.x} cy={bar.y} r={barR}
            fill="#c87533" stroke="#e0a060" strokeWidth={1}
          />
        ))}

        {/* Top bars (compression) */}
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
        <text x={bX + 4} y={barY_bottom - 4} fill="#888" fontSize={9}>
          {cover}mm cover
        </text>

        {/* Bar label */}
        <text x={bX + bW + 8} y={barY_bottom + 4} fill="#c87533" fontSize={10} fontWeight="bold">
          {tensionBars}-T{barDia}
        </text>
        {compressionBars > 0 && (
          <text x={bX + bW + 8} y={barY_top + 4} fill="#c87533" fontSize={10}>
            {compressionBars}-T{barDia}
          </text>
        )}
      </svg>

      {/* Legend */}
      <div className="flex gap-4 mt-4 text-xs text-white/50">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-[#c87533]" />
          <span>Rebar ({barDia}mm)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-1 bg-[#a06020]" />
          <span>Stirrup ({stirrupDia}mm)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-[#2a2a2e] border border-[#555]" />
          <span>Concrete</span>
        </div>
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
