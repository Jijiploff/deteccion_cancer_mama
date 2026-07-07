import { useCallback, useEffect, useState } from 'react'
import { fetchHistory, clearHistory as clearHistoryApi } from '../api'

export function useHistory() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchHistory()
      setItems(data.items)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const clear = useCallback(async () => {
    await clearHistoryApi()
    setItems([])
  }, [])

  return { items, loading, error, reload: load, clear }
}