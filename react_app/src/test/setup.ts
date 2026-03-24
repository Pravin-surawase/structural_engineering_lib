import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Auto-cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock import.meta.env defaults
vi.stubEnv('VITE_API_URL', 'http://localhost:8000');
