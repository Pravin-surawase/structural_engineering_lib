import { ArrowDownRight, ArrowRight, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PROJECT_OWNER, PYTHON_GUIDE_URL, SOURCE_URL } from '../../app/projectIdentity';
import { CrossSectionView } from '../design/CrossSectionView';
import { ProjectCredits } from '../layout/ProjectCredits';

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="h-full overflow-y-auto bg-paper text-ink [--focus-color:var(--color-cobalt)] [color-scheme:light]">
      <div className="mx-auto flex min-h-full max-w-7xl flex-col px-5 sm:px-8 lg:px-12">
        <header className="flex min-h-18 items-center justify-between gap-4 border-b border-ink/15 py-3">
          <div className="flex items-center gap-3">
            <img src={`${import.meta.env.BASE_URL}structlib.svg`} alt="" width="36" height="36" />
            <div>
              <p className="font-semibold tracking-tight">StructLib</p>
              <p className="text-xs text-ink/75">By {PROJECT_OWNER}</p>
            </div>
          </div>
          <a href={SOURCE_URL} className="inline-flex min-h-10 items-center gap-1.5 rounded-sm px-2 text-sm font-semibold text-cobalt hover:underline">
            Source <ArrowUpRight size={15} aria-hidden="true" />
          </a>
        </header>

        <section className="grid items-center gap-9 py-9 md:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] md:gap-8 md:py-14 lg:gap-16">
          <div className="min-w-0">
            <p className="font-mono text-xs font-semibold tracking-widest text-cobalt uppercase">Open-source Python library</p>
            <h1 className="mt-4 max-w-2xl text-[clamp(2.5rem,5.2vw,4.75rem)] leading-[0.98] font-semibold tracking-[-0.06em]">
              Reinforced concrete, made inspectable.
            </h1>
            <p className="mt-5 max-w-xl text-base leading-relaxed text-ink/80 sm:text-lg">
              Try a supported IS 456 check in the browser. Inspect the governing result, then use the same library in your own Python code.
            </p>
            <div className="mt-7 flex flex-wrap items-center gap-3">
              <button type="button" onClick={() => navigate('/workbench')} className="inline-flex min-h-11 items-center gap-3 rounded-sm bg-cobalt px-4 text-sm font-semibold text-white transition-colors hover:bg-cobalt-hover">
                Open workbench <ArrowRight size={16} aria-hidden="true" />
              </button>
              <a href={PYTHON_GUIDE_URL} className="inline-flex min-h-11 items-center gap-2 rounded-sm border border-ink/25 px-4 text-sm font-semibold text-ink hover:bg-white">
                Use the Python library <ArrowUpRight size={16} aria-hidden="true" />
              </a>
            </div>
            <p className="mt-5 max-w-lg text-sm leading-relaxed text-ink/75">Engineering use requires review by a qualified structural engineer.</p>
          </div>

          <figure className="min-w-0 border border-zinc-700 bg-ink text-white">
            <div className="flex flex-wrap justify-between gap-1 border-b border-white/15 px-4 py-3 font-mono text-xs text-zinc-300 sm:px-5">
              <span>Rectangular beam</span>
              <span>Section view · IS 456:2000</span>
            </div>
            <div className="bg-[linear-gradient(#ffffff13_1px,transparent_1px),linear-gradient(90deg,#ffffff13_1px,transparent_1px)] bg-size-[24px_24px] py-2">
              <div aria-hidden="true">
                <CrossSectionView width={300} depth={500} cover={40} astRequired={0} barDia={16} barCount={3} topBarCount={2} className="[&>svg]:h-56 [&>svg]:w-auto sm:[&>svg]:h-70" />
              </div>
            </div>
            <figcaption className="flex flex-wrap items-center justify-between gap-1 border-t border-white/15 px-4 py-3 text-xs sm:px-5">
              <span className="font-mono text-zinc-200">300 × 500 mm</span>
              <span className="text-zinc-300">Illustrative reinforcement layout</span>
            </figcaption>
          </figure>
        </section>

        <section className="grid border-y border-ink/15 sm:grid-cols-2" aria-label="Workbench entry points">
          <button type="button" onClick={() => navigate('/workbench/quick')} className="flex min-h-22 items-center justify-between gap-5 px-2 py-3 text-left hover:bg-white/70 sm:pr-6">
            <span className="space-y-1"><span className="block font-semibold">Quick beam</span><span className="block text-sm text-ink/75">Run a single calculation with editable inputs.</span></span>
            <ArrowDownRight className="shrink-0 text-cobalt" size={20} aria-hidden="true" />
          </button>
          <button type="button" onClick={() => navigate('/workbench/projects/new')} className="flex min-h-22 items-center justify-between gap-5 border-t border-ink/15 px-2 py-3 text-left hover:bg-white/70 sm:border-t-0 sm:border-l sm:pl-6">
            <span className="space-y-1"><span className="block font-semibold">New project</span><span className="block text-sm text-ink/75">Import beam data and review members together.</span></span>
            <ArrowDownRight className="shrink-0 text-cobalt" size={20} aria-hidden="true" />
          </button>
        </section>

        <footer className="mt-auto py-6 text-ink/80">
          <ProjectCredits />
        </footer>
      </div>
    </div>
  );
}
