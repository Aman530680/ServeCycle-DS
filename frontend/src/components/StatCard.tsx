import React from 'react'

interface StatCardProps {
  label: string
  value: string | number
  unit?: string
  variant?: 'default' | 'waste' | 'positive'
}

const variantColor: Record<string, string> = {
  default: 'var(--color-accent)',
  waste: 'var(--color-waste)',
  positive: 'var(--color-positive)',
}

export function StatCard({ label, value, unit, variant = 'default' }: StatCardProps) {
  return (
    <div
      style={{
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-md)',
        padding: 'var(--space-4) var(--space-6)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <p
        style={{
          fontSize: 'var(--font-size-xs)',
          fontWeight: 'var(--font-weight-medium)',
          color: 'var(--color-text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: 'var(--space-2)',
        }}
      >
        {label}
      </p>
      <p
        style={{
          fontSize: 'var(--font-size-2xl)',
          fontWeight: 'var(--font-weight-semibold)',
          color: variantColor[variant],
          fontVariantNumeric: 'tabular-nums',
          lineHeight: 'var(--line-height-tight)',
        }}
      >
        {value}
        {unit && (
          <span
            style={{
              fontSize: 'var(--font-size-sm)',
              color: 'var(--color-text-secondary)',
              fontWeight: 'var(--font-weight-normal)',
              marginLeft: 'var(--space-1)',
            }}
          >
            {unit}
          </span>
        )}
      </p>
    </div>
  )
}
