import { useState, useEffect, useCallback, useRef } from 'react'

export interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useApi<T>(fetcher: () => Promise<T>): ApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  // Track mounted state to avoid setting state after unmount
  const mountedRef = useRef(true)

  const run = useCallback(() => {
    setLoading(true)
    setError(null)
    fetcher()
      .then((result) => {
        if (mountedRef.current) {
          setData(result)
          setLoading(false)
        }
      })
      .catch((err: unknown) => {
        if (mountedRef.current) {
          setError(err instanceof Error ? err.message : 'Request failed')
          setLoading(false)
        }
      })
  }, [fetcher])

  useEffect(() => {
    mountedRef.current = true
    run()
    return () => {
      mountedRef.current = false
    }
  }, [run])

  return { data, loading, error, refetch: run }
}
