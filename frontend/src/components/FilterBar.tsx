import React from 'react'
import type { Filters } from '../api/types'

interface FilterBarProps {
  filters: Filters
  onChange: (next: Filters) => void
}

const FOOD_TYPES = ['', 'Meat', 'Baked Goods', 'Dairy Products', 'Fruits', 'Vegetables']
const EVENT_TYPES = ['', 'Corporate', 'Social Gathering', 'Wedding', 'Birthday']
const PRICING = ['', 'High', 'Moderate', 'Low']
const LOCATIONS = ['', 'Suburban', 'Urban', 'Rural']

function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: string[]
  onChange: (v: string) => void
}) {
  return (
    <label
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-1)',
        fontSize: 'var(--font-size-xs)',
        color: 'var(--color-text-secondary)',
        fontWeight: 'var(--font-weight-medium)',
      }}
    >
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label={label}
        style={{
          padding: 'var(--space-2) var(--space-3)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-sm)',
          fontSize: 'var(--font-size-sm)',
          background: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          cursor: 'pointer',
          minWidth: '140px',
        }}
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt === '' ? 'All' : opt}
          </option>
        ))}
      </select>
    </label>
  )
}

export function FilterBar({ filters, onChange }: FilterBarProps) {
  const set = (key: keyof Filters) => (val: string) =>
    onChange({ ...filters, [key]: val || undefined })

  return (
    <div
      role="search"
      aria-label="Filter results"
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 'var(--space-4)',
        padding: 'var(--space-4)',
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-md)',
        marginBottom: 'var(--space-6)',
      }}
    >
      <Select
        label="Food type"
        value={filters.food_type ?? ''}
        options={FOOD_TYPES}
        onChange={set('food_type')}
      />
      <Select
        label="Event type"
        value={filters.event_type ?? ''}
        options={EVENT_TYPES}
        onChange={set('event_type')}
      />
      <Select
        label="Pricing"
        value={filters.pricing ?? ''}
        options={PRICING}
        onChange={set('pricing')}
      />
      <Select
        label="Location"
        value={filters.geographical_location ?? ''}
        options={LOCATIONS}
        onChange={set('geographical_location')}
      />
      <div style={{ display: 'flex', alignItems: 'flex-end' }}>
        <button
          onClick={() => onChange({})}
          style={{
            padding: 'var(--space-2) var(--space-3)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            background: 'transparent',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-secondary)',
          }}
        >
          Clear
        </button>
      </div>
    </div>
  )
}
