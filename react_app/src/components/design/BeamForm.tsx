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
import './BeamForm.css';

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
    <div className="beam-form">
      <h2>Beam Design</h2>

      {/* Live Update Toggle */}
      <div className="form-section settings">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={autoDesign}
            onChange={(e) => setAutoDesign(e.target.checked)}
          />
          <span>Live Preview</span>
          {isLoading && <span className="loading-indicator">...</span>}
          {wsLatency !== null && (
            <span className="latency">{wsLatency.toFixed(0)}ms</span>
          )}
        </label>
      </div>

      <div className="form-section">
        <h3>Geometry</h3>
        <div className="form-row">
          <label>
            Width (mm)
            <input
              type="number"
              value={inputs.width}
              min={150}
              max={1000}
              step={10}
              onChange={(e) => handleInputChange('width', Number(e.target.value))}
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Depth (mm)
            <input
              type="number"
              value={inputs.depth}
              min={200}
              max={1500}
              step={10}
              onChange={(e) => handleInputChange('depth', Number(e.target.value))}
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Length (mm)
            <input
              type="number"
              value={length}
              min={1000}
              max={12000}
              step={100}
              onChange={(e) => handleInputChange('length', Number(e.target.value))}
            />
          </label>
        </div>
      </div>

      <div className="form-section">
        <h3>Loading</h3>
        <div className="form-row">
          <label>
            Moment (kN·m)
            <input
              type="number"
              value={inputs.moment}
              min={0}
              max={2000}
              step={5}
              onChange={(e) => handleInputChange('moment', Number(e.target.value))}
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Shear (kN)
            <input
              type="number"
              value={inputs.shear ?? 0}
              min={0}
              max={1000}
              step={5}
              onChange={(e) => handleInputChange('shear', Number(e.target.value))}
            />
          </label>
        </div>
      </div>

      <div className="form-section">
        <h3>Materials</h3>
        <div className="form-row">
          <label>
            Concrete fck (N/mm²)
            <select
              value={inputs.fck}
              onChange={(e) => handleInputChange('fck', Number(e.target.value))}
            >
              <option value={20}>M20</option>
              <option value={25}>M25</option>
              <option value={30}>M30</option>
              <option value={35}>M35</option>
              <option value={40}>M40</option>
            </select>
          </label>
        </div>
        <div className="form-row">
          <label>
            Steel fy (N/mm²)
            <select
              value={inputs.fy}
              onChange={(e) => handleInputChange('fy', Number(e.target.value))}
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
          className="design-button"
          onClick={handleDesign}
          disabled={isLoading || designMutation.isPending}
        >
          {designMutation.isPending ? 'Designing...' : 'Design Beam'}
        </button>
      )}
    </div>
  );
}
