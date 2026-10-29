function CatalogFeedback({ status, error, onRetry }) {
  if (status === 'loading') {
    return (
      <p aria-live="polite" className="catalog-feedback">
        Loading the product catalogue…
      </p>
    )
  }

  if (status === 'error') {
    return (
      <div
        aria-live="polite"
        className="catalog-feedback catalog-feedback--error"
      >
        <p>
          {error?.status === 404
            ? error.message
            : 'The catalogue could not be loaded. Please try again.'}
        </p>
        {onRetry && (
          <button className="catalog-retry" onClick={onRetry} type="button">
            Try again
          </button>
        )}
      </div>
    )
  }

  return null
}

export default CatalogFeedback
