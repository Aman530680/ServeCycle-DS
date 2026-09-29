import React, { useCallback, useState } from 'react'
import { ChartCard } from '../components/ChartCard'
import { DataTable } from '../components/DataTable'
import { useApi } from '../hooks/useApi'
import { api } from '../api/endpoints'
import type { PredictRequest, PredictResponse, WhatIfResponse } from '../api/types'

const FOOD_TYPES = ['Meat', 'Baked Goods', 'Dairy Products', 'Fruits', 'Vegetables']
const EVENT_TYPES = ['Corporate', 'Social Gathering', 'Wedding', 'Birthday']
const STORAGE = ['Refrigerated', 'Room Temperature']
const PURCHASE = ['Regular', 'Occasional']
const SEASONS = ['Winter', 'Summer', 'All Seasons']
const PREP_METHODS = ['Sit-down Dinner', 'Finger Food', 'Buffet']
const LOCATIONS = ['Suburban', 'Urban', 'Rural']
const PRICING = ['High', 'Moderate', 'Low']

const defaultForm: PredictRequest = {
  'Type of Food': 'Meat',
  'Number of Guests': 300,
  'Event Type': 'Corporate',
  'Storage Conditions': 'Refrigerated',
  'Purchase History': 'Regular',
  Seasonality: 'Winter',
  'Preparation Method': 'Buffet',
  'Geographical Location': 'Urban',
  Pricing: 'High',
  service_level: 0.9,
}

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <label
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-1)',
        fontSize: 'var(--font-size-xs)',
        color: 'var(--color-text-secondary)',
        fontWeight: 'var(--font-weight-medium)',
      }}
    >
      {label}
      {children}
    </label>
  )
}

const inputStyle: React.CSSProperties = {
  padding: 'var(--space-2) var(--space-3)',
  border: '1px solid var(--color-border)',
  borderRadius: 'var(--radius-sm)',
  fontSize: 'var(--font-size-sm)',
  background: 'var(--color-surface)',
  color: 'var(--color-text-primary)',
  width: '100%',
}

function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: string[]
  onChange: (v: string) => void
}) {
  return (
    <Field label={label}>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label={label}
        style={inputStyle}
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </Field>
  )
}

export function RecommendationsPage() {
  const [form, setForm] = useState<PredictRequest>(defaultForm)
  const [prediction, setPrediction] = useState<PredictResponse | null>(null)
  const [predLoading, setPredLoading] = useState(false)
  const [predError, setPredError] = useState<string | null>(null)

  const [reducePct, setReducePct] = useState(10)
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResponse | null>(null)
  const [whatIfLoading, setWhatIfLoading] = useState(false)
  const [whatIfError, setWhatIfError] = useState<string | null>(null)

  const recFetcher = useCallback(() => api.recommendations(), [])
  const { data: recData, loading: recLoading, error: recError } = useApi(recFetcher)

  const set = (key: keyof PredictRequest) => (v: string | number) =>
    setForm((prev) => ({ ...prev, [key]: v }))

  const handlePredict = async () => {
    setPredLoading(true)
    setPredError(null)
    setPrediction(null)
    try {
      const result = await api.predictDemand(form)
      setPrediction(result)
    } catch (e) {
      setPredError(e instanceof Error ? e.message : 'Prediction failed')
    } finally {
      setPredLoading(false)
    }
  }

  const handleWhatIf = async () => {
    if (!prediction) return
    setWhatIfLoading(true)
    setWhatIfError(null)
    setWhatIfResult(null)
    try {
      const result = await api.whatIf(form, reducePct)
      setWhatIfResult(result)
    } catch (e) {
      setWhatIfError(e instanceof Error ? e.message : 'What-if failed')
    } finally {
      setWhatIfLoading(false)
    }
  }

  const handleExport = () => {
    if (!recData?.results) return
    const headers = Object.keys(recData.results[0]).join(',')
    const rows = recData.results
      .map((r) => Object.values(r).join(','))
      .join('\n')
    const csv = `${headers}\n${rows}`
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'servecycle_recommendations.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <div className="page-header">
        <h1>Recommendations</h1>
        <p>
          Predict expected wastage for a planned event and get a suggested preparation quantity.
          All figures are estimates based on historical patterns.
        </p>
      </div>

      {/* Prediction form */}
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
        <h2
          style={{
            fontSize: 'var(--font-size-lg)',
            fontWeight: 'var(--font-weight-semibold)',
            marginBottom: 'var(--space-4)',
          }}
        >
          Predict preparation quantity
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
            gap: 'var(--space-4)',
            marginBottom: 'var(--space-4)',
          }}
        >
          <SelectField
            label="Food type"
            value={form['Type of Food']}
            options={FOOD_TYPES}
            onChange={set('Type of Food')}
          />
          <SelectField
            label="Event type"
            value={form['Event Type']}
            options={EVENT_TYPES}
            onChange={set('Event Type')}
          />
          <Field label="Number of guests">
            <input
              type="number"
              min={1}
              value={form['Number of Guests']}
              onChange={(e) => set('Number of Guests')(Number(e.target.value))}
              style={inputStyle}
              aria-label="Number of guests"
            />
          </Field>
          <SelectField
            label="Preparation method"
            value={form['Preparation Method']}
            options={PREP_METHODS}
            onChange={set('Preparation Method')}
          />
          <SelectField
            label="Storage conditions"
            value={form['Storage Conditions']}
            options={STORAGE}
            onChange={set('Storage Conditions')}
          />
          <SelectField
            label="Seasonality"
            value={form.Seasonality}
            options={SEASONS}
            onChange={set('Seasonality')}
          />
          <SelectField
            label="Location"
            value={form['Geographical Location']}
            options={LOCATIONS}
            onChange={set('Geographical Location')}
          />
          <SelectField
            label="Pricing"
            value={form.Pricing}
            options={PRICING}
            onChange={set('Pricing')}
          />
          <SelectField
            label="Purchase history"
            value={form['Purchase History']}
            options={PURCHASE}
            onChange={set('Purchase History')}
          />
          <Field label={`Service level: ${(form.service_level * 100).toFixed(0)}%`}>
            <input
              type="range"
              min={0.5}
              max={0.99}
              step={0.01}
              value={form.service_level}
              onChange={(e) => set('service_level')(Number(e.target.value))}
              aria-label="Service level"
              style={{ width: '100%', marginTop: 'var(--space-2)' }}
            />
          </Field>
        </div>
        <button
          onClick={handlePredict}
          disabled={predLoading}
          style={{
            padding: 'var(--space-2) var(--space-6)',
            background: 'var(--color-accent)',
            color: '#fff',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--font-size-sm)',
            fontWeight: 'var(--font-weight-medium)',
            cursor: predLoading ? 'not-allowed' : 'pointer',
            opacity: predLoading ? 0.7 : 1,
          }}
        >
          {predLoading ? 'Calculating...' : 'Get recommendation'}
        </button>
        {predError && (
          <p style={{ color: 'var(--color-waste)', fontSize: 'var(--font-size-sm)', marginTop: 'var(--space-3)' }}>
            {predError}
          </p>
        )}
      </div>

      {/* Prediction result */}
      {prediction && (
        <div
          style={{
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderLeft: '3px solid var(--color-positive)',
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
            Recommendation
          </h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
              gap: 'var(--space-4)',
              marginBottom: 'var(--space-4)',
            }}
          >
            {[
              { label: 'Recommended qty', value: `${prediction.recommended_qty} units` },
              { label: 'Predicted wastage', value: `${prediction.predicted_wastage_units} units` },
              { label: 'Base qty', value: `${prediction.base_qty.toFixed(1)} units` },
              { label: 'Buffer', value: `${prediction.buffer_units.toFixed(1)} units` },
              {
                label: 'Est. wastage %',
                value:
                  prediction.estimated_wastage_pct != null
                    ? `${prediction.estimated_wastage_pct.toFixed(1)}%`
                    : '—',
              },
              { label: 'Service level', value: `${(prediction.service_level * 100).toFixed(0)}%` },
            ].map(({ label, value }) => (
              <div key={label}>
                <p
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-text-secondary)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    marginBottom: 'var(--space-1)',
                  }}
                >
                  {label}
                </p>
                <p
                  style={{
                    fontSize: 'var(--font-size-xl)',
                    fontWeight: 'var(--font-weight-semibold)',
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  {value}
                </p>
              </div>
            ))}
          </div>
          <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
            <p
              style={{
                fontSize: 'var(--font-size-xs)',
                color: 'var(--color-text-secondary)',
                fontWeight: 'var(--font-weight-medium)',
                marginBottom: 'var(--space-2)',
              }}
            >
              Assumptions
            </p>
            {prediction.assumptions.map((a, i) => (
              <p
                key={i}
                style={{
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-secondary)',
                  marginBottom: 'var(--space-1)',
                }}
              >
                {a}
              </p>
            ))}
          </div>

          {/* What-if panel */}
          <div
            style={{
              marginTop: 'var(--space-6)',
              paddingTop: 'var(--space-4)',
              borderTop: '1px solid var(--color-border)',
            }}
          >
            <h4
              style={{
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-semibold)',
                marginBottom: 'var(--space-3)',
              }}
            >
              What-if: reduce preparation
            </h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
              <label
                style={{
                  fontSize: 'var(--font-size-sm)',
                  color: 'var(--color-text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                }}
              >
                Reduce by
                <input
                  type="number"
                  min={1}
                  max={99}
                  value={reducePct}
                  onChange={(e) => setReducePct(Number(e.target.value))}
                  style={{ ...inputStyle, width: '70px' }}
                  aria-label="Reduce preparation by percent"
                />
                %
              </label>
              <button
                onClick={handleWhatIf}
                disabled={whatIfLoading}
                style={{
                  padding: 'var(--space-2) var(--space-4)',
                  background: 'var(--color-warning)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--font-size-sm)',
                  cursor: whatIfLoading ? 'not-allowed' : 'pointer',
                  opacity: whatIfLoading ? 0.7 : 1,
                }}
              >
                {whatIfLoading ? 'Calculating...' : 'Run scenario'}
              </button>
            </div>
            {whatIfError && (
              <p style={{ color: 'var(--color-waste)', fontSize: 'var(--font-size-sm)', marginTop: 'var(--space-2)' }}>
                {whatIfError}
              </p>
            )}
            {whatIfResult && (
              <div style={{ marginTop: 'var(--space-4)' }}>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
                    gap: 'var(--space-3)',
                    marginBottom: 'var(--space-3)',
                  }}
                >
                  {[
                    {
                      label: 'Reduced qty',
                      value: `${whatIfResult.reduced_scenario.reduced_qty} units`,
                    },
                    {
                      label: 'Est. waste saved',
                      value: `${whatIfResult.reduced_scenario.est_waste_units_saved_vs_base.toFixed(1)} units`,
                    },
                    {
                      label: 'Est. unmet demand',
                      value: `${whatIfResult.reduced_scenario.est_unmet_units.toFixed(1)} units`,
                    },
                    {
                      label: 'Est. waste %',
                      value:
                        whatIfResult.reduced_scenario.est_waste_pct != null
                          ? `${whatIfResult.reduced_scenario.est_waste_pct.toFixed(1)}%`
                          : '—',
                    },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <p
                        style={{
                          fontSize: 'var(--font-size-xs)',
                          color: 'var(--color-text-secondary)',
                          textTransform: 'uppercase',
                          letterSpacing: '0.04em',
                          marginBottom: 'var(--space-1)',
                        }}
                      >
                        {label}
                      </p>
                      <p
                        style={{
                          fontSize: 'var(--font-size-lg)',
                          fontWeight: 'var(--font-weight-semibold)',
                          fontVariantNumeric: 'tabular-nums',
                        }}
                      >
                        {value}
                      </p>
                    </div>
                  ))}
                </div>
                <p
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-warning)',
                    fontStyle: 'italic',
                  }}
                >
                  {whatIfResult.caveat}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Historical records table */}
      <ChartCard
        title="Historical event records"
        subtitle="Sortable. All figures from clean records (duplicates excluded)."
        loading={recLoading}
        error={recError}
        empty={!recData || recData.results.length === 0}
      >
        {recData && (
          <>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: 'var(--space-3)',
              }}
            >
              <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                Showing {recData.results.length} of {recData.total.toLocaleString()} records
              </p>
              <button
                onClick={handleExport}
                style={{
                  padding: 'var(--space-1) var(--space-3)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  background: 'transparent',
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-accent)',
                  cursor: 'pointer',
                }}
              >
                Export CSV
              </button>
            </div>
            <DataTable
              columns={[
                { key: 'Type of Food', header: 'Food type' },
                { key: 'Event Type', header: 'Event type' },
                { key: 'Number of Guests', header: 'Guests', numeric: true },
                { key: 'Quantity of Food', header: 'Qty prepared', numeric: true },
                { key: 'Wastage Food Amount', header: 'Wastage', numeric: true },
                {
                  key: 'wastage_pct',
                  header: 'Wastage %',
                  numeric: true,
                  format: (v) => `${Number(v).toFixed(1)}%`,
                },
                { key: 'Preparation Method', header: 'Method' },
                { key: 'Pricing', header: 'Pricing' },
              ]}
              data={recData.results as Record<string, unknown>[]}
            />
          </>
        )}
      </ChartCard>
    </div>
  )
}
