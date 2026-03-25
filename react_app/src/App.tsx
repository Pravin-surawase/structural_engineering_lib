/**
 * Structural Engineering App
 *
 * React Router-based navigation with modern UI flow.
 * Route components are lazy-loaded for code splitting.
 */
import { lazy, Suspense } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { TopBar } from './components/layout/TopBar';
import { FloatingDock } from './components/ui/FloatingDock';
import { useImportedBeamsStore } from './store/importedBeamsStore';
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

/** Floating dock nav — shown on all pages except home */
function AppDock() {
  const location = useLocation();
  const navigate = useNavigate();
  const { beams } = useImportedBeamsStore();

  if (location.pathname === '/') return null;

  const beamCount = beams.length;

  const items = [
    {
      id: 'design',
      label: 'Design',
      active: location.pathname === '/design' || location.pathname.startsWith('/design'),
      onClick: () => navigate('/design'),
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
            d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
            d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
      ),
    },
    {
      id: 'import',
      label: 'Import',
      active: location.pathname === '/import',
      onClick: () => navigate('/import'),
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
      ),
    },
    {
      id: 'editor',
      label: 'Editor',
      active: location.pathname === '/editor',
      badge: beamCount > 0 ? beamCount : undefined,
      onClick: () => navigate('/editor'),
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
    },
    {
      id: 'batch',
      label: 'Batch',
      active: location.pathname === '/batch',
      onClick: () => navigate('/batch'),
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
            d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
    {
      id: 'dashboard',
      label: 'Dashboard',
      active: location.pathname === '/dashboard',
      onClick: () => navigate('/dashboard'),
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
  ];

  return <FloatingDock items={items} position="bottom" />;
}

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
          <AppDock />
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
