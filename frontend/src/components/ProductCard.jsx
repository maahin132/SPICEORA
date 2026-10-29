import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import ProductImage from './ProductImage.jsx'

function ProductCard({ product }) {
  return (
    <article className="product-card">
      <Link
        aria-label={`View ${product.name}`}
        className="product-card-link"
        to={`/products/${encodeURIComponent(product.slug)}/`}
      >
        <ProductImage
          alt={product.image_alt}
          className="product-card-image"
          src={product.image}
        />
        <div className="product-card-copy">
          <span className="eyebrow">{product.category.name}</span>
          <h3>{product.name}</h3>
          <p>{product.summary}</p>
          <span className="product-card-action">
            Product details
            <ArrowUpRight aria-hidden="true" size={16} strokeWidth={1.8} />
          </span>
        </div>
      </Link>
    </article>
  )
}

export default ProductCard
