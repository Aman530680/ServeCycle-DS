# Spec 4: dashboard — Tasks

## T1 — Vite + React + TypeScript scaffold
npm create vite, strict tsconfig, install recharts.
Design tokens in src/styles/tokens.css.
Traces to: design palette, typography, spacing.

## T2 — Shared components
StatCard, DataTable, ChartCard, FilterBar, InsightCard,
LoadingSpinner, EmptyState, ErrorState.
Traces to: design component inventory.

## T3 — API client
src/api/client.ts — typed fetch wrapper.
src/api/endpoints.ts — one function per endpoint.
src/hooks/useApi.ts — { data, loading, error } hook.
Traces to: design data fetching.

--- REVIEW: app shell and design tokens ---

## T4 — Overview page
StatCards (total events, wastage %, units prepared, units wasted).
InsightCards list. FilterBar synced to URL.
Traces to: spec page 1.

## T5 — Waste Analysis page
Bar charts: by food type, by event type, by pricing.
Heatmap (recharts ResponsiveContainer + custom cells).
Traces to: spec page 2.

--- REVIEW: Overview and Waste pages ---

## T6 — Demand page
Guest band chart, seasonality chart, preparation method chart.
Traces to: spec page 3.

## T7 — Promotions & Events page
Pricing impact bars, event type bars, seasonality bars.
Sample sizes visible. Caveats shown.
Traces to: spec page 4.

## T8 — Model page
Metrics with plain language explanations, baseline comparison table,
feature importance horizontal bar chart, actual-vs-predicted image.
Traces to: spec page 5.

## T9 — Recommendations page
Sortable, filterable table with pagination. Predict form.
What-if panel: reduce_pct slider, displays reduced scenario + caveat.
CSV export button.
Traces to: spec page 6.

--- REVIEW: remaining pages ---

## T10 — Frontend component tests (Vitest + RTL)
StatCard, DataTable, FilterBar, InsightCard — loading/empty/error states.
Traces to: spec testing section.

## T11 — Documentation
README.md, reports/insights.md, reports/action_plan.md,
docs/decisions.md. requirements.txt.
Traces to: spec documentation section.

--- REVIEW: testing and documentation ---
