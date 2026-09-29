import { useSearchParams } from 'react-router-dom'
import type { Filters } from '../api/types'

const FILTER_KEYS: (keyof Filters)[] = [
  'food_type',
  'event_type',
  'pricing',
  'geographical_location',
]

export function useFilters(): [Filters, (next: Filters) => void] {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters: Filters = {}
  for (const key of FILTER_KEYS) {
    const val = searchParams.get(key)
    if (val) filters[key] = val
  }

  const setFilters = (next: Filters) => {
    const params = new URLSearchParams(searchParams)
    for (const key of FILTER_KEYS) {
      if (next[key]) {
        params.set(key, next[key]!)
      } else {
        params.delete(key)
      }
    }
    setSearchParams(params)
  }

  return [filters, setFilters]
}
