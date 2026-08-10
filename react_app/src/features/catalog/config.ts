export function catalogueQuickEnabled(value: string | undefined): boolean {
  return value !== 'false';
}

export const CATALOGUE_QUICK_ENABLED = catalogueQuickEnabled(
  import.meta.env.VITE_CATALOGUE_QUICK_ENABLED,
);
