import { useEffect, useState } from 'react';
import { fetchWorkflowCatalog } from './client';
import type { WorkflowCatalog } from './types';

interface CatalogState {
  catalog: WorkflowCatalog | null;
  error: string | null;
  loading: boolean;
}

const INITIAL_STATE: CatalogState = { catalog: null, error: null, loading: true };

export function useWorkflowCatalog(): CatalogState {
  const [state, setState] = useState<CatalogState>(INITIAL_STATE);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    fetchWorkflowCatalog(controller.signal).then(
      (catalog) => {
        if (active) setState({ catalog, error: null, loading: false });
      },
      (error: unknown) => {
        if (active && !controller.signal.aborted) {
          setState({
            catalog: null,
            error: error instanceof Error ? error.message : 'Workflow catalogue unavailable',
            loading: false,
          });
        }
      },
    );
    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  return state;
}
