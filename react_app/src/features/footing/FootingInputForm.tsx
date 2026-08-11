import type { FootingDraft } from './draft';

interface FootingInputFormProps {
  draft: FootingDraft;
  issues: string[];
  disabled: boolean;
  onChange: (
    key: keyof FootingDraft,
    value: FootingDraft[keyof FootingDraft],
  ) => void;
}

interface NumberFieldDefinition {
  key: keyof FootingDraft;
  label: string;
  unit: string;
  step?: number;
  minimum?: number;
}

const NUMBER_INPUT_CLASS =
  'mt-1 w-full rounded-lg border border-white/10 bg-zinc-950 px-3 py-2 text-sm text-white outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:text-zinc-500';
const TEXT_INPUT_CLASS = NUMBER_INPUT_CLASS;
const CHECKBOX_CLASS = 'mt-0.5 h-4 w-4 accent-blue-500';
const FIELDSET_CLASS = 'space-y-3 rounded-xl border border-white/8 bg-white/[0.02] p-4';

const GEOMETRY_FIELDS: NumberFieldDefinition[] = [
  { key: 'column_L_mm', label: 'Column dimension L', unit: 'mm', minimum: 1 },
  { key: 'column_B_mm', label: 'Column dimension B', unit: 'mm', minimum: 1 },
  {
    key: 'minimum_overall_thickness_mm',
    label: 'Minimum overall thickness',
    unit: 'mm',
    minimum: 150,
  },
  {
    key: 'maximum_overall_thickness_mm',
    label: 'Maximum overall thickness',
    unit: 'mm',
    minimum: 150,
  },
  { key: 'thickness_increment_mm', label: 'Thickness increment', unit: 'mm', minimum: 1 },
  {
    key: 'effective_depth_offset_L_mm',
    label: 'Effective-depth offset L',
    unit: 'mm',
    minimum: 1,
  },
  {
    key: 'effective_depth_offset_B_mm',
    label: 'Effective-depth offset B',
    unit: 'mm',
    minimum: 1,
  },
];

const MATERIAL_FIELDS: NumberFieldDefinition[] = [
  {
    key: 'footing_concrete_fck_nmm2',
    label: 'Footing concrete fck',
    unit: 'N/mm²',
    minimum: 1,
  },
  {
    key: 'column_concrete_fck_nmm2',
    label: 'Column concrete fck',
    unit: 'N/mm²',
    minimum: 1,
  },
  { key: 'steel_fy_nmm2', label: 'Reinforcement fy', unit: 'N/mm²', minimum: 1 },
];

const TRANSFER_FIELDS: NumberFieldDefinition[] = [
  { key: 'dowel_count', label: 'Dowel count', unit: 'bars', minimum: 1, step: 1 },
  { key: 'dowel_diameter_mm', label: 'Dowel diameter', unit: 'mm', minimum: 1 },
  {
    key: 'column_longitudinal_bar_diameter_mm',
    label: 'Column longitudinal-bar diameter',
    unit: 'mm',
    minimum: 1,
  },
  {
    key: 'available_dowel_development_length_into_footing_mm',
    label: 'Available dowel length into footing',
    unit: 'mm',
    minimum: 1,
  },
  {
    key: 'available_dowel_development_length_into_column_mm',
    label: 'Available dowel length into column',
    unit: 'mm',
    minimum: 1,
  },
];

function TextField({
  fieldKey,
  label,
  value,
  disabled,
  onChange,
}: {
  fieldKey: keyof FootingDraft;
  label: string;
  value: string;
  disabled: boolean;
  onChange: FootingInputFormProps['onChange'];
}) {
  return (
    <label className="block text-xs font-medium text-zinc-300">
      {label}
      <input
        aria-label={label}
        className={TEXT_INPUT_CLASS}
        disabled={disabled}
        value={value}
        onChange={(event) => onChange(fieldKey, event.target.value)}
      />
    </label>
  );
}

function NumberField({
  definition,
  value,
  disabled,
  onChange,
}: {
  definition: NumberFieldDefinition;
  value: number;
  disabled: boolean;
  onChange: FootingInputFormProps['onChange'];
}) {
  const descriptionId = `${String(definition.key)}-unit`;
  return (
    <label className="block text-xs font-medium text-zinc-300">
      {definition.label}
      <span id={descriptionId} className="ml-1 text-zinc-500">
        ({definition.unit})
      </span>
      <input
        aria-describedby={descriptionId}
        aria-label={`${definition.label} in ${definition.unit}`}
        className={NUMBER_INPUT_CLASS}
        disabled={disabled}
        min={definition.minimum}
        step={definition.step ?? 'any'}
        type="number"
        value={value}
        onChange={(event) => onChange(definition.key, Number(event.target.value))}
      />
    </label>
  );
}

function NumberFieldGrid({
  definitions,
  draft,
  disabled,
  onChange,
}: {
  definitions: NumberFieldDefinition[];
  draft: FootingDraft;
  disabled: boolean;
  onChange: FootingInputFormProps['onChange'];
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {definitions.map((definition) => {
        const squareBDisabled =
          definition.key === 'column_B_mm'
          && draft.footing_type === 'ISOLATED_SQUARE';
        return (
          <NumberField
            key={definition.key}
            definition={definition}
            disabled={disabled || squareBDisabled}
            value={draft[definition.key] as number}
            onChange={onChange}
          />
        );
      })}
    </div>
  );
}

function ApprovalField({
  label,
  description,
  checked,
  disabled,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  disabled: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="flex items-start gap-3 rounded-lg border border-white/8 bg-zinc-950/60 p-3">
      <input
        aria-label={label}
        checked={checked}
        className={CHECKBOX_CLASS}
        disabled={disabled}
        type="checkbox"
        onChange={(event) => onChange(event.target.checked)}
      />
      <span>
        <span className="block text-sm font-medium text-zinc-100">{label}</span>
        <span className="mt-1 block text-xs leading-5 text-zinc-400">{description}</span>
      </span>
    </label>
  );
}

function DetailingFields({
  draft,
  disabled,
  onChange,
}: Omit<FootingInputFormProps, 'issues'>) {
  if (!draft.detailing_enabled) return null;

  return (
    <fieldset className={FIELDSET_CLASS}>
      <legend className="px-1 text-sm font-semibold text-white">
        Complete approved detailing inputs
      </legend>
      <div className="grid gap-3 sm:grid-cols-2">
        <NumberField
          definition={{ key: 'nominal_cover_mm', label: 'Nominal cover', unit: 'mm', minimum: 1 }}
          disabled={disabled}
          value={draft.nominal_cover_mm ?? 0}
          onChange={onChange}
        />
        <NumberField
          definition={{
            key: 'nominal_max_aggregate_size_mm',
            label: 'Nominal maximum aggregate size',
            unit: 'mm',
            minimum: 1,
          }}
          disabled={disabled}
          value={draft.nominal_max_aggregate_size_mm ?? 0}
          onChange={onChange}
        />
        <TextField
          fieldKey="cover_exposure_basis"
          label="Cover/exposure basis"
          value={draft.cover_exposure_basis ?? ''}
          disabled={disabled}
          onChange={onChange}
        />
        <label className="block text-xs font-medium text-zinc-300">
          Permitted bottom-bar diameters (mm, comma-separated)
          <input
            aria-label="Permitted bottom-bar diameters in mm"
            className={TEXT_INPUT_CLASS}
            disabled={disabled}
            value={(draft.permitted_bottom_bar_diameters_mm ?? []).join(', ')}
            onChange={(event) => {
              const diameters = event.target.value
                .split(',')
                .map((value) => value.trim())
                .filter((value) => value.length > 0)
                .map(Number);
              onChange('permitted_bottom_bar_diameters_mm', diameters);
            }}
          />
        </label>
        <label className="block text-xs font-medium text-zinc-300">
          Lower bottom-bar direction
          <select
            aria-label="Lower bottom-bar direction"
            className={TEXT_INPUT_CLASS}
            disabled={disabled}
            value={draft.lower_bottom_bar_direction ?? 'L'}
            onChange={(event) => onChange('lower_bottom_bar_direction', event.target.value as 'L' | 'B')}
          >
            <option value="L">L</option>
            <option value="B">B</option>
          </select>
        </label>
        <label className="block text-xs font-medium text-zinc-300">
          Upper bottom-bar direction
          <select
            aria-label="Upper bottom-bar direction"
            className={TEXT_INPUT_CLASS}
            disabled={disabled}
            value={draft.upper_bottom_bar_direction ?? 'B'}
            onChange={(event) => onChange('upper_bottom_bar_direction', event.target.value as 'L' | 'B')}
          >
            <option value="L">L</option>
            <option value="B">B</option>
          </select>
        </label>
        <label className="block text-xs font-medium text-zinc-300">
          Footing bottom-bar type
          <select
            aria-label="Footing bottom-bar type"
            className={TEXT_INPUT_CLASS}
            disabled={disabled}
            value={draft.footing_bottom_bar_type ?? 'deformed'}
            onChange={(event) => onChange(
              'footing_bottom_bar_type',
              event.target.value as 'deformed' | 'plain',
            )}
          >
            <option value="deformed">Deformed</option>
            <option value="plain">Plain</option>
          </select>
        </label>
      </div>
      <ApprovalField
        label="Cover exposure basis approved"
        description="Confirms that a qualified project decision supplied the exposure and cover basis."
        checked={draft.cover_exposure_basis_is_approved ?? false}
        disabled={disabled}
        onChange={(checked) => onChange('cover_exposure_basis_is_approved', checked)}
      />
    </fieldset>
  );
}

export function FootingInputForm({
  draft,
  issues,
  disabled,
  onChange,
}: FootingInputFormProps) {
  return (
    <div className="space-y-4">
      <fieldset className={FIELDSET_CLASS}>
        <legend className="px-1 text-sm font-semibold text-white">Case and actions</legend>
        <div className="grid gap-3 sm:grid-cols-2">
          <TextField
            fieldKey="case_id"
            label="Case ID"
            value={draft.case_id}
            disabled={disabled}
            onChange={onChange}
          />
          <label className="block text-xs font-medium text-zinc-300">
            Footing plan type
            <select
              aria-label="Footing plan type"
              className={TEXT_INPUT_CLASS}
              disabled={disabled}
              value={draft.footing_type}
              onChange={(event) => onChange(
                'footing_type',
                event.target.value as FootingDraft['footing_type'],
              )}
            >
              <option value="ISOLATED_SQUARE">Square, centred</option>
              <option value="ISOLATED_RECTANGULAR">Rectangular, centred</option>
            </select>
          </label>
          <TextField
            fieldKey="service_load_combination_id"
            label="Service load-combination ID"
            value={draft.service_load_combination_id}
            disabled={disabled}
            onChange={onChange}
          />
          <NumberField
            definition={{
              key: 'service_axial_load_kN',
              label: 'Service axial load',
              unit: 'kN',
              minimum: 1,
            }}
            disabled={disabled}
            value={draft.service_axial_load_kN}
            onChange={onChange}
          />
          <TextField
            fieldKey="factored_load_combination_id"
            label="Factored load-combination ID"
            value={draft.factored_load_combination_id}
            disabled={disabled}
            onChange={onChange}
          />
          <NumberField
            definition={{
              key: 'factored_axial_load_kN',
              label: 'Factored axial load',
              unit: 'kN',
              minimum: 1,
            }}
            disabled={disabled}
            value={draft.factored_axial_load_kN}
            onChange={onChange}
          />
        </div>
        <p className="text-xs leading-5 text-zinc-400">
          Service load basis: includes footing self-weight and overburden. The factored
          action is submitted separately; the client does not derive a load factor.
        </p>
      </fieldset>

      <fieldset className={FIELDSET_CLASS}>
        <legend className="px-1 text-sm font-semibold text-white">
          External soil and supporting-area evidence
        </legend>
        <div className="grid gap-3 sm:grid-cols-2">
          <NumberField
            definition={{
              key: 'allowable_soil_pressure_kPa',
              label: 'Allowable soil pressure',
              unit: 'kPa',
              minimum: 1,
            }}
            disabled={disabled}
            value={draft.allowable_soil_pressure_kPa}
            onChange={onChange}
          />
          <TextField
            fieldKey="allowable_soil_pressure_source_reference"
            label="Allowable-pressure source reference"
            value={draft.allowable_soil_pressure_source_reference}
            disabled={disabled}
            onChange={onChange}
          />
          <NumberField
            definition={{
              key: 'effective_supporting_area_A1_mm2',
              label: 'Effective supporting area A1',
              unit: 'mm²',
              minimum: 1,
            }}
            disabled={disabled}
            value={draft.effective_supporting_area_A1_mm2}
            onChange={onChange}
          />
          <div className="rounded-lg border border-white/8 bg-zinc-950/60 p-3 text-xs text-zinc-400">
            A1 basis
            <code className="mt-1 block break-all text-zinc-200">
              largest_frustum_1v_2h
            </code>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <ApprovalField
            label="Soil pressure externally approved"
            description="The service does not derive SBC or settlement capacity."
            checked={draft.soil_pressure_approved}
            disabled={disabled}
            onChange={(checked) => onChange('soil_pressure_approved', checked)}
          />
          <ApprovalField
            label="A1 area externally approved"
            description="The submitted effective supporting-area basis has been reviewed."
            checked={draft.a1_basis_approved}
            disabled={disabled}
            onChange={(checked) => onChange('a1_basis_approved', checked)}
          />
        </div>
      </fieldset>

      <fieldset className={FIELDSET_CLASS}>
        <legend className="px-1 text-sm font-semibold text-white">
          Geometry and depth search
        </legend>
        <NumberFieldGrid
          definitions={GEOMETRY_FIELDS}
          draft={draft}
          disabled={disabled}
          onChange={onChange}
        />
        {draft.footing_type === 'ISOLATED_SQUARE' ? (
          <p className="text-xs text-blue-200">
            Square mode keeps column B synchronized to column L.
          </p>
        ) : null}
      </fieldset>

      <fieldset className={FIELDSET_CLASS}>
        <legend className="px-1 text-sm font-semibold text-white">Materials</legend>
        <NumberFieldGrid
          definitions={MATERIAL_FIELDS}
          draft={draft}
          disabled={disabled}
          onChange={onChange}
        />
      </fieldset>

      <fieldset className={FIELDSET_CLASS}>
        <legend className="px-1 text-sm font-semibold text-white">
          Load transfer and dowels
        </legend>
        <NumberFieldGrid
          definitions={TRANSFER_FIELDS}
          draft={draft}
          disabled={disabled}
          onChange={onChange}
        />
        <label className="block text-xs font-medium text-zinc-300">
          Dowel bar type
          <select
            aria-label="Dowel bar type"
            className={TEXT_INPUT_CLASS}
            disabled={disabled}
            value={draft.dowel_bar_type ?? 'deformed'}
            onChange={(event) => onChange(
              'dowel_bar_type',
              event.target.value as 'deformed' | 'plain',
            )}
          >
            <option value="deformed">Deformed</option>
            <option value="plain">Plain</option>
          </select>
        </label>
      </fieldset>

      <fieldset className={FIELDSET_CLASS}>
        <legend className="px-1 text-sm font-semibold text-white">
          Optional complete detailing
        </legend>
        <label className="flex items-start gap-3 text-sm text-zinc-200">
          <input
            aria-label="Include complete detailing"
            checked={draft.detailing_enabled}
            className={CHECKBOX_CLASS}
            disabled={disabled}
            type="checkbox"
            onChange={(event) => onChange('detailing_enabled', event.target.checked)}
          />
          <span>
            Request a buildable reinforcement schedule
            <span className="mt-1 block text-xs leading-5 text-zinc-400">
              When omitted, a safe calculation remains an explicit detailing and
              aggregate HOLD.
            </span>
          </span>
        </label>
      </fieldset>

      <DetailingFields draft={draft} disabled={disabled} onChange={onChange} />

      {issues.length > 0 ? (
        <div
          className="rounded-xl border border-amber-400/30 bg-amber-400/10 p-4"
          role="alert"
        >
          <p className="text-sm font-semibold text-amber-100">Input review required</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-amber-100/80">
            {issues.map((issue) => <li key={issue}>{issue}</li>)}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
