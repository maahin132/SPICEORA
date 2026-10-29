import { useCallback } from 'react'
import { Link, useParams } from 'react-router-dom'

import { CatalogApiError, getProduct } from '../api/catalog.js'
import CatalogFeedback from '../components/CatalogFeedback.jsx'
import ProductImage from '../components/ProductImage.jsx'
import { useCatalogRequest } from '../hooks/useCatalogRequest.js'

function ProductDetailPage() {
  const { slug } = useParams()
  const request = useCallback(() => getProduct(slug), [slug])
  const state = useCatalogRequest(request)

  if (state.status !== 'success') {
    const unavailable =
      state.error instanceof CatalogApiError && state.error.status === 404

    return (
      <main className="catalog-page product-detail-page" id="main-content">
        <p className="eyebrow">SPICEORA · Product catalogue</p>
        {unavailable ? (
          <section aria-labelledby="product-not-found">
            <h1 id="product-not-found">Product not found.</h1>
            <p>This product is not available in the published catalogue.</p>
          </section>
        ) : (
          <CatalogFeedback
            error={state.error}
            onRetry={state.retry}
            status={state.status}
          />
        )}
        <Link className="text-link" to="/products/">
          Back to products
        </Link>
      </main>
    )
  }

  const product = state.data

  return (
    <main className="catalog-page product-detail-page" id="main-content">
      <nav aria-label="Breadcrumb" className="product-breadcrumb">
        <Link to="/">Home</Link>
        <span aria-hidden="true">/</span>
        <Link to="/products/">Products</Link>
        <span aria-hidden="true">/</span>
        <span aria-current="page">{product.name}</span>
      </nav>

      <article className="product-detail">
        <ProductImage
          alt={product.image_alt}
          className="product-detail-image"
          src={product.image}
        />
        <div className="product-detail-copy">
          <p className="eyebrow">{product.category.name}</p>
          <h1>{product.name}</h1>
          <p className="product-detail-summary">{product.summary}</p>
          <div className="product-description">{product.description}</div>
          <Link
            className="text-link"
            to={`/products/?category=${encodeURIComponent(product.category.slug)}`}
          >
            Explore this category
          </Link>
        </div>
      </article>
    </main>
  )
}

export default ProductDetailPage
