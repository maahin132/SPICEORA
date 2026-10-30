import { ArrowRight, ArrowUpRight } from 'lucide-react'
import { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'

import { getProducts } from '../api/catalog.js'
import CatalogFeedback from '../components/CatalogFeedback.jsx'
import ProductCard from '../components/ProductCard.jsx'
import { useCatalogRequest } from '../hooks/useCatalogRequest.js'
import usePageMetadata from '../hooks/usePageMetadata.js'

const enquirySteps = [
  {
    number: '01',
    title: 'Share your interest',
    description:
      'Tell us which spice category or product you would like to discuss.',
  },
  {
    number: '02',
    title: 'Add useful context',
    description:
      'A destination market or a little background can help frame the conversation.',
  },
  {
    number: '03',
    title: 'Agree what comes next',
    description:
      'Any next step depends on the details and a confirmed conversation with the team.',
  },
]

function EditorialImage({
  alt,
  className,
  objectPosition,
  loading = 'lazy',
}) {
  const [imageFailed, setImageFailed] = useState(false)

  return (
    <div
      aria-label={imageFailed && alt ? alt : undefined}
      className={`image-frame ${className}${imageFailed ? ' image-frame--fallback' : ''}`}
      role={imageFailed && alt ? 'img' : undefined}
    >
      {!imageFailed && (
        <img
          alt={alt}
          className="spice-image"
          decoding="async"
          fetchPriority={loading === 'eager' ? 'high' : 'auto'}
          loading={loading}
          onError={() => setImageFailed(true)}
          src="/images/spice-study.jpg"
          style={{ objectPosition }}
        />
      )}
      {imageFailed && <span className="image-fallback-mark" aria-hidden="true" />}
    </div>
  )
}

function SectionHeading({ eyebrow, title, description, id }) {
  return (
    <div className="section-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h2 id={id}>{title}</h2>
      {description && <p className="section-description">{description}</p>}
    </div>
  )
}

function HomeProductPreview() {
  const request = useCallback(() => getProducts({ page: '1' }), [])
  const state = useCatalogRequest(request)

  if (state.status !== 'success') {
    return (
      <CatalogFeedback
        error={state.error}
        onRetry={state.retry}
        status={state.status}
      />
    )
  }

  if (state.data.results.length === 0) {
    return (
      <div className="catalog-empty catalog-empty--compact">
        <p className="eyebrow">Catalogue status</p>
        <p>No products have been published yet.</p>
        <Link className="text-link" to="/enquiry/">
          Make a product enquiry
          <ArrowUpRight aria-hidden="true" size={16} strokeWidth={1.8} />
        </Link>
      </div>
    )
  }

  return (
    <div className="products-grid products-grid--preview">
      {state.data.results.slice(0, 3).map((product) => (
        <ProductCard key={product.slug} product={product} />
      ))}
    </div>
  )
}

function HomePage() {
  usePageMetadata(
    'SPICEORA | Indian Spice Categories',
    "Explore SPICEORA's Indian spice categories and share a product enquiry with the business.",
  )

  return (
    <main id="main-content">
      <section aria-labelledby="hero-title" className="hero-section">
        <div className="hero-copy">
          <p className="eyebrow hero-eyebrow">
            Indian spice categories · International trade
          </p>
          <h1 id="hero-title">
            From Indian Origins
            <br />
            <em>to Global Markets.</em>
          </h1>
          <p className="hero-intro">
            A considered introduction to SPICEORA and the spice categories at
            the heart of its export focus.
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" to="/enquiry/">
              Discuss an export enquiry
              <ArrowUpRight aria-hidden="true" size={17} strokeWidth={1.8} />
            </Link>
            <Link className="button button-text" to="/products/">
              Explore published products
              <ArrowRight aria-hidden="true" size={16} strokeWidth={1.8} />
            </Link>
          </div>
          <p className="hero-note">
            Product availability and details are confirmed directly with the
            company.
          </p>
        </div>

        <figure className="hero-visual">
          <EditorialImage
            alt="An overhead still life of assorted spices, seeds, turmeric and dried red chillies on a pale wooden surface."
            className="hero-image-frame"
            loading="eager"
            objectPosition="center"
          />
          <figcaption className="image-caption">
            An editorial study of spice, seed and colour.
          </figcaption>
        </figure>
      </section>

      <section
        aria-labelledby="collection-title"
        className="collection-section section-shell"
        id="collection"
      >
        <div className="collection-intro">
          <SectionHeading
            description="Only products reviewed and published by the business appear in this catalogue."
            eyebrow="Published products"
            id="collection-title"
            title="Explore the catalogue."
          />
          <Link className="text-link collection-link" to="/products/">
            Browse products
            <ArrowRight aria-hidden="true" size={16} strokeWidth={1.8} />
          </Link>
        </div>

        <HomeProductPreview />
      </section>

      <section
        aria-labelledby="about-title"
        className="about-section"
        id="about"
      >
        <div className="about-rule" />
        <div className="about-content">
          <p className="eyebrow">The SPICEORA perspective</p>
          <h2 id="about-title">
            Indian spices,
            <br />
            <em>introduced to the world.</em>
          </h2>
          <div className="about-copy">
            <p>
              SPICEORA is an Indian spice-export business for buyers looking to
              begin a conversation around familiar ingredients and international
              trade.
            </p>
            <p>
              The story, sourcing details and product information will be
              shared here as they are confirmed by the company—never assumed.
            </p>
            <Link className="text-link" to="/enquiry/">
              Start a conversation
              <ArrowRight aria-hidden="true" size={16} strokeWidth={1.8} />
            </Link>
          </div>
        </div>
        <p aria-hidden="true" className="about-index">
          01 / SPICEORA
        </p>
      </section>

      <section
        aria-labelledby="process-title"
        className="process-section section-shell"
        id="process"
      >
        <div className="process-heading">
          <SectionHeading
            description="A general way to begin a B2B conversation—not a confirmed description of SPICEORA’s operating process."
            eyebrow="A proposed enquiry path"
            id="process-title"
            title="Begin with a conversation."
          />
          <span aria-hidden="true" className="process-stamp">
            PROPOSED
            <br />
            NOT A SERVICE PROMISE
          </span>
        </div>
        <ol className="process-list">
          {enquirySteps.map((step) => (
            <li className="process-step" key={step.number}>
              <span className="step-number">{step.number}</span>
              <div>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section
        aria-labelledby="enquiry-title"
        className="enquiry-section"
        id="enquiry"
      >
        <div className="enquiry-inner">
          <p className="eyebrow enquiry-eyebrow">For international buyers</p>
          <h2 id="enquiry-title">
            Have a spice in mind?
            <br />
            <em>Let’s begin there.</em>
          </h2>
          <p className="enquiry-copy">
            Share the products or categories you are interested in. No response
            time or commercial terms are promised.
          </p>
          <Link className="button button-primary" to="/enquiry/">
            Open the enquiry form
            <ArrowUpRight aria-hidden="true" size={17} strokeWidth={1.8} />
          </Link>
        </div>
        <span aria-hidden="true" className="enquiry-side-note">
          SPICEORA
          <br />
          INDIAN SPICE EXPORT
        </span>
      </section>
    </main>
  )
}

export default HomePage
