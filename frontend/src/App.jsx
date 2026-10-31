import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import SiteFooter from './components/SiteFooter.jsx'
import SiteHeader from './components/SiteHeader.jsx'
import {
  ForgotPasswordPage,
  LoginPage,
  NewPasswordPage,
  RecoveryVerificationPage,
  RegistrationPage,
  VerificationPage,
} from './pages/AuthPages.jsx'
import HomePage from './pages/HomePage.jsx'
import EnquiryPage from './pages/EnquiryPage.jsx'
import {
  OperationsCollectionPage,
  OperationsDashboard,
  ProtectedOperationsRoute,
} from './pages/OperationsPages.jsx'
import ProductDetailPage from './pages/ProductDetailPage.jsx'
import ProductsPage from './pages/ProductsPage.jsx'

function EnquiryCompatibilityRedirect() {
  const location = useLocation()
  return (
    <Navigate
      replace
      to={`/contact/${location.search}${location.hash}`}
    />
  )
}

function ContactCanonicalRedirect() {
  const location = useLocation()
  return <Navigate replace to={`/contact/${location.search}${location.hash}`} />
}

function App() {
  const location = useLocation()
  const inOperations = location.pathname.startsWith('/operations')
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      {!inOperations && <SiteHeader />}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/contact/" element={<EnquiryPage />} />
        <Route path="/contact" element={<ContactCanonicalRedirect />} />
        <Route path="/enquiry/" element={<EnquiryCompatibilityRedirect />} />
        <Route path="/enquiry" element={<EnquiryCompatibilityRedirect />} />
        <Route path="/products/" element={<ProductsPage />} />
        <Route path="/products/:slug/" element={<ProductDetailPage />} />
        <Route path="/register" element={<RegistrationPage />} />
        <Route path="/verify/email" element={<VerificationPage channel="email" />} />
        <Route path="/verify/mobile" element={<VerificationPage channel="mobile" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/forgot-password/verify" element={<RecoveryVerificationPage />} />
        <Route path="/new-password" element={<NewPasswordPage />} />
        <Route path="/operations/login" element={<LoginPage audience="staff" />} />
        <Route path="/operations" element={<ProtectedOperationsRoute />}>
          <Route index element={<OperationsDashboard />} />
          <Route path=":section" element={<OperationsCollectionPage />} />
        </Route>
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
      {!inOperations && <SiteFooter />}
    </>
  )
}

export default App
