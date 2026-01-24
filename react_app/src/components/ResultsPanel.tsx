/**
 * ResultsPanel Component
 *
 * Displays beam design results from the API.
 */
import { useDesignStore } from '../store/designStore';
import './ResultsPanel.css';

export function ResultsPanel() {
  const { result, error, isLoading } = useDesignStore();

  if (isLoading) {
    return (
      <div className="results-panel">
        <h2>Results</h2>
        <div className="loading">Calculating...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-panel">
        <h2>Results</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="results-panel">
        <h2>Results</h2>
        <div className="placeholder">
          Click "Design Beam" to calculate reinforcement.
        </div>
      </div>
    );
  }

  const { flexure, shear, ast_total, asc_total, utilization_ratio, warnings } = result;

  return (
    <div className="results-panel">
      <h2>Design Results</h2>

      {/* Status */}
      <div className={`status ${result.success ? 'success' : 'failed'}`}>
        {result.success ? '✓ Design OK' : '✗ Design Failed'}
      </div>

      {/* Flexure Results */}
      <div className="result-section">
        <h3>Flexure</h3>
        <div className="result-grid">
          <div className="result-item">
            <span className="label">Ast Required</span>
            <span className="value">{flexure.ast_required.toFixed(0)} mm²</span>
          </div>
          <div className="result-item">
            <span className="label">Ast Min</span>
            <span className="value">{flexure.ast_min.toFixed(0)} mm²</span>
          </div>
          <div className="result-item">
            <span className="label">Ast Max</span>
            <span className="value">{flexure.ast_max.toFixed(0)} mm²</span>
          </div>
          <div className="result-item">
            <span className="label">xu/xu,max</span>
            <span className="value">
              {((flexure.xu / flexure.xu_max) * 100).toFixed(1)}%
            </span>
          </div>
          <div className="result-item">
            <span className="label">Under-reinforced</span>
            <span className={`value ${flexure.is_under_reinforced ? 'good' : 'bad'}`}>
              {flexure.is_under_reinforced ? 'Yes ✓' : 'No ✗'}
            </span>
          </div>
          <div className="result-item">
            <span className="label">Moment Capacity</span>
            <span className="value">{flexure.moment_capacity.toFixed(1)} kN·m</span>
          </div>
        </div>
      </div>

      {/* Shear Results */}
      {shear && (
        <div className="result-section">
          <h3>Shear</h3>
          <div className="result-grid">
            <div className="result-item">
              <span className="label">τv</span>
              <span className="value">{shear.tau_v.toFixed(2)} N/mm²</span>
            </div>
            <div className="result-item">
              <span className="label">τc</span>
              <span className="value">{shear.tau_c.toFixed(2)} N/mm²</span>
            </div>
            <div className="result-item">
              <span className="label">Stirrup Asv</span>
              <span className="value">{shear.asv_required.toFixed(0)} mm²</span>
            </div>
            <div className="result-item">
              <span className="label">Spacing</span>
              <span className="value">{shear.stirrup_spacing.toFixed(0)} mm</span>
            </div>
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="result-section summary">
        <h3>Summary</h3>
        <div className="result-grid">
          <div className="result-item highlight">
            <span className="label">Total Tension Steel</span>
            <span className="value">{ast_total.toFixed(0)} mm²</span>
          </div>
          <div className="result-item">
            <span className="label">Compression Steel</span>
            <span className="value">{asc_total.toFixed(0)} mm²</span>
          </div>
          <div className="result-item">
            <span className="label">Utilization</span>
            <span
              className={`value ${
                utilization_ratio < 0.9 ? 'good' : utilization_ratio < 1.0 ? 'warning' : 'bad'
              }`}
            >
              {(utilization_ratio * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {warnings && warnings.length > 0 && (
        <div className="result-section warnings">
          <h3>Warnings</h3>
          <ul>
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
