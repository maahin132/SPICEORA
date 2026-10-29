import { ArrowDown, ArrowRight, ArrowUpRight } from 'lucide-react'
import { useState } from 'react'

const spiceCategories = [
  { name: 'Cumin', position: '52% 39%', tone: 'sand' },
  { name: 'Fennel', position: '64% 25%', tone: 'sage' },
  { name: 'Red chilli', position: '78% 12%', tone: 'rust' },
  { name: 'Turmeric', position: '76% 57%', tone: 'ochre' },
  { name: 'Coriander', position: '39% 39%', tone: 'olive' },
  { name: 'Dhana-jeera', position: '60% 48%', tone: 'clay' },
]

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

function HomePage() {
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
            <a className="button button-primary" href="#enquiry">
              Discuss an export enquiry
              <ArrowUpRight aria-hidden="true" size={17} strokeWidth={1.8} />
            </a>
            <a className="button button-text" href="#collection">
              Explore the categories
              <ArrowDown aria-hidden="true" size={16} strokeWidth={1.8} />
            </a>
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
            description="The categories below are part of the SPICEORA brief. Product availability and public specifications are still to be confirmed."
            eyebrow="A considered collection"
            id="collection-title"
            title="Six familiar notes."
          />
          <a className="text-link collection-link" href="#enquiry">
            Ask about a category
            <ArrowRight aria-hidden="true" size={16} strokeWidth={1.8} />
          </a>
        </div>

        <div className="category-grid">
          {spiceCategories.map((spice, index) => (
            <a
              aria-label={`Ask about ${spice.name}`}
              className={`category-item category-item--${spice.tone}`}
              href="#enquiry"
              key={spice.name}
            >
              <div className="category-image-wrap">
                <EditorialImage
                  alt=""
                  className="category-image-frame"
                  objectPosition={spice.position}
                />
                <span aria-hidden="true" className="category-number">
                  0{index + 1}
                </span>
                <span aria-hidden="true" className="category-arrow">
                  <ArrowUpRight size={17} strokeWidth={1.8} />
                </span>
              </div>
              <div className="category-label">
                <h3>{spice.name}</h3>
                <span>Enquire</span>
              </div>
            </a>
          ))}
        </div>
        <p className="collection-caption">
          Illustrative spice photography; images do not represent confirmed
          inventory or product specifications.
        </p>
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
            <a className="text-link" href="#enquiry">
              Start a conversation
              <ArrowRight aria-hidden="true" size={16} strokeWidth={1.8} />
            </a>
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
            Contact details are awaiting owner confirmation. This preview does
            not accept or send enquiries.
          </p>
          <span className="contact-placeholder">
            Enquiry channel to be confirmed
          </span>
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
