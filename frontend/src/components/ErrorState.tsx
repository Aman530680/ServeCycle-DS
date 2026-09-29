import React from 'react'

interface ErrorStateProps {
  message: string
  onRetry?: () => void
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div
      style={{
        padding: 'var(--space-8)',
        textAlign: 'center',
        color: 'var(--color-waste)',
        fontSize: 'var(--font-size-sm)',
      }}
    >
      <p>{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: 'var(--space-3)',
            padding: 'var(--space-2) var(--space-4)',
            background: 'var(--color-accent)',
            color: '#fff',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--font-size-sm)',
            cursor: 'pointer',
          }}
        >
          Retry
        </button>
      )}
    </div>
  )
}
