import React, { useCallback } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { ChartCard } from '../components/ChartCard'
import { DataTable } from '../components/DataTable'
import { FilterBar } from '../components/FilterBar'
import { useApi } from '../hooks/useApi'
import { useFilters } from '../hooks/useFilters'
import { api } from '../api/endpoints'
import type { WasteGroupItem, HeatmapItem } from '../api/types'

const fmt = (v: number) => `${v.toFixed(1)}%`

export function WastePage() {
  const [filters, setFilters] = useFilters()

  const foodFetcher = useCallback(() => api.wasteByFoodType(filters), [filters])
  const eventFetcher = useCallback(() => api.wasteByEventType(filters), [filters])
  const pricingFetcher = useCallback(() => api.wasteByPricing(filters), [filters])
  const heatmapFetcher = useCallback(() => api.wastageHeatmap(), [])

  const food = useApi(foodFetcher)
  const event = useApi(eventFetcher)
  const pricing = useApi(pricingFetcher)
  const heatmap = useApi(heatmapFetcher)

  const tableColumns = [
    { key: 'n' as const, header: 'Events', numeric: true },
    { key: 'mean_wastage_pct' as const, header: 'Mean wastage %', numeric: true, format: (v: unknown) => `${Number(v).toFixed(1)}%` },
    { key: 'median_wastage_pct' as const, header: 'Median %', numeric: true, format: (v: unknown) => `${Number(v).toFixed(1)}%` },
    { key: 'high_waste_share_pct' as const, header: 'High-waste events %', numeric: true, format: (v: unknown) => `${Number(v).toFixed(1)}%` },
  ]

  return (
    <div>
      <div className="page-header">
        <h1>Waste Analysis</h1>
        <p>Wastage % by food type, event type, pricing, and event–food combination.</p>
      </div>

      <FilterBar filters={filters} onChange={setFilters} />

      <div className="chart-grid">
        <ChartCard
          title="Mean wastage % by food type"
          subtitle="% of units prepared that were discarded"
          loading={food.loading}
          error={food.error}
          empty={!food.data || food.data.length === 0}
          onRetry={food.refetch}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={food.data ?? []} margin={{ top: 16, right: 8, left: 0, bottom: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="Type of Food" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={fmt} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" radius={[3, 3, 0, 0]}>
                {(food.data ?? []).map((_, i) => (
                  <Cell key={i} fill="var(--color-waste)" />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Mean wastage % by event type"
          subtitle="% of units prepared that were discarded"
          loading={event.loading}
          error={event.error}
          empty={!event.data || event.data.length === 0}
          onRetry={event.refetch}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={event.data ?? []} margin={{ top: 16, right: 8, left: 0, bottom: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="Event Type" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={fmt} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" fill="var(--color-accent)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Mean wastage % by pricing tier"
          subtitle="High pricing events waste significantly more"
          loading={pricing.loading}
          error={pricing.error}
          empty={!pricing.data || pricing.data.length === 0}
          onRetry={pricing.refetch}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={pricing.data ?? []} margin={{ top: 16, right: 8, left: 0, bottom: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="Pricing" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={fmt} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" fill="var(--color-warning)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard
        title="Wastage detail by food type"
        subtitle="All figures from clean event records (duplicates excluded)"
        loading={food.loading}
        error={food.error}
        empty={!food.data || food.data.length === 0}
      >
        {food.data && (
          <DataTable
            columns={[
              { key: 'Type of Food' as keyof WasteGroupItem & string, header: 'Food type' },
              ...tableColumns,
            ]}
            data={food.data}
          />
        )}
      </ChartCard>

      <div style={{ marginTop: 'var(--space-6)' }}>
        <ChartCard
          title="Wastage heatmap — food type x event type"
          subtitle="Mean wastage %. Cells with fewer than 10 events are excluded."
          loading={heatmap.loading}
          error={heatmap.error}
          empty={!heatmap.data || heatmap.data.length === 0}
        >
          {heatmap.data && (
            <DataTable
              columns={[
                { key: 'Type of Food' as keyof HeatmapItem & string, header: 'Food type' },
                { key: 'Event Type' as keyof HeatmapItem & string, header: 'Event type' },
                { key: 'n' as keyof HeatmapItem & string, header: 'n', numeric: true },
                {
                  key: 'mean_wastage_pct' as keyof HeatmapItem & string,
                  header: 'Mean wastage %',
                  numeric: true,
                  format: (v: unknown) => `${Number(v).toFixed(1)}%`,
                },
              ]}
              data={heatmap.data}
            />
          )}
        </ChartCard>
      </div>
    </div>
  )
}
