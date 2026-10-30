import { ArrowUpRight } from 'lucide-react'
import { useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { getCategories, getProducts } from '../api/catalog.js'
import CatalogFeedback from '../components/CatalogFeedback.jsx'
import ProductCard from '../components/ProductCard.jsx'
import { useCatalogRequest } from '../hooks/useCatalogRequest.js'
import usePageMetadata from '../hooks/usePageMetadata.js'

function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const category = searchParams.get('category') || ''
  const page = searchParams.get('page') || '1'
  const request = useCallback(
    () => Promise.all([getProducts({ category, page }), getCategories()]),
    [category, page],
  )
  const state = useCatalogRequest(request)
  usePageMetadata(
    'Products | SPICEORA',
    'Review product information published by SPICEORA, or ask about a category through the enquiry form.',
  )

  function updateSearch(nextCategory, nextPage = '1') {
    const nextParams = new URLSearchParams()
    if (nextCategory) nextParams.set('category', nextCategory)
    if (nextPage !== '1') nextParams.set('page', nextPage)
    setSearchParams(nextParams)
  }

  return (
    <main className="catalog-page" id="main-content">
      <div className="catalog-intro">
        <p className="eyebrow">SPICEORA · Product catalogue</p>
        <h1>Explore the collection.</h1>
        <p>
          Browse products published in the catalogue. Product details appear
          here only when confirmed and approved by the business.
        </p>
        <Link className="text-link" to="/">
          Return to the homepage
        </Link>
      </div>

      <section aria-labelledby="products-heading" className="catalog-results">
        <div className="catalog-toolbar">
          <div>
            <p className="eyebrow">Published products</p>
            <h2 id="products-heading">A considered collection</h2>
          </div>
          {state.status === 'success' && state.data[1].length > 0 && (
            <div className="catalog-filter">
              <label htmlFor="category-filter">Filter by category</label>
              <select
                id="category-filter"
                onChange={(event) => updateSearch(event.target.value)}
                value={category}
              >
                <option value="">All categories</option>
                {state.data[1].map((item) => (
                  <option key={item.slug} value={item.slug}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <CatalogFeedback
          error={state.error}
          onRetry={state.retry}
          status={state.status}
        />

        {state.status === 'success' && state.data[0].results.length === 0 && (
          <div aria-live="polite" className="catalog-empty">
            <p className="eyebrow">Catalogue status</p>
            <h3>No products have been published yet.</h3>
            <p>
              Only owner-approved product information appears here. You can
              still share what you are looking for with SPICEORA.
            </p>
            <div className="catalog-empty-actions">
              <Link
                className="button button-primary"
                to={
                  category
                    ? `/enquiry/?category=${encodeURIComponent(category)}`
                    : '/enquiry/'
                }
              >
                Make a product enquiry
                <ArrowUpRight aria-hidden="true" size={16} />
              </Link>
              {category && (
                <button
                  className="text-link catalog-clear-filter"
                  onClick={() => updateSearch('')}
                  type="button"
                >
                  Browse all categories
                </button>
              )}
            </div>
          </div>
        )}

        {state.status === 'success' && state.data[0].results.length > 0 && (
          <>
            <div className="products-grid">
              {state.data[0].results.map((product) => (
                <ProductCard key={product.slug} product={product} />
              ))}
            </div>
            <nav aria-label="Product pages" className="catalog-pagination">
              <button
                disabled={!state.data[0].previous}
                onClick={() =>
                  updateSearch(category, String(Math.max(1, Number(page) - 1)))
                }
                type="button"
              >
                Previous
              </button>
              <span>
                Page {page} · {state.data[0].count} products
              </span>
              <button
                disabled={!state.data[0].next}
                onClick={() => updateSearch(category, String(Number(page) + 1))}
                type="button"
              >
                Next
              </button>
            </nav>
          </>
        )}
      </section>
    </main>
  )
}

export default ProductsPage
