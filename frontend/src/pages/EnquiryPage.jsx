import { ArrowLeft, ArrowUpRight } from 'lucide-react'
import { useCallback, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import {
  EnquiryApiError,
  getCategories,
  getProduct,
  submitEnquiry,
} from '../api/catalog.js'
import CatalogFeedback from '../components/CatalogFeedback.jsx'
import { useCatalogRequest } from '../hooks/useCatalogRequest.js'
import usePageMetadata from '../hooks/usePageMetadata.js'

function fieldError(errors, name) {
  const messages = errors[name]
  return Array.isArray(messages) ? messages.join(' ') : ''
}

function EnquiryPage() {
  usePageMetadata(
    'Export Enquiry | SPICEORA',
    'Share a product or category enquiry with SPICEORA using the export enquiry form.',
  )
  const [searchParams] = useSearchParams()
  const productSlug = searchParams.get('product') || ''
  const categorySlug = searchParams.get('category') || ''
  const categoriesRequest = useCallback(() => getCategories(), [])
  const productRequest = useCallback(
    () => (productSlug ? getProduct(productSlug) : Promise.resolve(null)),
    [productSlug],
  )
  const categoriesState = useCatalogRequest(categoriesRequest)
  const productState = useCatalogRequest(productRequest)
  const [categoryChoice, setCategoryChoice] = useState(categorySlug)
  const [productDismissed, setProductDismissed] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [fieldErrors, setFieldErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [reference, setReference] = useState('')
  const submitLock = useRef(false)

  const selectedProduct =
    productState.status === 'success' && !productDismissed
      ? productState.data
      : null
  const hasCategory = categoriesState.data?.some(
    (item) => item.slug === categoryChoice,
  )
  const category =
    selectedProduct?.category.slug ||
    (categoriesState.status === 'success' && categoryChoice && !hasCategory
      ? ''
      : categoryChoice)

  async function handleSubmit(event) {
    event.preventDefault()
    if (
      submitLock.current ||
      categoriesState.status !== 'success' ||
      !category
    ) {
      return
    }

    const formData = new FormData(event.currentTarget)
    const payload = {
      full_name: formData.get('full_name'),
      company_name: formData.get('company_name'),
      email: formData.get('email'),
      phone: formData.get('phone'),
      country: formData.get('country'),
      quantity: formData.get('quantity') || null,
      quantity_unit: formData.get('quantity_unit'),
      message: formData.get('message'),
      ...(selectedProduct
        ? { product_slug: selectedProduct.slug }
        : { category_slug: category }),
    }

    submitLock.current = true
    setIsSubmitting(true)
    setFieldErrors({})
    setSubmitError('')
    try {
      const result = await submitEnquiry(payload)
      setReference(result.reference)
    } catch (error) {
      if (error instanceof EnquiryApiError) {
        setFieldErrors(error.errors)
        setSubmitError(error.message)
      } else {
        setSubmitError('We could not submit your enquiry. Please try again.')
      }
    } finally {
      submitLock.current = false
      setIsSubmitting(false)
    }
  }

  const categoryError =
    fieldError(fieldErrors, 'category_slug') || fieldError(fieldErrors, 'product_slug')

  return (
    <main className="catalog-page enquiry-page" id="main-content">
      <div className="enquiry-intro">
        <p className="eyebrow">SPICEORA · Export enquiry</p>
        <h1>Start a business conversation.</h1>
        <p>
          Share a little about your request. Fields marked required help us
          understand how to route your enquiry.
        </p>
        <Link className="text-link" to="/products/">
          <ArrowLeft aria-hidden="true" size={16} />
          Browse published products
        </Link>
      </div>

      {reference ? (
        <section
          aria-labelledby="enquiry-success-title"
          aria-live="polite"
          className="enquiry-success"
        >
          <p className="eyebrow">Enquiry received</p>
          <h2 id="enquiry-success-title">Thank you for getting in touch.</h2>
          <p>
            Your enquiry has been recorded. This confirmation does not indicate
            that an email notification was sent or promise a response time.
          </p>
          <p className="enquiry-reference">
            Reference <span>{reference}</span>
          </p>
          <Link className="text-link" to="/">
            Return to the homepage
            <ArrowUpRight aria-hidden="true" size={16} />
          </Link>
        </section>
      ) : (
        <form className="enquiry-form" onSubmit={handleSubmit}>
          {submitError && (
            <p aria-live="assertive" className="enquiry-form-error" role="alert">
              {submitError}
            </p>
          )}

          {categoriesState.status !== 'success' ? (
            <CatalogFeedback
              error={categoriesState.error}
              onRetry={categoriesState.retry}
              status={categoriesState.status}
            />
          ) : productSlug && productState.status === 'loading' ? (
            <CatalogFeedback status="loading" />
          ) : (
            <>
              {productState.status === 'error' && (
                <p className="enquiry-form-notice" role="status">
                  The selected product is no longer available. Choose an active
                  category to continue.
                </p>
              )}

              {selectedProduct && (
                <div className="enquiry-product-selection">
                  <span className="eyebrow">Product of interest</span>
                  <strong>{selectedProduct.name}</strong>
                  <span>{selectedProduct.category.name}</span>
                  <button onClick={() => setProductDismissed(true)} type="button">
                    Remove product selection
                  </button>
                </div>
              )}

              <div className="enquiry-fields">
                <div className="enquiry-field">
                  <label htmlFor="full-name">Full name <span>(required)</span></label>
                  <input
                    autoComplete="name"
                    id="full-name"
                    name="full_name"
                    required
                    maxLength={120}
                    aria-describedby={fieldErrors.full_name ? 'full-name-error' : undefined}
                    aria-invalid={Boolean(fieldErrors.full_name)}
                  />
                  {fieldErrors.full_name && (
                    <span className="enquiry-field-error" id="full-name-error">
                      {fieldError(fieldErrors, 'full_name')}
                    </span>
                  )}
                </div>

                <div className="enquiry-field">
                  <label htmlFor="company-name">Company name <span>(optional)</span></label>
                  <input
                    autoComplete="organization"
                    id="company-name"
                    maxLength={160}
                    name="company_name"
                    aria-describedby={
                      fieldErrors.company_name ? 'company-name-error' : undefined
                    }
                    aria-invalid={Boolean(fieldErrors.company_name)}
                  />
                  {fieldErrors.company_name && (
                    <span className="enquiry-field-error" id="company-name-error">
                      {fieldError(fieldErrors, 'company_name')}
                    </span>
                  )}
                </div>

                <div className="enquiry-field">
                  <label htmlFor="business-email">Business email <span>(required)</span></label>
                  <input
                    autoComplete="email"
                    id="business-email"
                    maxLength={254}
                    name="email"
                    required
                    type="email"
                    aria-describedby={fieldErrors.email ? 'business-email-error' : undefined}
                    aria-invalid={Boolean(fieldErrors.email)}
                  />
                  {fieldErrors.email && (
                    <span className="enquiry-field-error" id="business-email-error">
                      {fieldError(fieldErrors, 'email')}
                    </span>
                  )}
                </div>

                <div className="enquiry-field">
                  <label htmlFor="phone">Phone number <span>(optional)</span></label>
                  <input
                    autoComplete="tel"
                    id="phone"
                    maxLength={40}
                    name="phone"
                    type="tel"
                    aria-describedby={fieldErrors.phone ? 'phone-error' : undefined}
                    aria-invalid={Boolean(fieldErrors.phone)}
                  />
                  {fieldErrors.phone && (
                    <span className="enquiry-field-error" id="phone-error">
                      {fieldError(fieldErrors, 'phone')}
                    </span>
                  )}
                </div>

                <div className="enquiry-field">
                  <label htmlFor="country">Country <span>(required)</span></label>
                  <input
                    autoComplete="country-name"
                    id="country"
                    maxLength={100}
                    name="country"
                    required
                    aria-describedby={fieldErrors.country ? 'country-error' : undefined}
                    aria-invalid={Boolean(fieldErrors.country)}
                  />
                  {fieldErrors.country && (
                    <span className="enquiry-field-error" id="country-error">
                      {fieldError(fieldErrors, 'country')}
                    </span>
                  )}
                </div>

                <div className="enquiry-field">
                  <label htmlFor="interest-category">
                    Product or category of interest <span>(required)</span>
                  </label>
                  <select
                    id="interest-category"
                    name="category_slug"
                    required
                    value={category}
                    onChange={(event) => {
                      setCategoryChoice(event.target.value)
                      setProductDismissed(true)
                    }}
                    aria-describedby={categoryError ? 'interest-error' : undefined}
                    aria-invalid={Boolean(categoryError)}
                  >
                    <option value="">Select a category</option>
                    {categoriesState.data.map((item) => (
                      <option key={item.slug} value={item.slug}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                  {categoryError && (
                    <span className="enquiry-field-error" id="interest-error">
                      {categoryError}
                    </span>
                  )}
                </div>

                <div className="enquiry-field enquiry-field--quantity">
                  <label htmlFor="quantity">Estimated required quantity <span>(required)</span></label>
                  <input
                    id="quantity"
                    inputMode="decimal"
                    max="9999999999999.999"
                    min="0.001"
                    name="quantity"
                    required
                    placeholder="For example, 500"
                    step="0.001"
                    type="number"
                    aria-describedby={fieldErrors.quantity ? 'quantity-error' : undefined}
                    aria-invalid={Boolean(fieldErrors.quantity)}
                  />
                  {fieldErrors.quantity && (
                    <span className="enquiry-field-error" id="quantity-error">
                      {fieldError(fieldErrors, 'quantity')}
                    </span>
                  )}
                </div>

                <div className="enquiry-field enquiry-field--quantity">
                  <label htmlFor="quantity-unit">Quantity unit <span>(required)</span></label>
                  <select
                    id="quantity-unit"
                    name="quantity_unit"
                    defaultValue=""
                    required
                    aria-describedby={
                      fieldErrors.quantity_unit ? 'quantity-unit-error' : undefined
                    }
                    aria-invalid={Boolean(fieldErrors.quantity_unit)}
                  >
                    <option value="">Select a unit</option>
                    <option value="kg">Kilograms</option>
                    <option value="metric_tonne">Metric tonnes</option>
                  </select>
                  {fieldErrors.quantity_unit && (
                    <span className="enquiry-field-error" id="quantity-unit-error">
                      {fieldError(fieldErrors, 'quantity_unit')}
                    </span>
                  )}
                </div>

                <div className="enquiry-field enquiry-field--message">
                  <label htmlFor="message">Additional message <span>(optional)</span></label>
                  <textarea
                    id="message"
                    maxLength={5000}
                    name="message"
                    rows={6}
                    aria-describedby={fieldErrors.message ? 'message-error' : undefined}
                    aria-invalid={Boolean(fieldErrors.message)}
                  />
                  {fieldErrors.message && (
                    <span className="enquiry-field-error" id="message-error">
                      {fieldError(fieldErrors, 'message')}
                    </span>
                  )}
                </div>
              </div>

              <p className="enquiry-privacy-note">
                Please do not include payment details or other sensitive
                personal information. Privacy and data-retention details need
                owner review before public launch.
              </p>
              <button
                className="button button-primary enquiry-submit"
                disabled={isSubmitting || !category}
                type="submit"
              >
                {isSubmitting ? 'Sending enquiry…' : 'Send export enquiry'}
                {!isSubmitting && (
                  <ArrowUpRight aria-hidden="true" size={17} strokeWidth={1.8} />
                )}
              </button>
            </>
          )}
        </form>
      )}
    </main>
  )
}

export default EnquiryPage
