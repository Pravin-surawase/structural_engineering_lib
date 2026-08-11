import { API_BASE_URL } from '../../config';
import type {
  ColumnDesignResponse,
  ColumnDetailingResponse,
  ColumnReviewBundle,
  ColumnReviewInputs,
} from './types';

interface APIEnvelope<T> {
  success: boolean;
  data: T;
}

async function requestData<T>(
  path: string,
  payload: Record<string, unknown>,
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    ...(signal ? { signal } : {}),
  });
  const body = await response.json().catch(() => null) as APIEnvelope<T> | null;
  if (!response.ok || !body?.success) {
    throw new Error(`Column check failed with HTTP ${response.status}`);
  }
  return body.data;
}

/**
 * Review supplied rectangular tied-column reinforcement using maintained APIs.
 * The detailing endpoint computes provided steel area; the unified adequacy
 * check consumes that server result so the browser does not duplicate math.
 */
export async function reviewRectangularColumn(
  inputs: ColumnReviewInputs,
  signal?: AbortSignal,
): Promise<ColumnReviewBundle> {
  const detailing = await requestData<ColumnDetailingResponse>(
    '/api/v1/design/column/detailing',
    {
      b_mm: inputs.b_mm,
      D_mm: inputs.D_mm,
      cover_mm: inputs.cover_mm,
      fck: inputs.fck_nmm2,
      fy: inputs.fy_nmm2,
      num_bars: inputs.num_bars,
      bar_dia_mm: inputs.bar_dia_mm,
      tie_dia_mm: inputs.tie_dia_mm,
      is_circular: false,
      at_lap_section: inputs.at_lap_section,
    },
    signal,
  );

  const design = await requestData<ColumnDesignResponse>(
    '/api/v1/design/column',
    {
      Pu_kN: inputs.Pu_kN,
      Mux_kNm: inputs.Mux_kNm,
      Muy_kNm: inputs.Muy_kNm,
      b_mm: inputs.b_mm,
      D_mm: inputs.D_mm,
      l_mm: inputs.l_mm,
      end_condition: inputs.end_condition,
      fck: inputs.fck_nmm2,
      fy: inputs.fy_nmm2,
      Asc_mm2: detailing.Asc_provided_mm2,
      d_prime_mm: inputs.d_prime_mm,
      l_unsupported_mm: inputs.l_unsupported_mm,
      braced: inputs.braced,
      M1x_kNm: inputs.M1x_kNm,
      M2x_kNm: inputs.M2x_kNm,
      M1y_kNm: inputs.M1y_kNm,
      M2y_kNm: inputs.M2y_kNm,
    },
    signal,
  );

  return { design, detailing };
}
