import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatCard } from '../components/StatCard'

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard label="Total events" value={1782} />)
    expect(screen.getByText('Total events')).toBeInTheDocument()
    expect(screen.getByText('1782')).toBeInTheDocument()
  })

  it('renders unit when provided', () => {
    render(<StatCard label="Prepared" value={666980} unit="units" />)
    expect(screen.getByText('units')).toBeInTheDocument()
  })

  it('renders string values', () => {
    render(<StatCard label="Wastage" value="6.9%" variant="waste" />)
    expect(screen.getByText('6.9%')).toBeInTheDocument()
  })

  it('renders without unit', () => {
    render(<StatCard label="R²" value="0.893" />)
    expect(screen.getByText('0.893')).toBeInTheDocument()
  })
})
