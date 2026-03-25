/**
 * Structural Engineering App
 *
 * React Router-based navigation with modern UI flow.
 * Route components are lazy-loaded for code splitting.
 */
import { lazy, Suspense } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { TopBar } from './components/layout/TopBar';
import './App.css';

// Lazy-load route components for code splitting
const HomePage = lazy(() => import('./components/pages/HomePage').then(m => ({ default: m.HomePage })));
const ModeSelectPage = lazy(() => import('./components/pages/ModeSelectPage').then(m => ({ default: m.ModeSelectPage })));
const DesignView = lazy(() => import('./components/design/DesignView').then(m => ({ default: m.DesignView })));
const ImportView = lazy(() => import('./components/import/ImportView').then(m => ({ default: m.ImportView })));
const BuildingEditorPage = lazy(() => import('./components/pages/BuildingEditorPage').then(m => ({ default: m.BuildingEditorPage })));
const BeamDetailPage = lazy(() => import('./components/pages/BeamDetailPage').then(m => ({ default: m.BeamDetailPage })));
const DashboardPage = lazy(() => import('./components/pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const BatchDesignPage = lazy(() => import('./components/pages/BatchDesignPage'));

function RouteLoadingFallback() {
  return (
    <div className="flex items-center justify-center h-full w-full">
      <div className="animate-spin rounded-full h-8 w-8 border-2 border-zinc-600 border-t-blue-500" />
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

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="h-screen w-screen bg-zinc-950 overflow-hidden">
          <TopBar />
          <Suspense fallback={<RouteLoadingFallback />}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/start" element={<ModeSelectPage />} />
              <Route path="/design" element={<DesignView />} />
              <Route path="/design/results" element={<BeamDetailPage />} />
              <Route path="/import" element={<ImportView />} />
              <Route path="/editor" element={<BuildingEditorPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/batch" element={<BatchDesignPage />} />
            </Routes>
          </Suspense>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
