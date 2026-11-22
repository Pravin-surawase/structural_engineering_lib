import { Settings } from 'lucide-react';
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { activeGlobalDestination, GLOBAL_DESTINATIONS } from '../../app/navigation';
import { PROJECT_OWNER, SOURCE_URL } from '../../app/projectIdentity';
import { SettingsPanel } from './SettingsPanel';

export function TopBar() {
  const { pathname } = useLocation();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  if (pathname === '/') return null;

  const activeDestination = activeGlobalDestination(pathname);
  return (
    <header className="fixed inset-x-0 top-0 z-40 h-14 border-b border-zinc-700 bg-zinc-950 text-white">
      <div className="mx-auto flex h-full max-w-screen-2xl items-center justify-between gap-3 px-4 sm:px-6">
        <Link to="/" className="flex shrink-0 items-center gap-2.5 rounded-sm">
          <img src={`${import.meta.env.BASE_URL}structlib.svg`} alt="" width="29" height="29" />
          <span className="leading-tight">
            <span className="block text-sm font-semibold tracking-tight">StructLib</span>
            <span className="block text-[11px] text-zinc-300">By {PROJECT_OWNER}</span>
          </span>
        </Link>

        <nav aria-label="Main navigation" className="hidden h-full items-stretch gap-4 md:flex">
          {GLOBAL_DESTINATIONS.map((destination) => {
            const isActive = activeDestination === destination.id;
            return (
              <Link
                key={destination.id}
                to={destination.path}
                aria-current={isActive ? 'page' : undefined}
                className={`inline-flex items-center border-b-2 px-2 text-sm font-medium transition-colors ${isActive ? 'border-blue-400 text-white' : 'border-transparent text-zinc-300 hover:text-white'}`}
              >
                {destination.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-1 sm:gap-2">
          <a href={SOURCE_URL} className="hidden min-h-10 items-center rounded-sm px-2 text-sm text-zinc-300 hover:text-white sm:inline-flex">Source</a>
          <button
            type="button"
            aria-label="Settings"
            aria-haspopup="dialog"
            onClick={() => setIsSettingsOpen(true)}
            className="inline-flex size-10 items-center justify-center rounded-sm text-zinc-300 hover:bg-zinc-800 hover:text-white"
          >
            <Settings size={18} aria-hidden="true" />
          </button>
        </div>
      </div>
      <SettingsPanel isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </header>
  );
}
