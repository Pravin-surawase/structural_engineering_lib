import type { FormEvent } from 'react';
import type { ColumnEndCondition, ColumnReviewInputs } from './types';

export interface ColumnInputEditorProps {
  inputs: ColumnReviewInputs;
  isSubmitting: boolean;
  onChange: (patch: Partial<ColumnReviewInputs>) => void;
  onSubmit: () => void;
}

interface NumberInputProps {
  label: string;
  unit: string;
  value: number;
  min?: number;
  step?: number;
  onChange: (value: number) => void;
}

function NumberInput({ label, unit, value, min = 0, step = 1, onChange }: NumberInputProps) {
  return (
    <label className="grid gap-1 text-xs text-zinc-300">
      <span>{label} <span className="text-zinc-500">({unit})</span></span>
      <input
        aria-label={label}
        type="number"
        min={min}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="rounded-lg border border-white/10 bg-zinc-950 px-3 py-2 text-sm text-white"
      />
    </label>
  );
}

export function ColumnInputEditor({
  inputs,
  isSubmitting,
  onChange,
  onSubmit,
}: ColumnInputEditorProps) {
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={submit} className="space-y-4" aria-label="Rectangular column inputs">
      <div>
        <h2 className="text-lg font-semibold text-white">Rectangular column inputs</h2>
        <p className="mt-1 text-xs leading-5 text-zinc-400">
          Supplied-section adequacy check only. Units are mm, kN, kN·m, and N/mm².
        </p>
      </div>

      <label className="grid gap-1 text-xs text-zinc-300">
        <span>Member label</span>
        <input
          aria-label="Member label"
          value={inputs.member_label}
          onChange={(event) => onChange({ member_label: event.target.value })}
          className="rounded-lg border border-white/10 bg-zinc-950 px-3 py-2 text-sm text-white"
        />
      </label>

      <fieldset className="grid grid-cols-2 gap-3 rounded-xl border border-white/10 p-3">
        <legend className="px-1 text-xs font-semibold text-zinc-200">Section and loads</legend>
        <NumberInput label="Width b" unit="mm" value={inputs.b_mm} min={100} onChange={(b_mm) => onChange({ b_mm })} />
        <NumberInput label="Depth D" unit="mm" value={inputs.D_mm} min={100} onChange={(D_mm) => onChange({ D_mm })} />
        <NumberInput label="Unsupported length" unit="mm" value={inputs.l_mm} min={100} onChange={(l_mm) => onChange({ l_mm })} />
        <NumberInput label="Factored axial load" unit="kN" value={inputs.Pu_kN} onChange={(Pu_kN) => onChange({ Pu_kN })} />
        <NumberInput label="Applied Mux" unit="kN·m" value={inputs.Mux_kNm} step={0.1} onChange={(Mux_kNm) => onChange({ Mux_kNm })} />
        <NumberInput label="Applied Muy" unit="kN·m" value={inputs.Muy_kNm} step={0.1} onChange={(Muy_kNm) => onChange({ Muy_kNm })} />
      </fieldset>

      <fieldset className="grid grid-cols-2 gap-3 rounded-xl border border-white/10 p-3">
        <legend className="px-1 text-xs font-semibold text-zinc-200">Materials and supplied ties</legend>
        <NumberInput label="Concrete fck" unit="N/mm²" value={inputs.fck_nmm2} min={15} onChange={(fck_nmm2) => onChange({ fck_nmm2 })} />
        <NumberInput label="Steel fy" unit="N/mm²" value={inputs.fy_nmm2} min={250} onChange={(fy_nmm2) => onChange({ fy_nmm2 })} />
        <NumberInput label="Longitudinal bars" unit="count" value={inputs.num_bars} min={3} onChange={(num_bars) => onChange({ num_bars })} />
        <NumberInput label="Longitudinal bar diameter" unit="mm" value={inputs.bar_dia_mm} min={8} onChange={(bar_dia_mm) => onChange({ bar_dia_mm })} />
        <NumberInput label="Clear cover" unit="mm" value={inputs.cover_mm} min={15} onChange={(cover_mm) => onChange({ cover_mm })} />
        <NumberInput label="Tie diameter" unit="mm" value={inputs.tie_dia_mm} min={6} onChange={(tie_dia_mm) => onChange({ tie_dia_mm })} />
        <NumberInput label="Steel centroid d prime" unit="mm" value={inputs.d_prime_mm} min={1} onChange={(d_prime_mm) => onChange({ d_prime_mm })} />
        <NumberInput label="Length for minimum eccentricity" unit="mm" value={inputs.l_unsupported_mm} min={100} onChange={(l_unsupported_mm) => onChange({ l_unsupported_mm })} />
      </fieldset>

      <fieldset className="space-y-3 rounded-xl border border-white/10 p-3">
        <legend className="px-1 text-xs font-semibold text-zinc-200">Analysis assumptions</legend>
        <label className="grid gap-1 text-xs text-zinc-300">
          <span>End condition</span>
          <select
            aria-label="End condition"
            value={inputs.end_condition}
            onChange={(event) => onChange({ end_condition: event.target.value as ColumnEndCondition })}
            className="rounded-lg border border-white/10 bg-zinc-950 px-3 py-2 text-sm text-white"
          >
            <option value="FIXED_FIXED">Fixed-fixed, no sway</option>
            <option value="FIXED_HINGED">Fixed-hinged</option>
            <option value="FIXED_FIXED_SWAY">Fixed-fixed, sway</option>
            <option value="FIXED_FREE">Fixed-free</option>
            <option value="HINGED_HINGED">Hinged-hinged</option>
            <option value="FIXED_PARTIAL">Fixed-partial</option>
            <option value="HINGED_PARTIAL">Hinged-partial</option>
          </select>
        </label>
        <label className="flex items-center gap-2 text-xs text-zinc-300">
          <input type="checkbox" checked={inputs.braced} onChange={(event) => onChange({ braced: event.target.checked })} />
          Braced frame for the maintained simplified long-column check
        </label>
        <label className="flex items-center gap-2 text-xs text-zinc-300">
          <input type="checkbox" checked={inputs.at_lap_section} onChange={(event) => onChange({ at_lap_section: event.target.checked })} />
          Review reinforcement at a lap section
        </label>
        <p className="rounded-lg bg-amber-400/10 px-3 py-2 text-xs leading-5 text-amber-100">
          Capacity assumes rectangular/square tied columns with symmetric two-face, two-layer reinforcement. Circular, PMM, arbitrary layouts, automatic sizing, and general second-order analysis are held.
        </p>
      </fieldset>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
      >
        {isSubmitting ? 'Checking column…' : 'Check supplied column'}
      </button>
    </form>
  );
}
