# Spec 4: dashboard — Design

## Palette (CSS variables)

```css
--color-bg:           #f7f6f3;   /* warm off-white, not pure white */
--color-surface:      #ffffff;
--color-border:       #e2e0db;
--color-text-primary: #1a1917;
--color-text-secondary: #6b6963;
--color-accent:       #2c6e8a;   /* one primary — steel blue */
--color-waste:        #c0392b;   /* waste colour, consistent everywhere */
--color-positive:     #2e7d52;   /* savings / good outcomes */
--color-warning:      #b45309;   /* caution states */
```

No gradients. No glassmorphism. No box-shadows heavier than `0 1px 3px rgba(0,0,0,0.08)`.

## Typography

Inter with system-ui fallback: `'Inter', system-ui, -apple-system, sans-serif`.

```css
--font-size-xs:   0.75rem;
--font-size-sm:   0.875rem;
--font-size-base: 1rem;
--font-size-lg:   1.125rem;
--font-size-xl:   1.25rem;
--font-size-2xl:  1.5rem;
--font-size-3xl:  1.875rem;

--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
```

## Spacing scale

```css
--space-1: 0.25rem;   --space-2: 0.5rem;   --space-3: 0.75rem;
--space-4: 1rem;      --space-6: 1.5rem;   --space-8: 2rem;
--space-12: 3rem;     --space-16: 4rem;
```

## Pages

1. **Overview** (`/`) — total events, prepared, wasted, overall wastage %, insights list
2. **Waste Analysis** (`/waste`) — by food type, by event type, by pricing, heatmap
3. **Demand** (`/demand`) — by guest band, by seasonality, by preparation method
4. **Promotions & Events** (`/events`) — pricing impact, event type breakdown, seasonality
5. **Model** (`/model`) — metrics with plain language, baseline comparison, feature importance
6. **Recommendations** (`/recommendations`) — sortable table, predict form, what-if panel

## Component inventory

| Component | Props | Notes |
|---|---|---|
| StatCard | label, value, unit?, change?, variant? | variant: default, waste, positive |
| DataTable | columns, data, sortable? | right-aligned numerics, sticky header |
| ChartCard | title, children | wraps any Recharts chart with title + loading/empty/error |
| FilterBar | filters, onChange | food_type, event_type, pricing, location dropdowns |
| InsightCard | number, statement, comparison_basis, caveat? | — |
| LoadingSpinner | — | centred, subtle |
| EmptyState | message | — |
| ErrorState | message, onRetry? | — |

## Data fetching

Custom `useApi` hook wrapping `fetch`. Returns `{ data, loading, error }`.
No external data-fetching library — keep the dependency count low.
All API calls go through `src/api/client.ts` which reads `VITE_API_URL` from env.

## URL filters

Global filters (food_type, event_type, pricing, geographical_location) live in
the URL query string and are read/written via `URLSearchParams`. FilterBar syncs
with the URL on every change.

## Chart rules

- Recharts only. No D3 direct manipulation.
- All axes labelled. Numbers formatted: `6.9%` not `6.900000001%`.
- Waste bars always `var(--color-waste)`. Positive bars `var(--color-accent)`.
- No 3D. No rainbow. No pie charts.
- Chart titles state what is shown and the unit.
- Every ChartCard has loading, empty, and error states.
