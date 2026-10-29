import { ArrowUpRight } from 'lucide-react'

function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="footer-main">
        <a aria-label="SPICEORA home" className="footer-wordmark" href="/">
          SPICEORA<span aria-hidden="true">.</span>
        </a>
        <p>From Indian Origins to Global Markets.</p>
        <a className="footer-contact-link" href="#enquiry">
          Enquiry information
          <ArrowUpRight aria-hidden="true" size={15} strokeWidth={1.8} />
        </a>
      </div>
      <div className="footer-bottom">
        <span>Indian spices · International trade</span>
        <a href="#top">Back to top ↑</a>
      </div>
    </footer>
  )
}

export default SiteFooter
