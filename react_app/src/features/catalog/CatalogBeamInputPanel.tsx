import { AlertTriangle, Loader2 } from 'lucide-react';
import type {
  CatalogBeamTransportName,
  CatalogBeamValues,
  CatalogField,
} from './types';
import { useWorkflowCatalog } from './useWorkflowCatalog';

export interface CatalogBeamInputPanelProps {
  values: CatalogBeamValues;
  widthError?: string | null;
  onChange: (name: CatalogBeamTransportName, value: number | undefined) => void;
  onUseManual: () => void;
  disabled?: boolean;
}

const controlClass = 'min-h-10 w-full rounded-sm border border-ink/25 bg-white px-2.5 text-sm text-ink disabled:opacity-50';

function FieldControl({
  field,
  value,
  onChange,
  disabled,
  error,
}: {
  field: CatalogField;
  value: number | undefined;
  onChange: (value: number | undefined) => void;
  disabled: boolean;
  error: string | null;
}) {
  const inputId = `catalog-field-${field.field_id}`;
  return (
    <label htmlFor={inputId} className="block min-w-0 space-y-1.5">
      <span className="flex flex-wrap items-center justify-between gap-x-2 text-xs font-medium text-ink/80">
        {field.label}
        <span className="font-normal text-ink/75">{field.unit}</span>
      </span>
      {field.widget === 'select' ? (
        <select
          id={inputId}
          aria-label={`${field.label} in ${field.unit}`}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? `${inputId}-error` : undefined}
          value={value ?? ''}
          disabled={disabled}
          onChange={(event) => onChange(Number(event.target.value))}
          className={controlClass}
        >
          {field.choices.map((choice) => (
            <option key={String(choice)} value={Number(choice)}>
              {String(choice)}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={inputId}
          aria-label={`${field.label} in ${field.unit}`}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? `${inputId}-error` : undefined}
          type="number"
          value={value ?? ''}
          min={field.minimum ?? undefined}
          max={field.maximum ?? undefined}
          step="any"
          required={field.required}
          disabled={disabled}
          onChange={(event) => {
            const next = event.target.value;
            onChange(
              next === '' && field.default === null ? undefined : Number(next),
            );
          }}
          className={controlClass}
        />
      )}
      {error ? <span id={`${inputId}-error`} role="alert" className="block text-xs text-rose-800">{error}</span> : null}
    </label>
  );
}

export function CatalogBeamInputPanel({
  values,
  widthError = null,
  onChange,
  onUseManual,
  disabled = false,
}: CatalogBeamInputPanelProps) {
  const { catalog, error, loading } = useWorkflowCatalog();

  if (loading) {
    return (
      <div className="flex items-center gap-2 rounded-sm border border-ink/20 bg-white p-3 text-sm text-ink/80" role="status">
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
        Loading the approved beam contract…
      </div>
    );
  }

  if (!catalog || error) {
    return (
      <div className="rounded-sm border border-amber-300 bg-amber-50 p-3" role="alert">
        <div className="flex items-start gap-2 text-sm text-amber-950">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <div>
            <p className="font-semibold">Catalogue input is unavailable</p>
            <p className="mt-1">{error ?? 'The approved beam contract could not be loaded.'}</p>
            <button type="button" onClick={onUseManual} className="mt-2 font-semibold underline underline-offset-2">
              Use reviewed manual form
            </button>
          </div>
        </div>
      </div>
    );
  }

  const capability = catalog.capabilities[0];
  const groups = new Map<string, CatalogField[]>();
  for (const field of capability.fields) {
    groups.set(field.group, [...(groups.get(field.group) ?? []), field]);
  }

  return (
    <div className="space-y-3" data-testid="catalog-beam-inputs">
      {[...groups.entries()].map(([group, fields]) => (
        <fieldset key={group} className="grid min-w-0 grid-cols-2 gap-2.5 rounded-sm border border-ink/20 bg-white px-3 pb-3 pt-1">
          <legend className="px-1 text-sm font-semibold text-ink">{group}</legend>
          {fields.map((field) => (
            <FieldControl
              key={field.field_id}
              field={field}
              value={values[field.transport_name]}
              error={field.transport_name === 'width' ? widthError : null}
              disabled={disabled}
              onChange={(value) => onChange(field.transport_name, value)}
            />
          ))}
        </fieldset>
      ))}
      <details className="text-xs leading-relaxed text-ink/80">
        <summary className="cursor-pointer font-medium text-cobalt">Catalogue scope and source</summary>
        <p className="mt-2">{capability.title} · Catalogue {catalog.catalog_version} · {capability.request_schema_id}</p>
        <p className="mt-1">{capability.limitations.join(' ')}</p>
      </details>
    </div>
  );
}
