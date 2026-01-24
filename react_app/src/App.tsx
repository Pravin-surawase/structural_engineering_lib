/**
 * Structural Engineering App
 *
 * React Three Fiber + Dockview based IDE for beam design.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WorkspaceLayout } from './components/WorkspaceLayout';
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
      <WorkspaceLayout />
    </QueryClientProvider>
  );
}

export default App;
