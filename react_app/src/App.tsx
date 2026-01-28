/**
 * Structural Engineering App
 *
 * React Router-based navigation with modern UI flow.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { TopBar } from './components/layout/TopBar';
import { HomePage } from './components/pages/HomePage';
import { ModeSelectPage } from './components/pages/ModeSelectPage';
import { DesignView } from './components/DesignView';
import { ImportView } from './components/ImportView';
import { BuildingEditorPage } from './components/pages/BuildingEditorPage';
import { BeamDetailPage } from './components/pages/BeamDetailPage';
import './App.css';

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
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/start" element={<ModeSelectPage />} />
            <Route path="/design" element={<DesignView />} />
            <Route path="/design/results" element={<BeamDetailPage />} />
            <Route path="/import" element={<ImportView />} />
            <Route path="/editor" element={<BuildingEditorPage />} />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
