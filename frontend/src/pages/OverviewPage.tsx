import React, { useCallback } from 'react'
import { StatCard } from '../components/StatCard'
import { InsightCard } from '../components/InsightCard'
import { FilterBar } from '../components/FilterBar'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorState } from '../components/ErrorState'
import { useApi } from '../hooks/useApi'
import { useFilters } from '../hooks/useFilters'
import { api } from '../api/endpoints'

export function OverviewPage() {
  const [filters, setFilters] = useFilters()

  const overviewFetcher = useCallback(() => api.overview(filters), [filters])
  const insightsFetcher = useCallback(() => api.insights(), [])

  const { data: overview, loading: ovLoading, error: ovError, refetch: ovRetry } = useApi(overviewFetcher)
  const { data: insights, loading: insLoading, error: insError } = useApi(insightsFetcher)

  return (
    <div>
      <div className="page-header">
        <h1>Overview</h1>
        <p>Summary of catering event food wastage across all records.</p>
      </div>

      <FilterBar filters={filters} onChange={setFilters} />

      {ovLoading ? (
        <LoadingSpinner />
      ) : ovError ? (
        <ErrorState message={ovError} onRetry={ovRetry} />
      ) : overview ? (
        <div className="stat-grid">
          <StatCard label="Total events" value={overview.total_events.toLocaleString()} />
          <StatCard
            label="Mean wastage"
            value={`${overview.overall_wastage_pct.toFixed(1)}%`}
            variant="waste"
          />
          <StatCard
            label="Units prepared"
            value={overview.total_qty_prepared.toLocaleString()}
            unit="units"
          />
          <StatCard
            label="Units wasted"
            value={overview.total_wastage_units.toLocaleString()}
            unit="units"
            variant="waste"
          />
          <StatCard label="Food types" value={overview.unique_food_types} />
          <StatCard label="Event types" value={overview.unique_event_types} />
        </div>
      ) : null}

      <div style={{ marginTop: 'var(--space-8)' }}>
        <h2
          style={{
            fontSize: 'var(--font-size-lg)',
            fontWeight: 'var(--font-weight-semibold)',
            marginBottom: 'var(--space-4)',
          }}
        >
          Key findings
        </h2>
        {insLoading ? (
          <LoadingSpinner />
        ) : insError ? (
          <ErrorState message={insError} />
        ) : insights && insights.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {insights.map((item) => (
              <InsightCard key={item.number} {...item} />
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>
            No insights available.
          </p>
        )}
      </div>
    </div>
  )
}
