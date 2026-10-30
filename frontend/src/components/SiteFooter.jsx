import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'

function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="footer-main">
        <Link aria-label="SPICEORA home" className="footer-wordmark" to="/">
          SPICEORA<span aria-hidden="true">.</span>
        </Link>
        <p>From Indian Origins to Global Markets.</p>
        <Link className="footer-contact-link" to="/enquiry/">
          Export enquiry
          <ArrowUpRight aria-hidden="true" size={15} strokeWidth={1.8} />
        </Link>
      </div>
      <div className="footer-bottom">
        <span>Indian spices · International trade</span>
        <Link to="/#top">Back to top ↑</Link>
      </div>
    </footer>
  )
}

export default SiteFooter
