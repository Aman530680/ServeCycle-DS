import React from 'react'

export function LoadingSpinner() {
  return (
    <div
      role="status"
      aria-label="Loading"
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 'var(--space-12)',
        color: 'var(--color-text-secondary)',
        fontSize: 'var(--font-size-sm)',
      }}
    >
      Loading...
    </div>
  )
}
