/** Restrained landing page for the structural workbench. */
import { ArrowRight, Boxes, PanelsTopLeft, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const secondaryActions = [
  {
    label: 'Quick beam',
    description: 'Run one focused IS 456 beam design.',
    path: '/workbench/quick',
    icon: PanelsTopLeft,
  },
  {
    label: 'New project',
    description: 'Import and review a building project.',
    path: '/workbench/projects/new',
    icon: Boxes,
  },
] as const;

export function HomePage() {
  const navigate = useNavigate();

  return (
    <main className="min-h-dvh overflow-y-auto bg-zinc-950 text-zinc-100">
      <div className="mx-auto flex min-h-dvh w-full max-w-6xl flex-col px-5 py-6 sm:px-8 lg:px-12">
        <header className="flex items-center justify-between border-b border-white/10 pb-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-sm font-bold text-white">
              SL
            </div>
            <div>
              <p className="text-sm font-semibold text-white">StructLib</p>
              <p className="text-xs text-zinc-500">IS 456 structural workbench</p>
            </div>
          </div>
          <span className="rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs font-medium text-amber-200">
            Alpha
          </span>
        </header>

        <section className="grid flex-1 items-center gap-10 py-12 lg:grid-cols-[minmax(0,1.2fr)_minmax(20rem,0.8fr)]">
          <div className="max-w-2xl">
            <p className="mb-4 text-sm font-medium text-blue-300">Design, review, resolve, export</p>
            <h1 className="text-balance text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
              Reinforced-concrete design in one clear workflow.
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-zinc-400 sm:text-lg">
              Move from focused beam checks to imported-project review without
              learning a collection of disconnected screens.
            </p>

            <button
              type="button"
              onClick={() => navigate('/workbench')}
              className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-950/40 transition-colors hover:bg-blue-500 sm:w-auto"
            >
              Open workbench
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>

          <div className="space-y-3" aria-label="Workbench entry points">
            {secondaryActions.map(({ label, description, path, icon: Icon }) => (
              <button
                key={path}
                type="button"
                onClick={() => navigate(path)}
                className="group flex w-full items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left transition-colors hover:border-white/20 hover:bg-white/[0.06]"
              >
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/[0.06] text-zinc-300 group-hover:text-white">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-sm font-semibold text-white">{label}</span>
                  <span className="mt-0.5 block text-xs leading-5 text-zinc-500">{description}</span>
                </span>
                <ArrowRight className="h-4 w-4 text-zinc-600 group-hover:text-zinc-300" aria-hidden="true" />
              </button>
            ))}

            <div className="flex gap-3 rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.06] p-4">
              <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-300" aria-hidden="true" />
              <p className="text-xs leading-5 text-emerald-100/80">
                Results identify supported cases and evidence status. Professional
                engineering review remains required for project use.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
