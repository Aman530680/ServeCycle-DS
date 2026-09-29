import React, { useState } from 'react'

export interface Column<T> {
  key: keyof T & string
  header: string
  numeric?: boolean
  format?: (val: unknown) => string
}

interface DataTableProps<T extends Record<string, unknown>> {
  columns: Column<T>[]
  data: T[]
  sortable?: boolean
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  sortable = true,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const handleSort = (key: string) => {
    if (!sortable) return
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  const sorted = sortKey
    ? [...data].sort((a, b) => {
        const av = a[sortKey]
        const bv = b[sortKey]
        if (typeof av === 'number' && typeof bv === 'number') {
          return sortDir === 'asc' ? av - bv : bv - av
        }
        return sortDir === 'asc'
          ? String(av).localeCompare(String(bv))
          : String(bv).localeCompare(String(av))
      })
    : data

  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: 'var(--font-size-sm)',
        }}
      >
        <thead>
          <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={() => handleSort(col.key)}
                style={{
                  padding: 'var(--space-2) var(--space-3)',
                  textAlign: col.numeric ? 'right' : 'left',
                  fontWeight: 'var(--font-weight-semibold)',
                  color: 'var(--color-text-secondary)',
                  cursor: sortable ? 'pointer' : 'default',
                  userSelect: 'none',
                  whiteSpace: 'nowrap',
                  fontSize: 'var(--font-size-xs)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                {col.header}
                {sortable && sortKey === col.key && (
                  <span style={{ marginLeft: 4 }}>
                    {sortDir === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, i) => (
            <tr
              key={i}
              style={{
                borderBottom: '1px solid var(--color-border)',
                background: i % 2 === 0 ? 'transparent' : 'rgba(0,0,0,0.015)',
              }}
            >
              {columns.map((col) => {
                const raw = row[col.key]
                const display = col.format ? col.format(raw) : String(raw ?? '')
                return (
                  <td
                    key={col.key}
                    style={{
                      padding: 'var(--space-2) var(--space-3)',
                      textAlign: col.numeric ? 'right' : 'left',
                      fontVariantNumeric: col.numeric ? 'tabular-nums' : 'normal',
                      color: 'var(--color-text-primary)',
                    }}
                  >
                    {display}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
