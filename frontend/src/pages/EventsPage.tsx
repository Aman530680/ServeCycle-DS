import React, { useCallback } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { ChartCard } from '../components/ChartCard'
import { DataTable } from '../components/DataTable'
import { useApi } from '../hooks/useApi'
import { api } from '../api/endpoints'

export function EventsPage() {
  const promotionsFetcher = useCallback(() => api.promotionsImpact(), [])
  const eventsFetcher = useCallback(() => api.eventsImpact(), [])

  const promotions = useApi(promotionsFetcher)
  const events = useApi(eventsFetcher)

  return (
    <div>
      <div className="page-header">
        <h1>Promotions &amp; Events</h1>
        <p>
          Pricing tier is used as a proxy for event spend level (no promotion flag
          in the dataset). Event type and seasonality capture special-event effects.
        </p>
      </div>

      <div className="chart-grid">
        <ChartCard
          title="Wastage % by pricing tier"
          subtitle="Proxy for event spend level — not a direct promotion flag"
          loading={promotions.loading}
          error={promotions.error}
          empty={!promotions.data || promotions.data.length === 0}
          onRetry={promotions.refetch}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={promotions.data ?? []} margin={{ top: 16, right: 8, left: 0, bottom: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="Pricing" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `${v.toFixed(1)}%`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" fill="var(--color-warning)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          {promotions.data && (
            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: 'var(--space-2)' }}>
              Sample sizes: {promotions.data.map(d => `${d['Pricing'] as string} n=${d.n}`).join(', ')}
            </p>
          )}
        </ChartCard>

        <ChartCard
          title="Wastage % by event type"
          subtitle="Weddings show the highest mean wastage"
          loading={events.loading}
          error={events.error}
          empty={!events.data}
          onRetry={events.refetch}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={events.data?.by_event_type ?? []}
              margin={{ top: 16, right: 8, left: 0, bottom: 24 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="Event Type" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `${v.toFixed(1)}%`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" fill="var(--color-accent)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Wastage % by seasonality"
          subtitle="Summer events waste slightly more than winter"
          loading={events.loading}
          error={events.error}
          empty={!events.data}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={events.data?.by_seasonality ?? []}
              margin={{ top: 16, right: 8, left: 0, bottom: 24 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="Seasonality" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `${v.toFixed(1)}%`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" fill="var(--color-accent)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {promotions.data && (
        <ChartCard title="Pricing tier detail" subtitle="n = number of events">
          <DataTable
            columns={[
              { key: 'Pricing', header: 'Pricing tier' },
              { key: 'n', header: 'Events', numeric: true },
              { key: 'mean_wastage_pct', header: 'Mean wastage %', numeric: true, format: (v) => `${Number(v).toFixed(1)}%` },
              { key: 'median_wastage_pct', header: 'Median %', numeric: true, format: (v) => `${Number(v).toFixed(1)}%` },
            ]}
            data={promotions.data}
          />
        </ChartCard>
      )}
    </div>
  )
}
