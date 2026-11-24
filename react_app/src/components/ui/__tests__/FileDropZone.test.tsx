import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useImportedBeamsStore } from '../../../store/importedBeamsStore';
import { FileDropZone } from '../FileDropZone';

const materials = { fck: 25, fy: 500, cover: 40, stirrupDiameter: 8, tensionBarDiameter: 16 };

function dropFile(filename: string) {
  const file = new File(['beam data'], filename, { type: 'text/csv' });
  fireEvent.drop(screen.getByLabelText('Choose CSV file'), { dataTransfer: { files: [file] } });
}

describe('FileDropZone', () => {
  beforeEach(() => {
    useImportedBeamsStore.setState({ beams: [], isImporting: false, error: null });
  });

  afterEach(() => vi.restoreAllMocks());

  it('ignores a second drop while a request is pending and accepts a retry after failure', async () => {
    let respondToFirst!: (response: Response) => void;
    const firstResponse = new Promise<Response>((resolve) => { respondToFirst = resolve; });
    const fetchImport = vi.spyOn(globalThis, 'fetch')
      .mockReturnValueOnce(firstResponse)
      .mockResolvedValueOnce(Response.json({
        success: true,
        beam_count: 1,
        warnings: [],
        beams: [{
          id: 'B1', width_mm: 300, depth_mm: 500, span_mm: 6000, fck_mpa: 25,
          fy_mpa: 500, cover_mm: 40, mu_knm: 100, vu_kn: 70,
        }],
      }));
    const queryClient = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <FileDropZone materialOverrides={materials} />
      </QueryClientProvider>,
    );

    act(() => {
      dropFile('first.csv');
      dropFile('ignored.csv');
    });
    await waitFor(() => expect(fetchImport).toHaveBeenCalledTimes(1));
    expect((fetchImport.mock.calls[0][1]?.body as FormData).get('file')).toHaveProperty('name', 'first.csv');
    expect(screen.getByLabelText('Choose CSV file')).toBeDisabled();

    respondToFirst(Response.json({ detail: 'Repair the source file.' }, { status: 422 }));
    await waitFor(() => expect(screen.getByLabelText('Choose CSV file')).toBeEnabled());
    dropFile('corrected.csv');

    expect(await screen.findByText('Imported 1 beam')).toBeVisible();
    expect(fetchImport).toHaveBeenCalledTimes(2);
    expect((fetchImport.mock.calls[1][1]?.body as FormData).get('file')).toHaveProperty('name', 'corrected.csv');
  });
});
