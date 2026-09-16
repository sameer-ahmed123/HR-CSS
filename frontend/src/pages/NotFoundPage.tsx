import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <main className="grid min-h-screen place-items-center bg-surface px-6 py-12 text-ink">
      <div className="w-full max-w-2xl">
        <div className="flex items-center justify-between border-b border-ink/10 pb-5">
          <Link
            to="/"
            className="font-display text-2xl font-bold tracking-tight"
          >
            hr<span className="text-coral">.</span>css
          </Link>
          <span className="text-xs font-bold uppercase tracking-[0.18em] text-ink/40">
            Error 404
          </span>
        </div>
        <div className="py-16 sm:py-24">
          <p className="font-display text-[clamp(7rem,24vw,13rem)] font-bold leading-[0.8] tracking-[-0.08em] text-mint">
            404
          </p>
          <div className="mt-10 max-w-md">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-coral">
              Page not found
            </p>
            <h1 className="mt-4 font-display text-4xl font-bold tracking-tight sm:text-5xl">
              This page took a day off.
            </h1>
            <p className="mt-4 text-base leading-7 text-ink/55">
              The address may be outdated or the page may have moved somewhere
              else in your workspace.
            </p>
            <Link
              className="mt-8 inline-flex items-center gap-3 bg-ink px-5 py-3 text-sm font-bold text-mist transition hover:bg-ink/90"
              to="/"
            >
              <ArrowLeft size={17} />
              Back to overview
            </Link>
          </div>
        </div>
        <p className="border-t border-ink/10 pt-5 text-xs uppercase tracking-[0.16em] text-ink/35">
          Human resources / 2026
        </p>
      </div>
    </main>
  );
}
