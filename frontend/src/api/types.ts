export interface OverviewData {
  total_events: number
  total_qty_prepared: number
  total_wastage_units: number
  overall_wastage_pct: number
  median_wastage_pct: number
  unique_food_types: number
  unique_event_types: number
}

export interface WasteGroupItem {
  [key: string]: string | number
  n: number
  mean_wastage_pct: number
  median_wastage_pct: number
  std: number
  high_waste_share_pct: number
}

export interface WasteSummary {
  n: number
  mean_wastage_pct: number
  median_wastage_pct: number
  std_wastage_pct: number
  min_wastage_pct: number
  max_wastage_pct: number
  total_units_prepared: number
  total_units_wasted: number
  high_waste_event_count: number
}

export interface HeatmapItem {
  'Type of Food': string
  'Event Type': string
  n: number
  mean_wastage_pct: number
}

export interface ModelMetrics {
  mae: number
  rmse: number
  r2: number
  wape: number
  train_rows: number
  test_rows: number
  split_strategy: string
  plain_language: Record<string, string>
}

export interface BaselineItem {
  name: string
  mae: number
  rmse: number
  r2: number
  wape: number
}

export interface FeatureImportanceItem {
  feature: string
  importance: number
}

export interface InsightItem {
  number: number
  statement: string
  comparison_basis: string
  caveat: string | null
}

export interface PredictRequest {
  'Type of Food': string
  'Number of Guests': number
  'Event Type': string
  'Storage Conditions': string
  'Purchase History': string
  Seasonality: string
  'Preparation Method': string
  'Geographical Location': string
  Pricing: string
  service_level: number
}

export interface PredictResponse {
  recommended_qty: number
  predicted_wastage_units: number
  base_qty: number
  buffer_units: number
  service_level: number
  estimated_wastage_pct: number | null
  per_guest_rate: number
  assumptions: string[]
}

export interface WhatIfResponse {
  base_recommendation: PredictResponse
  reduced_scenario: {
    reduce_pct: number
    reduced_qty: number
    est_waste_units: number
    est_waste_pct: number | null
    est_unmet_units: number
    est_waste_units_saved_vs_base: number
  }
  caveat: string
}

export interface RecommendationsResponse {
  total: number
  page: number
  page_size: number
  results: Record<string, unknown>[]
}

export interface Filters {
  food_type?: string
  event_type?: string
  pricing?: string
  geographical_location?: string
}
