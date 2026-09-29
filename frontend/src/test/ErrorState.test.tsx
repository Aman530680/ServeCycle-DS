import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ErrorState } from '../components/ErrorState'

describe('ErrorState', () => {
  it('renders the error message', () => {
    render(<ErrorState message="Something went wrong." />)
    expect(screen.getByText('Something went wrong.')).toBeInTheDocument()
  })

  it('renders retry button when onRetry is provided', () => {
    const onRetry = vi.fn()
    render(<ErrorState message="Failed." onRetry={onRetry} />)
    expect(screen.getByText('Retry')).toBeInTheDocument()
  })

  it('calls onRetry when retry button is clicked', () => {
    const onRetry = vi.fn()
    render(<ErrorState message="Failed." onRetry={onRetry} />)
    fireEvent.click(screen.getByText('Retry'))
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('does not render retry button when onRetry is absent', () => {
    render(<ErrorState message="Failed." />)
    expect(screen.queryByText('Retry')).toBeNull()
  })
})
