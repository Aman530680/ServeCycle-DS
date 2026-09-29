import React, { useCallback } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ScatterChart, Scatter, ReferenceLine,
} from 'recharts'
import { ChartCard } from '../components/ChartCard'
import { DataTable } from '../components/DataTable'
import { StatCard } from '../components/StatCard'
import { useApi } from '../hooks/useApi'
import { api } from '../api/endpoints'

export function ModelPage() {
  const metricsFetcher = useCallback(() => api.modelMetrics(), [])
  const baselinesFetcher = useCallback(() => api.modelBaselines(), [])
  const featuresFetcher = useCallback(() => api.modelFeatures(), [])
  const importanceFetcher = useCallback(() => api.modelImportance(), [])

  const metrics = useApi(metricsFetcher)
  const baselines = useApi(baselinesFetcher)
  const features = useApi(featuresFetcher)
  const importance = useApi(importanceFetcher)

  return (
    <div>
      <div className="page-header">
        <h1>Model</h1>
        <p>
          Random Forest regression predicting wastage units from pre-event context.
          Evaluated on a held-out test set — figures are not cherry-picked.
        </p>
      </div>

      {metrics.data && (
        <div className="stat-grid" style={{ marginBottom: 'var(--space-6)' }}>
          <StatCard
            label="MAE"
            value={metrics.data.mae.toFixed(2)}
            unit="units"
            variant="default"
          />
          <StatCard
            label="RMSE"
            value={metrics.data.rmse.toFixed(2)}
            unit="units"
            variant="default"
          />
          <StatCard
            label="R²"
            value={metrics.data.r2.toFixed(3)}
            variant="positive"
          />
          <StatCard
            label="WAPE"
            value={`${metrics.data.wape.toFixed(1)}%`}
            variant="default"
          />
          <StatCard
            label="Test rows"
            value={metrics.data.test_rows.toLocaleString()}
          />
          <StatCard
            label="Train rows"
            value={metrics.data.train_rows.toLocaleString()}
          />
        </div>
      )}

      {metrics.data?.plain_language && (
        <div
          style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-6)',
            marginBottom: 'var(--space-6)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <h3
            style={{
              fontSize: 'var(--font-size-base)',
              fontWeight: 'var(--font-weight-semibold)',
              marginBottom: 'var(--space-4)',
            }}
          >
            What these numbers mean
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {Object.entries(metrics.data.plain_language).map(([k, v]) => (
              <p key={k} style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                <strong style={{ color: 'var(--color-text-primary)', textTransform: 'uppercase', fontSize: 'var(--font-size-xs)' }}>
                  {k}
                </strong>{' '}
                — {v}
              </p>
            ))}
          </div>
          <p
            style={{
              marginTop: 'var(--space-4)',
              fontSize: 'var(--font-size-xs)',
              color: 'var(--color-warning)',
              fontStyle: 'italic',
            }}
          >
            Split strategy: {metrics.data.split_strategy}
          </p>
        </div>
      )}

      <div className="chart-grid">
        <ChartCard
          title="Baseline comparison"
          subtitle="Model must beat all three baselines to be considered useful"
          loading={baselines.loading}
          error={baselines.error}
          empty={!baselines.data || baselines.data.length === 0}
          onRetry={baselines.refetch}
        >
          {baselines.data && metrics.data && (
            <DataTable
              columns={[
                { key: 'name', header: 'Model' },
                {
                  key: 'mae',
                  header: 'MAE (units)',
                  numeric: true,
                  format: (v) => Number(v).toFixed(3),
                },
                {
                  key: 'rmse',
                  header: 'RMSE',
                  numeric: true,
                  format: (v) => Number(v).toFixed(3),
                },
                {
                  key: 'r2',
                  header: 'R²',
                  numeric: true,
                  format: (v) => Number(v).toFixed(4),
                },
                {
                  key: 'wape',
                  header: 'WAPE',
                  numeric: true,
                  format: (v) => `${Number(v).toFixed(2)}%`,
                },
              ]}
              data={[
                ...baselines.data,
                {
                  name: 'Random Forest',
                  mae: metrics.data.mae,
                  rmse: metrics.data.rmse,
                  r2: metrics.data.r2,
                  wape: metrics.data.wape,
                },
              ]}
            />
          )}
        </ChartCard>

        <ChartCard
          title="Feature importance (impurity-based)"
          subtitle="Higher = more predictive of wastage amount"
          loading={importance.loading}
          error={importance.error}
          empty={!importance.data || importance.data.length === 0}
          onRetry={importance.refetch}
        >
          <ResponsiveContainer width="100%" height={280}>
            <BarChart
              layout="vertical"
              data={[...(importance.data ?? [])].reverse()}
              margin={{ top: 4, right: 16, left: 120, bottom: 4 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => v.toFixed(3)} />
              <YAxis type="category" dataKey="feature" tick={{ fontSize: 10 }} width={115} />
              <Tooltip formatter={(v: number) => [v.toFixed(4), 'Importance']} />
              <Bar dataKey="importance" fill="var(--color-accent)" radius={[0, 3, 3, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {features.data && (
        <div
          style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-6)',
            marginTop: 'var(--space-6)',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <h3
            style={{
              fontSize: 'var(--font-size-base)',
              fontWeight: 'var(--font-weight-semibold)',
              marginBottom: 'var(--space-3)',
            }}
          >
            Model configuration
          </h3>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-2)' }}>
            <strong>Target:</strong> {features.data.target}
          </p>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-2)' }}>
            <strong>Features ({features.data.features.length}):</strong>{' '}
            {features.data.features.join(', ')}
          </p>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-waste)', marginBottom: 'var(--space-2)' }}>
            <strong>Excluded:</strong> {features.data.excluded.join(', ')}
          </p>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            <strong>Best params:</strong>{' '}
            {Object.entries(features.data.best_params)
              .map(([k, v]) => `${k}=${v}`)
              .join(', ')}
          </p>
        </div>
      )}
    </div>
  )
}
