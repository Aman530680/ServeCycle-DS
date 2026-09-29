import React, { useCallback } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { ChartCard } from '../components/ChartCard'
import { DataTable } from '../components/DataTable'
import { useApi } from '../hooks/useApi'
import { api } from '../api/endpoints'

export function DemandPage() {
  const weekdayFetcher = useCallback(() => api.demandByWeekday(), [])
  const weatherFetcher = useCallback(() => api.demandByWeather(), [])
  const prepFetcher = useCallback(() => api.wasteByPrepMethod(), [])

  const weekday = useApi(weekdayFetcher)
  const weather = useApi(weatherFetcher)
  const prep = useApi(prepFetcher)

  return (
    <div>
      <div className="page-header">
        <h1>Demand</h1>
        <p>
          Preparation and wastage by guest volume, seasonality, and preparation method.
          This dataset has no date or weekday column — guest-count bands are used as a
          volume proxy.
        </p>
      </div>

      <div className="chart-grid">
        <ChartCard
          title="Wastage % by guest count band (quartiles)"
          subtitle="Larger events waste a higher share of prepared food"
          loading={weekday.loading}
          error={weekday.error}
          empty={!weekday.data || weekday.data.length === 0}
          onRetry={weekday.refetch}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={weekday.data ?? []} margin={{ top: 16, right: 8, left: 0, bottom: 32 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="guest_band" tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={(v) => `${v.toFixed(1)}%`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" fill="var(--color-accent)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Wastage % by seasonality"
          subtitle="No weather column — seasonality is the closest proxy"
          loading={weather.loading}
          error={weather.error}
          empty={!weather.data || weather.data.length === 0}
          onRetry={weather.refetch}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={weather.data ?? []} margin={{ top: 16, right: 8, left: 0, bottom: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="Seasonality" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `${v.toFixed(1)}%`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" fill="var(--color-accent)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Wastage % by preparation method"
          subtitle="Sit-down dinner produces the highest wastage rate"
          loading={prep.loading}
          error={prep.error}
          empty={!prep.data || prep.data.length === 0}
          onRetry={prep.refetch}
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={prep.data ?? []} margin={{ top: 16, right: 8, left: 0, bottom: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="Preparation Method" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `${v.toFixed(1)}%`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'Mean wastage']} />
              <Bar dataKey="mean_wastage_pct" fill="var(--color-waste)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {weekday.data && (
        <ChartCard
          title="Guest count band detail"
          subtitle="Mean wastage % and mean preparation quantity per band"
        >
          <DataTable
            columns={[
              { key: 'guest_band', header: 'Guest band' },
              { key: 'n', header: 'Events', numeric: true },
              { key: 'mean_wastage_pct', header: 'Mean wastage %', numeric: true, format: (v) => `${Number(v).toFixed(1)}%` },
              { key: 'mean_guests', header: 'Mean guests', numeric: true, format: (v) => Number(v).toFixed(0) },
              { key: 'mean_qty_prepared', header: 'Mean qty prepared', numeric: true, format: (v) => Number(v).toFixed(0) },
            ]}
            data={weekday.data}
          />
        </ChartCard>
      )}
    </div>
  )
}
