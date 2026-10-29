import { Route, Routes } from 'react-router-dom'
import SiteFooter from './components/SiteFooter.jsx'
import SiteHeader from './components/SiteHeader.jsx'
import HomePage from './pages/HomePage.jsx'

function App() {
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <SiteHeader />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="*"
          element={
            <main className="not-found-page" id="main-content">
              <p className="eyebrow">SPICEORA</p>
              <h1>That page is not here yet.</h1>
              <a className="text-link" href="/">
                Return to the homepage
              </a>
            </main>
          }
        />
      </Routes>
      <SiteFooter />
    </>
  )
}

export default App
