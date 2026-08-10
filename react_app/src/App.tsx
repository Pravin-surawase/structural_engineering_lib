/**
 * Structural Engineering App
 *
 * React Router-based navigation with modern UI flow.
 * Route components are lazy-loaded for code splitting.
 */
import { lazy, Suspense } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { Boxes, PanelsTopLeft } from 'lucide-react';
import { activeGlobalDestination, GLOBAL_DESTINATIONS } from './app/navigation';
import { WorkspacePersistenceBridge } from './workspace/WorkspacePersistenceBridge';
import { TopBar } from './components/layout/TopBar';
import { FloatingDock } from './components/ui/FloatingDock';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import { ToastContainer } from './components/ui/Toast';
import { WORKFLOW_RUNNER_ENABLED } from './features/automation/config';

// Lazy-load route components for code splitting
const HomePage = lazy(() => import('./components/pages/HomePage').then(m => ({ default: m.HomePage })));
const HubPage = lazy(() => import('./components/pages/HubPage').then(m => ({ default: m.HubPage })));
const WorkbenchHomePage = lazy(() => import('./components/pages/WorkbenchHomePage').then(m => ({ default: m.WorkbenchHomePage })));
const DesignView = lazy(() => import('./components/design/DesignView').then(m => ({ default: m.DesignView })));
const CatalogDesignView = lazy(() => import('./features/workflows/CatalogDesignView').then(m => ({ default: m.CatalogDesignView })));
const ImportView = lazy(() => import('./components/import/ImportView').then(m => ({ default: m.ImportView })));
const BuildingEditorPage = lazy(() => import('./components/pages/BuildingEditorPage').then(m => ({ default: m.BuildingEditorPage })));
const BeamDetailPage = lazy(() => import('./components/pages/BeamDetailPage').then(m => ({ default: m.BeamDetailPage })));
const DashboardPage = lazy(() => import('./components/pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const BatchDesignPage = lazy(() => import('./components/pages/BatchDesignPage'));
const WorkflowComposerPage = lazy(() => import('./features/automation/WorkflowComposerPage').then(m => ({ default: m.WorkflowComposerPage })));

function RouteLoadingFallback() {
  return (
    <div
      className="flex items-center justify-center h-full w-full"
      role="status"
      aria-live="polite"
    >
      <div className="animate-spin rounded-full h-8 w-8 border-2 border-zinc-600 border-t-blue-500" />
      <span className="sr-only">Loading page content...</span>
    </div>
  );
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

/** Floating dock nav — shown on all pages except home */
function AppDock() {
  const location = useLocation();
  const navigate = useNavigate();

  if (location.pathname === '/') return null;

  const activeId = activeGlobalDestination(location.pathname);
  const icons = {
    workbench: <PanelsTopLeft className="h-5 w-5" aria-hidden="true" />,
    projects: <Boxes className="h-5 w-5" aria-hidden="true" />,
  };
  const items = GLOBAL_DESTINATIONS.map((destination) => ({
    ...destination,
    active: activeId === destination.id,
    onClick: () => navigate(destination.path),
    icon: icons[destination.id],
  }));

  return (
    <div className="md:hidden">
      <FloatingDock items={items} position="bottom" />
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <WorkspacePersistenceBridge />
          <div className="h-screen w-screen bg-zinc-950 flex flex-col">
            <a
              href="#main-content"
              className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-md focus:shadow-lg"
            >
              Skip to main content
            </a>
            <TopBar />
            <main id="main-content" className="flex-1 overflow-hidden">
              <Suspense fallback={<RouteLoadingFallback />}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/start" element={<HubPage />} />
                  <Route path="/workbench" element={<WorkbenchHomePage />} />
                  <Route path="/workbench/quick" element={<DesignView />} />
                  <Route path="/workbench/quick/catalog" element={<CatalogDesignView />} />
                  <Route path="/workbench/quick/manual" element={<DesignView />} />
                  <Route path="/workbench/projects" element={<WorkbenchHomePage initialView="projects" />} />
                  <Route path="/workbench/projects/new" element={<ImportView />} />
                  <Route path="/design" element={<DesignView />} />
                  <Route path="/design/results" element={<BeamDetailPage />} />
                  <Route path="/import" element={<ImportView />} />
                  <Route path="/editor" element={<BuildingEditorPage />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/batch" element={<BatchDesignPage />} />
                  {WORKFLOW_RUNNER_ENABLED ? <Route path="/workbench/automation" element={<WorkflowComposerPage />} /> : null}
                </Routes>
              </Suspense>
            </main>
            <AppDock />
            <ToastContainer />
          </div>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
