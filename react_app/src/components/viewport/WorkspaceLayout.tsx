/**
 * WorkspaceLayout Component
 *
 * Dockview-based IDE-like layout with resizable panels.
 */
import { useRef, useCallback } from 'react';
import { DockviewReact } from 'dockview';
import type { DockviewReadyEvent, IDockviewPanelProps } from 'dockview';
import 'dockview/dist/styles/dockview.css';
import { BeamForm } from '../design/BeamForm';
import { Viewport3D } from './Viewport3D';
import { ResultsPanel } from '../design/ResultsPanel';
import './WorkspaceLayout.css';

// Panel components wrapped for Dockview
function BeamFormPanel(_props: IDockviewPanelProps) {
  return <BeamForm />;
}

function ViewportPanel(_props: IDockviewPanelProps) {
  return <Viewport3D />;
}

function ResultsPanel2(_props: IDockviewPanelProps) {
  return <ResultsPanel />;
}

// Component registry for Dockview
const components = {
  beamForm: BeamFormPanel,
  viewport: ViewportPanel,
  results: ResultsPanel2,
};

export function WorkspaceLayout() {
  const apiRef = useRef<DockviewReadyEvent['api'] | null>(null);

  const onReady = useCallback((event: DockviewReadyEvent) => {
    apiRef.current = event.api;

    // Create left panel (form)
    event.api.addGroup();
    event.api.addPanel({
      id: 'beam-form',
      component: 'beamForm',
      title: 'Beam Design',
    });

    // Create center panel (3D viewport)
    event.api.addPanel({
      id: 'viewport-3d',
      component: 'viewport',
      title: '3D Viewport',
      position: { referencePanel: 'beam-form', direction: 'right' },
    });

    // Create right panel (results)
    event.api.addPanel({
      id: 'results',
      component: 'results',
      title: 'Results',
      position: { referencePanel: 'viewport-3d', direction: 'right' },
    });

    // Set proportions (roughly 1:2:1)
    const groups = event.api.groups;
    if (groups.length >= 3) {
      groups[0].api.setSize({ width: 280 });
      groups[2].api.setSize({ width: 320 });
    }
  }, []);

  return (
    <div className="workspace-layout">
      <DockviewReact
        className="dockview-container"
        components={components}
        onReady={onReady}
        watermarkComponent={() => null}
      />
    </div>
  );
}
