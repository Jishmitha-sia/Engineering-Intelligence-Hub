import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Engineering Intelligence Hub
        </p>
        <h1 className="mt-4 max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          AI-powered knowledge for software teams
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-slate-600">
          Upload technical docs, search engineering knowledge, chat with your
          documentation, and analyze GitHub repositories in one platform.
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <Link
            href="/register"
            className="inline-flex h-10 items-center justify-center rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-800"
          >
            Get started
          </Link>
          <Link
            href="/login"
            className="inline-flex h-10 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-900 hover:bg-slate-50"
          >
            Sign in
          </Link>
        </div>
      </div>
    </main>
  );
}
