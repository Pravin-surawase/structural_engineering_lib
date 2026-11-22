import { X } from 'lucide-react';
import { useEffect, useRef } from 'react';
import { version } from '../../../package.json';
import { API_BASE_URL } from '../../config';
import { ProjectCredits } from './ProjectCredits';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (isOpen && !dialog?.open) dialog?.showModal();
    if (!isOpen && dialog?.open) dialog.close();
  }, [isOpen]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="settings-title"
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
      className="fixed inset-y-0 right-0 left-auto m-0 h-dvh max-h-none w-full max-w-md border-l border-zinc-700 bg-zinc-950 p-0 text-white backdrop:bg-black/65"
    >
      {isOpen ? <div className="flex min-h-full flex-col">
        <header className="flex items-center justify-between border-b border-zinc-700 px-5 py-4 sm:px-6">
          <h2 id="settings-title" className="text-xl font-semibold tracking-tight">Settings</h2>
          <button type="button" onClick={onClose} aria-label="Close settings" className="inline-flex size-10 items-center justify-center rounded-sm text-zinc-300 hover:bg-zinc-800 hover:text-white">
            <X size={20} aria-hidden="true" />
          </button>
        </header>

        <div className="flex-1 space-y-7 px-5 py-6 sm:px-6">
          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-white">Workbench</h3>
            <dl className="divide-y divide-zinc-700 border-y border-zinc-700 text-sm">
              <div className="flex flex-wrap justify-between gap-2 py-3">
                <dt className="text-zinc-300">API endpoint</dt>
                <dd className="break-all font-mono text-blue-200">{API_BASE_URL || 'Same origin'}</dd>
              </div>
              <div className="flex justify-between gap-2 py-3">
                <dt className="text-zinc-300">Design standard</dt>
                <dd>IS 456:2000</dd>
              </div>
              <div className="flex justify-between gap-2 py-3">
                <dt className="text-zinc-300">Workbench version</dt>
                <dd className="font-mono">{version}</dd>
              </div>
            </dl>
          </section>
          <section className="space-y-3 text-zinc-300">
            <h3 className="text-sm font-semibold text-white">About StructLib</h3>
            <ProjectCredits />
          </section>
        </div>
      </div> : null}
    </dialog>
  );
}
