// Fallback components for UI errors
import React from 'react'

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
  )
}

export function ErrorFallback({ error, resetError }) {
  return (
    <div className="p-6 border rounded-lg bg-red-50 border-red-200">
      <h2 className="text-lg font-semibold text-red-800 mb-2">Something went wrong</h2>
      <pre className="text-sm text-red-600 mb-4 overflow-auto">{error.message}</pre>
      <button
        onClick={resetError}
        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Try again
      </button>
    </div>
  )
}

export function SimpleFallback({ children, fallback = <LoadingSpinner /> }) {
  const [hasError, setHasError] = React.useState(false)
  const [error, setError] = React.useState(null)

  const resetError = () => {
    setHasError(false)
    setError(null)
  }

  React.useEffect(() => {
    const errorHandler = (error) => {
      console.error('Caught by SimpleFallback:', error)
      setHasError(true)
      setError(error)
    }

    window.addEventListener('error', errorHandler)
    window.addEventListener('unhandledrejection', (event) => {
      errorHandler(event.reason)
    })

    return () => {
      window.removeEventListener('error', errorHandler)
      window.removeEventListener('unhandledrejection', errorHandler)
    }
  }, [])

  if (hasError) {
    return <ErrorFallback error={error} resetError={resetError} />
  }

  try {
    return children
  } catch (error) {
    return <ErrorFallback error={error} resetError={resetError} />
  }
}