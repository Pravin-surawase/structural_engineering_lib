/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_WS_URL: string;
  readonly VITE_WORKFLOW_RUNNER_ENABLED?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
