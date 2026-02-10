/**
 * BeamForm Component
 *
 * Input form for beam design parameters with live validation.
 * Supports auto-design mode with debounced updates.
 */
import { useCallback } from 'react';
import { useDesignStore } from '../../store/designStore';
import { useMutation } from '@tanstack/react-query';
import { designBeam } from '../../api/client';
import { useAutoDesign } from '../../hooks/useAutoDesign';

export function BeamForm() {
  const {
    inputs,
    length,
    setInputs,
    setLength,
    setResult,
    setLoading,
    setError,
    isLoading,
    autoDesign,
    setAutoDesign,
    wsLatency,
  } = useDesignStore();

  // Auto-design hook (debounced REST calls)
  useAutoDesign(autoDesign);

  const designMutation = useMutation({
    mutationFn: designBeam,
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: (data) => {
      setResult(data);
    },
    onError: (error: Error) => {
      setError(error.message);
    },
    onSettled: () => {
      setLoading(false);
    },
  });

  const handleInputChange = useCallback(
    (field: string, value: number) => {
      if (field === 'length') {
        setLength(value);
      } else {
        setInputs({ [field]: value });
      }
    },
    [setInputs, setLength]
  );

  const handleDesign = useCallback(() => {
    designMutation.mutate(inputs);
  }, [inputs, designMutation]);

  return (
    <div className="p-4 flex flex-col gap-4 h-full overflow-y-auto bg-[#1e1e1e] text-[#e0e0e0]">
      <h2 className="m-0 text-lg text-white border-b border-[#333] pb-2">Beam Design</h2>

      {/* Live Update Toggle */}
      <div className="flex flex-col gap-2 bg-[#252525] px-3 py-2 rounded border border-[#333]">
        <label className="flex items-center gap-2 text-[13px] text-[#ccc] cursor-pointer">
          <input
            type="checkbox"
            checked={autoDesign}
            onChange={(e) => setAutoDesign(e.target.checked)}
            className="w-4 h-4 accent-[#0078d4] cursor-pointer"
          />
          <span className="shrink-0">Live Preview</span>
          {isLoading && <span className="text-[#0078d4] animate-pulse">...</span>}
          {wsLatency !== null && (
            <span className="ml-auto text-[11px] text-green-500 bg-green-500/15 px-1.5 py-0.5 rounded">
              {wsLatency.toFixed(0)}ms
            </span>
          )}
        </label>
      </div>

      <div className="flex flex-col gap-2">
        <h3 className="m-0 text-sm text-[#888] uppercase tracking-wide">Geometry</h3>
        <div className="flex flex-col gap-1">
          <label className="flex flex-col gap-1 text-[13px] text-[#ccc]">
            Width (mm)
            <input
              type="number"
              value={inputs.width}
              min={150}
              max={1000}
              step={10}
              onChange={(e) => handleInputChange('width', Number(e.target.value))}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
          </label>
        </div>
        <div className="flex flex-col gap-1">
          <label className="flex flex-col gap-1 text-[13px] text-[#ccc]">
            Depth (mm)
            <input
              type="number"
              value={inputs.depth}
              min={200}
              max={1500}
              step={10}
              onChange={(e) => handleInputChange('depth', Number(e.target.value))}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
          </label>
        </div>
        <div className="flex flex-col gap-1">
          <label className="flex flex-col gap-1 text-[13px] text-[#ccc]">
            Length (mm)
            <input
              type="number"
              value={length}
              min={1000}
              max={12000}
              step={100}
              onChange={(e) => handleInputChange('length', Number(e.target.value))}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
          </label>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <h3 className="m-0 text-sm text-[#888] uppercase tracking-wide">Loading</h3>
        <div className="flex flex-col gap-1">
          <label className="flex flex-col gap-1 text-[13px] text-[#ccc]">
            Moment (kN·m)
            <input
              type="number"
              value={inputs.moment}
              min={0}
              max={2000}
              step={5}
              onChange={(e) => handleInputChange('moment', Number(e.target.value))}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
          </label>
        </div>
        <div className="flex flex-col gap-1">
          <label className="flex flex-col gap-1 text-[13px] text-[#ccc]">
            Shear (kN)
            <input
              type="number"
              value={inputs.shear ?? 0}
              min={0}
              max={1000}
              step={5}
              onChange={(e) => handleInputChange('shear', Number(e.target.value))}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
          </label>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <h3 className="m-0 text-sm text-[#888] uppercase tracking-wide">Materials</h3>
        <div className="flex flex-col gap-1">
          <label className="flex flex-col gap-1 text-[13px] text-[#ccc]">
            Concrete fck (N/mm²)
            <select
              value={inputs.fck}
              onChange={(e) => handleInputChange('fck', Number(e.target.value))}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            >
              <option value={20}>M20</option>
              <option value={25}>M25</option>
              <option value={30}>M30</option>
              <option value={35}>M35</option>
              <option value={40}>M40</option>
            </select>
          </label>
        </div>
        <div className="flex flex-col gap-1">
          <label className="flex flex-col gap-1 text-[13px] text-[#ccc]">
            Steel fy (N/mm²)
            <select
              value={inputs.fy}
              onChange={(e) => handleInputChange('fy', Number(e.target.value))}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            >
              <option value={415}>Fe415</option>
              <option value={500}>Fe500</option>
              <option value={550}>Fe550</option>
            </select>
          </label>
        </div>
      </div>

      {/* Manual design button (hidden in auto mode) */}
      {!autoDesign && (
        <button
          className="px-6 py-3 bg-[#0078d4] text-white border-none rounded text-sm font-semibold cursor-pointer transition-colors mt-2 hover:enabled:bg-[#106ebe] disabled:bg-[#555] disabled:cursor-not-allowed"
          onClick={handleDesign}
          disabled={isLoading || designMutation.isPending}
        >
          {designMutation.isPending ? 'Designing...' : 'Design Beam'}
        </button>
      )}
    </div>
  );
}
