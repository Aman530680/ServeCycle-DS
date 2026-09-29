import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { DataTable } from '../components/DataTable'

const columns = [
  { key: 'name' as const, header: 'Name' },
  { key: 'value' as const, header: 'Value', numeric: true },
]

const data = [
  { name: 'Fruits', value: 7.0 },
  { name: 'Meat', value: 6.85 },
  { name: 'Vegetables', value: 6.76 },
]

describe('DataTable', () => {
  it('renders column headers', () => {
    render(<DataTable columns={columns} data={data} />)
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Value')).toBeInTheDocument()
  })

  it('renders all data rows', () => {
    render(<DataTable columns={columns} data={data} />)
    expect(screen.getByText('Fruits')).toBeInTheDocument()
    expect(screen.getByText('Meat')).toBeInTheDocument()
    expect(screen.getByText('Vegetables')).toBeInTheDocument()
  })

  it('sorts ascending on header click', () => {
    render(<DataTable columns={columns} data={data} />)
    fireEvent.click(screen.getByText('Value'))
    const cells = screen.getAllByRole('cell').filter((c) =>
      ['7', '6.85', '6.76'].includes(c.textContent ?? ''),
    )
    // After ascending sort the first numeric cell should be smallest
    expect(cells[0].textContent).toBe('6.76')
  })

  it('sorts descending on second header click', () => {
    render(<DataTable columns={columns} data={data} />)
    fireEvent.click(screen.getByText('Value'))
    fireEvent.click(screen.getByText('Value'))
    const cells = screen.getAllByRole('cell').filter((c) =>
      ['7', '6.85', '6.76'].includes(c.textContent ?? ''),
    )
    expect(cells[0].textContent).toBe('7')
  })

  it('applies custom format function', () => {
    const cols = [
      { key: 'name' as const, header: 'Name' },
      {
        key: 'value' as const,
        header: 'Pct',
        numeric: true,
        format: (v: unknown) => `${Number(v).toFixed(1)}%`,
      },
    ]
    render(<DataTable columns={cols} data={data} />)
    expect(screen.getByText('7.0%')).toBeInTheDocument()
  })
})
