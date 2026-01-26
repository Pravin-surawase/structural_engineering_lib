/**
 * Structural Engineering App
 *
 * Modern Gen Z-style UI with BentoGrid layout and 3D visualization.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ModernAppLayout } from './components/layout/ModernAppLayout';
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
      <ModernAppLayout />
    </QueryClientProvider>
  );
}

export default App;
