import React from 'react'
import { LoadingSpinner } from './LoadingSpinner'
import { EmptyState } from './EmptyState'
import { ErrorState } from './ErrorState'

interface ChartCardProps {
  title: string
  subtitle?: string
  loading?: boolean
  error?: string | null
  empty?: boolean
  onRetry?: () => void
  children: React.ReactNode
}

export function ChartCard({
  title,
  subtitle,
  loading,
  error,
  empty,
  onRetry,
  children,
}: ChartCardProps) {
  return (
    <div
      style={{
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-md)',
        padding: 'var(--space-6)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div style={{ marginBottom: 'var(--space-4)' }}>
        <h3
          style={{
            fontSize: 'var(--font-size-base)',
            fontWeight: 'var(--font-weight-semibold)',
            color: 'var(--color-text-primary)',
          }}
        >
          {title}
        </h3>
        {subtitle && (
          <p
            style={{
              fontSize: 'var(--font-size-xs)',
              color: 'var(--color-text-secondary)',
              marginTop: 'var(--space-1)',
            }}
          >
            {subtitle}
          </p>
        )}
      </div>
      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorState message={error} onRetry={onRetry} />
      ) : empty ? (
        <EmptyState message="No data available for the current filters." />
      ) : (
        children
      )}
    </div>
  )
}
