/**
 * BeamForm Component
 *
 * Input form for beam design parameters with live validation.
 * Supports auto-design mode with debounced updates.
 */
import { useCallback, useState } from 'react';
import { useDesignStore } from '../../store/designStore';
import { useMutation } from '@tanstack/react-query';
import { designBeam } from '../../api/client';
import { useAutoDesign } from '../../hooks/useAutoDesign';

interface ValidationErrors {
  [fieldName: string]: string | undefined;
}

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

  const [errors, setErrors] = useState<ValidationErrors>({});

  // Validation function
  const validate = useCallback((field?: string) => {
    const errs: ValidationErrors = {};

    // Width validation
    if (!field || field === 'width') {
      if (inputs.width < 150) {
        errs.width = 'Width < 150mm not recommended (IS 456 Cl 23.1.1)';
      } else if (inputs.width > 1000) {
        errs.width = 'Width exceeds typical beam range (max 1000mm)';
      } else if (inputs.width < 100) {
        errs.width = 'Width too small for structural beam';
      }
    }

    // Depth validation
    if (!field || field === 'depth') {
      if (inputs.depth < 200) {
        errs.depth = 'Depth < 200mm not recommended for beams';
      } else if (inputs.depth > 1500) {
        errs.depth = 'Depth exceeds typical beam range (max 1500mm)';
      }

      // Cross-field: depth should be reasonable w.r.t width (span-to-depth ratio)
      if (inputs.depth < inputs.width * 0.8) {
        errs.depth = 'Depth typically ≥ 0.8 × width for beams';
      }
    }

    // Length validation
    if (!field || field === 'length') {
      if (length < 1000) {
        errs.length = 'Span too short for structural beam';
      } else if (length > 12000) {
        errs.length = 'Span exceeds typical beam range (max 12m)';
      }

      // Span-to-depth ratio check (typical 10-20)
      const spanToDepth = length / inputs.depth;
      if (spanToDepth > 25) {
        errs.length = `High span/depth ratio (${spanToDepth.toFixed(1)}), consider deeper section`;
      } else if (spanToDepth < 5) {
        errs.length = `Low span/depth ratio (${spanToDepth.toFixed(1)}), section may be over-designed`;
      }
    }

    // Moment validation
    if (!field || field === 'moment') {
      if (inputs.moment < 0) {
        errs.moment = 'Moment cannot be negative';
      } else if (inputs.moment === 0) {
        errs.moment = 'Zero moment — check loading';
      } else if (inputs.moment > 2000) {
        errs.moment = 'Moment exceeds typical range (max 2000 kN·m)';
      }
    }

    // Shear validation
    if (!field || field === 'shear') {
      const shearValue = inputs.shear ?? 0;
      if (shearValue < 0) {
        errs.shear = 'Shear cannot be negative';
      } else if (shearValue > 1000) {
        errs.shear = 'Shear exceeds typical range (max 1000 kN)';
      }
    }

    // Update errors (only update the field being validated, or all if no field specified)
    setErrors((prev) => {
      if (field) {
        return { ...prev, [field]: errs[field] };
      }
      return errs;
    });

    return Object.keys(errs).length === 0;
  }, [inputs.width, inputs.depth, inputs.moment, inputs.shear, length]);

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
      // Clear error for this field when user starts typing
      setErrors((prev) => ({ ...prev, [field]: undefined }));

      if (field === 'length') {
        setLength(value);
      } else {
        setInputs({ [field]: value });
      }
    },
    [setInputs, setLength]
  );

  const handleBlur = useCallback(
    (field: string) => {
      // Validate this field on blur
      validate(field);
    },
    [validate]
  );

  const handleDesign = useCallback(() => {
    // Validate all fields before submission
    const isValid = validate();
    if (isValid) {
      designMutation.mutate(inputs);
    }
  }, [inputs, designMutation, validate]);

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

      <fieldset className="flex flex-col gap-2">
        <legend className="m-0 text-sm text-zinc-400 uppercase tracking-wide">Geometry</legend>
        <div className="flex flex-col gap-1">
          <label htmlFor="beam-width" className="flex flex-col gap-1 text-[13px] text-[#ccc] group relative">
            <span className="relative">
              Width (mm) <span aria-hidden="true">*</span>
              <span className="absolute left-0 -top-8 hidden group-hover:block bg-zinc-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50 border border-white/10 shadow-lg">
                Beam width (b) — minimum 150mm per IS 456 Cl 23.1
              </span>
            </span>
            <input
              id="beam-width"
              type="number"
              value={inputs.width}
              min={150}
              max={1000}
              step={10}
              onChange={(e) => handleInputChange('width', Number(e.target.value))}
              onBlur={() => handleBlur('width')}
              aria-required="true"
              aria-invalid={!!errors.width}
              aria-describedby={errors.width ? "beam-width-error" : undefined}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
            {errors.width && (
              <p id="beam-width-error" role="alert" className="text-amber-400 text-xs mt-1 leading-tight">{errors.width}</p>
            )}
          </label>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="beam-depth" className="flex flex-col gap-1 text-[13px] text-[#ccc] group relative">
            <span className="relative">
              Depth (mm) <span aria-hidden="true">*</span>
              <span className="absolute left-0 -top-8 hidden group-hover:block bg-zinc-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50 border border-white/10 shadow-lg">
                Overall depth of beam (D)
              </span>
            </span>
            <input
              id="beam-depth"
              type="number"
              value={inputs.depth}
              min={200}
              max={1500}
              step={10}
              onChange={(e) => handleInputChange('depth', Number(e.target.value))}
              onBlur={() => handleBlur('depth')}
              aria-required="true"
              aria-invalid={!!errors.depth}
              aria-describedby={errors.depth ? "beam-depth-error" : undefined}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
            {errors.depth && (
              <p id="beam-depth-error" role="alert" className="text-amber-400 text-xs mt-1 leading-tight">{errors.depth}</p>
            )}
          </label>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="beam-length" className="flex flex-col gap-1 text-[13px] text-[#ccc]">
            Length (mm) <span aria-hidden="true">*</span>
            <input
              id="beam-length"
              type="number"
              value={length}
              min={1000}
              max={12000}
              step={100}
              onChange={(e) => handleInputChange('length', Number(e.target.value))}
              onBlur={() => handleBlur('length')}
              aria-required="true"
              aria-invalid={!!errors.length}
              aria-describedby={errors.length ? "beam-length-error" : undefined}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
            {errors.length && (
              <p id="beam-length-error" role="alert" className="text-amber-400 text-xs mt-1 leading-tight">{errors.length}</p>
            )}
          </label>
        </div>
      </fieldset>

      <fieldset className="flex flex-col gap-2">
        <legend className="m-0 text-sm text-zinc-400 uppercase tracking-wide">Loading</legend>
        <div className="flex flex-col gap-1">
          <label htmlFor="beam-moment" className="flex flex-col gap-1 text-[13px] text-[#ccc] group relative">
            <span className="relative">
              Moment (kN·m) <span aria-hidden="true">*</span>
              <span className="absolute left-0 -top-8 hidden group-hover:block bg-zinc-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50 border border-white/10 shadow-lg">
                Factored bending moment (Mu) in kN·m
              </span>
            </span>
            <input
              id="beam-moment"
              type="number"
              value={inputs.moment}
              min={0}
              max={2000}
              step={5}
              onChange={(e) => handleInputChange('moment', Number(e.target.value))}
              onBlur={() => handleBlur('moment')}
              aria-required="true"
              aria-invalid={!!errors.moment}
              aria-describedby={errors.moment ? "beam-moment-error" : undefined}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
            {errors.moment && (
              <p id="beam-moment-error" role="alert" className="text-red-400 text-xs mt-1 leading-tight">{errors.moment}</p>
            )}
          </label>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="beam-shear" className="flex flex-col gap-1 text-[13px] text-[#ccc] group relative">
            <span className="relative">
              Shear (kN)
              <span className="absolute left-0 -top-8 hidden group-hover:block bg-zinc-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50 border border-white/10 shadow-lg">
                Factored shear force (Vu) in kN
              </span>
            </span>
            <input
              id="beam-shear"
              type="number"
              value={inputs.shear ?? 0}
              min={0}
              max={1000}
              step={5}
              onChange={(e) => handleInputChange('shear', Number(e.target.value))}
              onBlur={() => handleBlur('shear')}
              aria-invalid={!!errors.shear}
              aria-describedby={errors.shear ? "beam-shear-error" : undefined}
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            />
            {errors.shear && (
              <p id="beam-shear-error" role="alert" className="text-red-400 text-xs mt-1 leading-tight">{errors.shear}</p>
            )}
          </label>
        </div>
      </fieldset>

      <fieldset className="flex flex-col gap-2">
        <legend className="m-0 text-sm text-zinc-400 uppercase tracking-wide">Materials</legend>
        <div className="flex flex-col gap-1">
          <label htmlFor="beam-fck" className="flex flex-col gap-1 text-[13px] text-[#ccc] group relative">
            <span className="relative">
              Concrete fck (N/mm²) <span aria-hidden="true">*</span>
              <span className="absolute left-0 -top-8 hidden group-hover:block bg-zinc-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50 border border-white/10 shadow-lg">
                Characteristic compressive strength — IS 456 Table 2
              </span>
            </span>
            <select
              id="beam-fck"
              value={inputs.fck}
              onChange={(e) => handleInputChange('fck', Number(e.target.value))}
              aria-required="true"
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
          <label htmlFor="beam-fy" className="flex flex-col gap-1 text-[13px] text-[#ccc] group relative">
            <span className="relative">
              Steel fy (N/mm²) <span aria-hidden="true">*</span>
              <span className="absolute left-0 -top-8 hidden group-hover:block bg-zinc-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50 border border-white/10 shadow-lg">
                Characteristic yield strength of steel — IS 456 Table 2
              </span>
            </span>
            <select
              id="beam-fy"
              value={inputs.fy}
              onChange={(e) => handleInputChange('fy', Number(e.target.value))}
              aria-required="true"
              className="px-3 py-2 border border-[#444] rounded bg-[#2d2d2d] text-white text-sm w-full box-border focus:outline-none focus:border-[#0078d4] focus:ring-2 focus:ring-[#0078d4]/30"
            >
              <option value={415}>Fe415</option>
              <option value={500}>Fe500</option>
              <option value={550}>Fe550</option>
            </select>
          </label>
        </div>
      </fieldset>

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
