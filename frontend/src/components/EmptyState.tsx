import React from 'react'

interface EmptyStateProps {
  message: string
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <div
      style={{
        padding: 'var(--space-12)',
        textAlign: 'center',
        color: 'var(--color-text-secondary)',
        fontSize: 'var(--font-size-sm)',
      }}
    >
      {message}
    </div>
  )
}
