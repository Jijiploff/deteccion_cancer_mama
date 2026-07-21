import { useEffect, useState } from 'react'
import { fetchHistory, checkHealth, API_URL } from '../api'
import { useLanguage } from '../context/LanguageContext'

export default function Dashboard({ username, onLogout }) {
  const { t } = useLanguage()
  const [history, setHistory] = useState([])
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const headers = token ? { Authorization: `Bearer ${token}` } : {}

    Promise.all([
      fetchHistory().catch(() => ({ items: [] })),
      checkHealth().catch(() => null),
    ]).then(([h, he]) => {
      setHistory(h.items || [])
      setHealth(he)
      setLoading(false)
    })
  }, [])

  const totalPredictions = history.length
  const malignant = history.filter((h) => h.label === 'MALIGNANT').length
  const benign = history.filter((h) => h.label === 'BENIGN').length

  return (
    <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-xl font-semibold text-ink">{t('dashboard.title')}</h1>
          <p className="text-sm text-muted">{t('dashboard.welcome', { username })}</p>
        </div>
        <button
          onClick={onLogout}
          className="rounded-lg border border-line px-4 py-2 text-sm text-ink transition-colors hover:bg-line/20"
        >
          {t('dashboard.logout')}
        </button>
      </div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-line bg-surface p-5">
          <p className="text-xs uppercase tracking-wider text-muted">{t('dashboard.total_diagnoses')}</p>
          <p className="mt-1 font-display text-2xl font-semibold text-ink">{totalPredictions}</p>
        </div>
        <div className="rounded-xl border border-line bg-surface p-5">
          <p className="text-xs uppercase tracking-wider text-muted">{t('dashboard.malignant')}</p>
          <p className="mt-1 font-display text-2xl font-semibold text-malignant">{malignant}</p>
        </div>
        <div className="rounded-xl border border-line bg-surface p-5">
          <p className="text-xs uppercase tracking-wider text-muted">{t('dashboard.benign')}</p>
          <p className="mt-1 font-display text-2xl font-semibold text-benign">{benign}</p>
        </div>
        <div className="rounded-xl border border-line bg-surface p-5">
          <p className="text-xs uppercase tracking-wider text-muted">{t('dashboard.api_status')}</p>
          <p className={`mt-1 font-display text-2xl font-semibold ${health ? 'text-benign' : 'text-malignant'}`}>
            {health ? t('dashboard.online') : t('dashboard.offline')}
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-line bg-surface p-5">
        <h2 className="mb-4 font-display text-base font-semibold text-ink">{t('dashboard.history_title')}</h2>
        {loading ? (
          <p className="text-sm text-muted">{t('dashboard.loading')}</p>
        ) : history.length === 0 ? (
          <p className="text-sm text-muted">{t('dashboard.no_history')}</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-line text-xs uppercase tracking-wider text-muted">
                  <th className="pb-2 pr-4 font-medium">{t('dashboard.table.file')}</th>
                  <th className="pb-2 pr-4 font-medium">{t('dashboard.table.result')}</th>
                  <th className="pb-2 pr-4 font-medium">{t('dashboard.table.confidence')}</th>
                  <th className="pb-2 font-medium">{t('dashboard.table.date')}</th>
                </tr>
              </thead>
              <tbody>
                {history.slice(0, 20).map((item) => (
                  <tr key={item.prediction_id} className="border-b border-line/50">
                    <td className="py-2 pr-4 text-ink">{item.filename}</td>
                    <td className={`py-2 pr-4 font-medium ${item.label === 'MALIGNANT' ? 'text-malignant' : 'text-benign'}`}>
                      {item.label}
                    </td>
                    <td className="py-2 pr-4 text-muted">{(item.confidence * 100).toFixed(0)}%</td>
                    <td className="py-2 text-muted">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
