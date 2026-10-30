import { Link, Route, Routes } from 'react-router-dom'
import SiteFooter from './components/SiteFooter.jsx'
import SiteHeader from './components/SiteHeader.jsx'
import HomePage from './pages/HomePage.jsx'
import EnquiryPage from './pages/EnquiryPage.jsx'
import ProductDetailPage from './pages/ProductDetailPage.jsx'
import ProductsPage from './pages/ProductsPage.jsx'

function App() {
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <SiteHeader />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/enquiry/" element={<EnquiryPage />} />
        <Route path="/products/" element={<ProductsPage />} />
        <Route path="/products/:slug/" element={<ProductDetailPage />} />
        <Route
          path="*"
          element={
            <main className="not-found-page" id="main-content">
              <p className="eyebrow">SPICEORA</p>
              <h1>That page is not here yet.</h1>
              <Link className="text-link" to="/">
                Return to the homepage
              </Link>
            </main>
          }
        />
      </Routes>
      <SiteFooter />
    </>
  )
}

export default App
