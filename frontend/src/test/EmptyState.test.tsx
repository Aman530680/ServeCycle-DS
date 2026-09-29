import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { EmptyState } from '../components/EmptyState'

describe('EmptyState', () => {
  it('renders the message', () => {
    render(<EmptyState message="No data available." />)
    expect(screen.getByText('No data available.')).toBeInTheDocument()
  })
})
