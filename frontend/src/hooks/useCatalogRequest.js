import { useEffect, useState } from 'react'

export function useCatalogRequest(request) {
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState(null)

  useEffect(() => {
    let active = true

    request()
      .then((data) => {
        if (active) {
          setResult({ request, attempt, status: 'success', data, error: null })
        }
      })
      .catch((error) => {
        if (active) {
          setResult({ request, attempt, status: 'error', data: null, error })
        }
      })

    return () => {
      active = false
    }
  }, [request, attempt])

  const state =
    result?.request === request && result?.attempt === attempt
      ? result
      : { status: 'loading', data: null, error: null }

  return {
    ...state,
    retry: () => setAttempt((current) => current + 1),
  }
}
