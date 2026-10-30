import { useState } from 'react'

function ProductImage({ alt, className, loading = 'lazy', src }) {
  const [failedSrc, setFailedSrc] = useState(null)
  const failed = Boolean(src) && failedSrc === src

  return (
    <div className={className}>
      {src && !failed ? (
        <img
          alt={alt}
          decoding="async"
          fetchPriority={loading === 'eager' ? 'high' : 'auto'}
          loading={loading}
          onError={() => setFailedSrc(src)}
          src={src}
        />
      ) : (
        <div
          aria-label={alt || undefined}
          className="product-image-placeholder"
          role={alt ? 'img' : undefined}
        >
          <span>SPICEORA</span>
        </div>
      )}
    </div>
  )
}

export default ProductImage
