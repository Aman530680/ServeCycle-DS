import React from 'react'
import type { InsightItem } from '../api/types'

export function InsightCard({ number, statement, comparison_basis, caveat }: InsightItem) {
  return (
    <div
      style={{
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderLeft: '3px solid var(--color-accent)',
        borderRadius: 'var(--radius-md)',
        padding: 'var(--space-4) var(--space-6)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'flex-start' }}>
        <span
          style={{
            fontSize: 'var(--font-size-xs)',
            fontWeight: 'var(--font-weight-semibold)',
            color: 'var(--color-accent)',
            background: 'rgba(44,110,138,0.1)',
            borderRadius: 'var(--radius-sm)',
            padding: '2px 8px',
            flexShrink: 0,
            marginTop: 2,
          }}
        >
          {number}
        </span>
        <div style={{ flex: 1 }}>
          <p
            style={{
              fontSize: 'var(--font-size-sm)',
              color: 'var(--color-text-primary)',
              fontWeight: 'var(--font-weight-medium)',
              lineHeight: 'var(--line-height-normal)',
            }}
          >
            {statement}
          </p>
          <p
            style={{
              fontSize: 'var(--font-size-xs)',
              color: 'var(--color-text-secondary)',
              marginTop: 'var(--space-1)',
            }}
          >
            Basis: {comparison_basis}
          </p>
          {caveat && (
            <p
              style={{
                fontSize: 'var(--font-size-xs)',
                color: 'var(--color-warning)',
                marginTop: 'var(--space-1)',
                fontStyle: 'italic',
              }}
            >
              Note: {caveat}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
