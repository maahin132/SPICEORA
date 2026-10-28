import { Leaf } from 'lucide-react'
import { Link, Route, Routes } from 'react-router-dom'

function FoundationScreen() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-6 py-8 sm:px-10">
      <header className="flex items-center gap-3">
        <span className="flex size-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-800">
          <Leaf aria-hidden="true" size={22} />
        </span>
        <span className="text-lg font-semibold tracking-tight text-stone-900">
          SPICEORA
        </span>
      </header>

      <section className="flex flex-1 flex-col items-center justify-center py-20 text-center">
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-emerald-800">
          Phase 0 · Foundation
        </p>
        <h1 className="max-w-2xl text-4xl font-semibold tracking-tight text-stone-950 sm:text-6xl">
          Your project foundation is ready.
        </h1>
        <p className="mt-6 max-w-xl text-lg leading-8 text-stone-600">
          The SPICEORA frontend is connected to its React and Vite development
          foundation. Product pages will begin in a later approved phase.
        </p>
        <Link
          className="mt-8 rounded-full border border-stone-300 px-5 py-2.5 text-sm font-medium text-stone-800 transition hover:border-emerald-700 hover:text-emerald-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-700"
          to="/"
        >
          Foundation home
        </Link>
      </section>

      <footer className="border-t border-stone-200 py-5 text-center text-sm text-stone-500">
        SPICEORA · Project bootstrap
      </footer>
    </main>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<FoundationScreen />} />
      <Route path="*" element={<FoundationScreen />} />
    </Routes>
  )
}

export default App
