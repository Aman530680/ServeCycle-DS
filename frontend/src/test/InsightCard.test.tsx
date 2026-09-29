import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { InsightCard } from '../components/InsightCard'

describe('InsightCard', () => {
  it('renders insight number', () => {
    render(
      <InsightCard
        number={1}
        statement="Fruits waste the most."
        comparison_basis="Overall mean."
        caveat={null}
      />,
    )
    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('renders statement text', () => {
    render(
      <InsightCard
        number={2}
        statement="High pricing events waste 8.8%."
        comparison_basis="High vs Low pricing."
        caveat={null}
      />,
    )
    expect(screen.getByText('High pricing events waste 8.8%.')).toBeInTheDocument()
  })

  it('renders comparison basis', () => {
    render(
      <InsightCard
        number={3}
        statement="Statement."
        comparison_basis="n=400 vs n=350."
        caveat={null}
      />,
    )
    expect(screen.getByText(/n=400 vs n=350/)).toBeInTheDocument()
  })

  it('renders caveat when provided', () => {
    render(
      <InsightCard
        number={4}
        statement="Statement."
        comparison_basis="Basis."
        caveat="Small sample size — interpret with caution."
      />,
    )
    expect(
      screen.getByText(/Small sample size — interpret with caution/),
    ).toBeInTheDocument()
  })

  it('does not render caveat section when caveat is null', () => {
    render(
      <InsightCard number={5} statement="Statement." comparison_basis="Basis." caveat={null} />,
    )
    expect(screen.queryByText(/Note:/)).toBeNull()
  })
})
