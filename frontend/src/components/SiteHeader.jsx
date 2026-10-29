import { ArrowUpRight, Menu, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'

const navigation = [
  { href: '/products/', label: 'Products' },
  { href: '/#about', label: 'About SPICEORA' },
  { href: '/#process', label: 'The enquiry path' },
]

function NavigationLinks({ className, onNavigate }) {
  return (
    <nav aria-label="Main navigation" className={className}>
      {navigation.map((item) => (
        <Link to={item.href} key={item.href} onClick={onNavigate}>
          {item.label}
        </Link>
      ))}
    </nav>
  )
}

function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false)
  const menuButtonRef = useRef(null)

  useEffect(() => {
    if (!menuOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setMenuOpen(false)
        menuButtonRef.current?.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [menuOpen])

  function closeMenu() {
    setMenuOpen(false)
  }

  return (
    <header className="site-header" id="top">
      <div className="header-inner">
        <Link
          aria-label="SPICEORA home"
          className="wordmark"
          to="/"
          onClick={closeMenu}
        >
          SPICEORA<span aria-hidden="true">.</span>
        </Link>

        <NavigationLinks className="desktop-navigation" />

        <Link
          className="header-cta"
          to="/#enquiry"
          onClick={closeMenu}
        >
          Export enquiry
          <ArrowUpRight aria-hidden="true" size={16} strokeWidth={1.8} />
        </Link>

        <button
          aria-controls="mobile-navigation"
          aria-expanded={menuOpen}
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          className="menu-toggle"
          onClick={() => setMenuOpen((isOpen) => !isOpen)}
          ref={menuButtonRef}
          type="button"
        >
          {menuOpen ? (
            <X aria-hidden="true" size={22} />
          ) : (
            <Menu aria-hidden="true" size={22} />
          )}
        </button>
      </div>

      <div
        className="mobile-navigation-wrap"
        hidden={!menuOpen}
        id="mobile-navigation"
      >
        <NavigationLinks
          className="mobile-navigation"
          onNavigate={closeMenu}
        />
        <Link className="mobile-menu-cta" to="/#enquiry" onClick={closeMenu}>
          Start an export enquiry
          <ArrowUpRight aria-hidden="true" size={16} strokeWidth={1.8} />
        </Link>
      </div>
    </header>
  )
}

export default SiteHeader
