import { Link } from "react-router-dom";
export default function ForbiddenPage() {
  return (
    <div className="mx-auto max-w-xl py-24 text-center">
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-coral">
        403
      </p>
      <h1 className="mt-4 font-display text-4xl font-bold">
        This area is restricted.
      </h1>
      <p className="mt-3 text-ink/55">
        Your role does not have access to this workspace.
      </p>
      <Link
        className="mt-8 inline-block bg-ink px-5 py-3 text-sm font-bold text-mist"
        to="/"
      >
        Return to overview
      </Link>
    </div>
  );
}
