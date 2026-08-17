import { AlertTriangle, Database, Loader2 } from 'lucide-react';
import type {
  CatalogBeamTransportName,
  CatalogBeamValues,
  CatalogField,
} from './types';
import { useWorkflowCatalog } from './useWorkflowCatalog';

export interface CatalogBeamInputPanelProps {
  values: CatalogBeamValues;
  onChange: (name: CatalogBeamTransportName, value: number | undefined) => void;
  onUseManual: () => void;
  disabled?: boolean;
}

function FieldControl({
  field,
  value,
  onChange,
  disabled,
}: {
  field: CatalogField;
  value: number | undefined;
  onChange: (value: number | undefined) => void;
  disabled: boolean;
}) {
  const inputId = `catalog-field-${field.field_id}`;
  return (
    <label htmlFor={inputId} className="block space-y-1.5">
      <span className="flex items-center justify-between gap-2 text-xs font-medium text-zinc-300">
        {field.label}
        <span className="text-[10px] font-normal text-zinc-500">{field.unit}</span>
      </span>
      {field.widget === 'select' ? (
        <select
          id={inputId}
          aria-label={`${field.label} in ${field.unit}`}
          value={value ?? ''}
          disabled={disabled}
          onChange={(event) => onChange(Number(event.target.value))}
          className="w-full rounded-lg border border-white/10 bg-zinc-900 px-3 py-2 text-sm text-white outline-none focus:border-blue-400"
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
          className="w-full rounded-lg border border-white/10 bg-zinc-900 px-3 py-2 text-sm text-white outline-none focus:border-blue-400"
        />
      )}
    </label>
  );
}

export function CatalogBeamInputPanel({
  values,
  onChange,
  onUseManual,
  disabled = false,
}: CatalogBeamInputPanelProps) {
  const { catalog, error, loading } = useWorkflowCatalog();

  if (loading) {
    return (
      <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] p-3 text-xs text-zinc-400" role="status">
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
        Loading the approved beam contract…
      </div>
    );
  }

  if (!catalog || error) {
    return (
      <div className="rounded-xl border border-amber-400/30 bg-amber-400/10 p-3" role="alert">
        <div className="flex items-start gap-2 text-xs text-amber-100">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <div>
            <p className="font-semibold">Catalogue input is unavailable</p>
            <p className="mt-1 text-amber-100/70">{error ?? 'The approved beam contract could not be loaded.'}</p>
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
      <div className="flex items-start gap-2 rounded-xl border border-blue-400/20 bg-blue-400/[0.06] p-3">
        <Database className="mt-0.5 h-4 w-4 shrink-0 text-blue-300" aria-hidden="true" />
        <div>
          <p className="text-xs font-semibold text-blue-100">{capability.title}</p>
          <p className="mt-1 text-[10px] leading-4 text-blue-100/65">
            Catalogue {catalog.catalog_version} · {capability.request_schema_id}
          </p>
        </div>
      </div>
      {[...groups.entries()].map(([group, fields]) => (
        <fieldset key={group} className="grid grid-cols-2 gap-2.5 rounded-xl border border-white/8 bg-white/[0.03] p-3">
          <legend className="px-1 text-xs font-semibold text-white/70">{group}</legend>
          {fields.map((field) => (
            <FieldControl
              key={field.field_id}
              field={field}
              value={values[field.transport_name]}
              disabled={disabled}
              onChange={(value) => onChange(field.transport_name, value)}
            />
          ))}
        </fieldset>
      ))}
      <p className="text-[10px] leading-4 text-zinc-500">
        {capability.limitations.join(' ')}
      </p>
    </div>
  );
}
