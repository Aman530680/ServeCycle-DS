import { apiFetch, buildQuery } from './client'
import type {
  OverviewData,
  WasteGroupItem,
  WasteSummary,
  HeatmapItem,
  ModelMetrics,
  BaselineItem,
  FeatureImportanceItem,
  InsightItem,
  PredictRequest,
  PredictResponse,
  WhatIfResponse,
  RecommendationsResponse,
  Filters,
} from './types'

export const api = {
  overview: (f: Filters = {}) =>
    apiFetch<OverviewData>(`/api/overview${buildQuery(f)}`),

  wasteSummary: (f: Filters = {}) =>
    apiFetch<WasteSummary>(`/api/waste/summary${buildQuery(f)}`),

  wasteByFoodType: (f: Filters = {}) =>
    apiFetch<WasteGroupItem[]>(`/api/waste/by-food-type${buildQuery(f)}`),

  wasteByEventType: (f: Filters = {}) =>
    apiFetch<WasteGroupItem[]>(`/api/waste/by-event-type${buildQuery(f)}`),

  wasteByPricing: (f: Filters = {}) =>
    apiFetch<WasteGroupItem[]>(`/api/waste/by-pricing${buildQuery(f)}`),

  wasteByLocation: (f: Filters = {}) =>
    apiFetch<WasteGroupItem[]>(`/api/waste/by-location${buildQuery(f)}`),

  wasteByPrepMethod: (f: Filters = {}) =>
    apiFetch<WasteGroupItem[]>(`/api/waste/by-preparation-method${buildQuery(f)}`),

  wastageHeatmap: () =>
    apiFetch<HeatmapItem[]>('/api/waste/heatmap'),

  demandTrends: () =>
    apiFetch<WasteGroupItem[]>('/api/demand/trends'),

  demandByWeather: () =>
    apiFetch<WasteGroupItem[]>('/api/demand/by-weather'),

  demandByWeekday: () =>
    apiFetch<WasteGroupItem[]>('/api/demand/by-weekday'),

  promotionsImpact: () =>
    apiFetch<WasteGroupItem[]>('/api/promotions/impact'),

  eventsImpact: () =>
    apiFetch<{ by_event_type: WasteGroupItem[]; by_seasonality: WasteGroupItem[] }>(
      '/api/events/impact',
    ),

  modelMetrics: () =>
    apiFetch<ModelMetrics>('/api/model/metrics'),

  modelBaselines: () =>
    apiFetch<BaselineItem[]>('/api/model/baselines'),

  modelFeatures: () =>
    apiFetch<{ features: string[]; target: string; excluded: string[]; best_params: Record<string, unknown> }>(
      '/api/model/features',
    ),

  modelImportance: () =>
    apiFetch<FeatureImportanceItem[]>('/api/model/importance'),

  insights: () =>
    apiFetch<InsightItem[]>('/api/insights'),

  recommendations: (food_type?: string, event_type?: string, page = 1, page_size = 50) =>
    apiFetch<RecommendationsResponse>(
      `/api/recommendations${buildQuery({ food_type, event_type, page, page_size })}`,
    ),

  predictDemand: (body: PredictRequest) =>
    apiFetch<PredictResponse>('/api/predict-demand', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  whatIf: (context: PredictRequest, reduce_pct: number) =>
    apiFetch<WhatIfResponse>('/api/what-if', {
      method: 'POST',
      body: JSON.stringify({ context, reduce_pct }),
    }),
}
