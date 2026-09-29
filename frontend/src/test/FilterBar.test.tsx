import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { FilterBar } from '../components/FilterBar'

describe('FilterBar', () => {
  it('renders all four filter labels', () => {
    render(<FilterBar filters={{}} onChange={vi.fn()} />)
    expect(screen.getByLabelText('Food type')).toBeInTheDocument()
    expect(screen.getByLabelText('Event type')).toBeInTheDocument()
    expect(screen.getByLabelText('Pricing')).toBeInTheDocument()
    expect(screen.getByLabelText('Location')).toBeInTheDocument()
  })

  it('calls onChange when a filter is changed', () => {
    const onChange = vi.fn()
    render(<FilterBar filters={{}} onChange={onChange} />)
    fireEvent.change(screen.getByLabelText('Food type'), {
      target: { value: 'Meat' },
    })
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ food_type: 'Meat' }))
  })

  it('calls onChange with empty object when Clear is clicked', () => {
    const onChange = vi.fn()
    render(<FilterBar filters={{ food_type: 'Meat' }} onChange={onChange} />)
    fireEvent.click(screen.getByText('Clear'))
    expect(onChange).toHaveBeenCalledWith({})
  })

  it('reflects current filter values', () => {
    render(<FilterBar filters={{ pricing: 'High' }} onChange={vi.fn()} />)
    const pricingSelect = screen.getByLabelText('Pricing') as HTMLSelectElement
    expect(pricingSelect.value).toBe('High')
  })
})
