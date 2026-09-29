import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ChartCard } from '../components/ChartCard'

describe('ChartCard', () => {
  it('renders title', () => {
    render(<ChartCard title="Waste by food type"><p>chart</p></ChartCard>)
    expect(screen.getByText('Waste by food type')).toBeInTheDocument()
  })

  it('renders subtitle when provided', () => {
    render(
      <ChartCard title="Test" subtitle="Mean wastage % by food type">
        <p>chart</p>
      </ChartCard>,
    )
    expect(screen.getByText('Mean wastage % by food type')).toBeInTheDocument()
  })

  it('shows loading state instead of children', () => {
    render(
      <ChartCard title="Test" loading>
        <p>should not appear</p>
      </ChartCard>,
    )
    expect(screen.queryByText('should not appear')).toBeNull()
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('shows error state when error is provided', () => {
    render(
      <ChartCard title="Test" error="Request failed">
        <p>should not appear</p>
      </ChartCard>,
    )
    expect(screen.getByText('Request failed')).toBeInTheDocument()
    expect(screen.queryByText('should not appear')).toBeNull()
  })

  it('shows empty state when empty is true', () => {
    render(
      <ChartCard title="Test" empty>
        <p>should not appear</p>
      </ChartCard>,
    )
    expect(
      screen.getByText('No data available for the current filters.'),
    ).toBeInTheDocument()
    expect(screen.queryByText('should not appear')).toBeNull()
  })

  it('renders children when not loading, error, or empty', () => {
    render(
      <ChartCard title="Test">
        <p>real chart content</p>
      </ChartCard>,
    )
    expect(screen.getByText('real chart content')).toBeInTheDocument()
  })

  it('calls onRetry when retry button is clicked in error state', () => {
    const onRetry = vi.fn()
    render(
      <ChartCard title="Test" error="Failed" onRetry={onRetry}>
        <p>chart</p>
      </ChartCard>,
    )
    fireEvent.click(screen.getByText('Retry'))
    expect(onRetry).toHaveBeenCalledTimes(1)
  })
})
