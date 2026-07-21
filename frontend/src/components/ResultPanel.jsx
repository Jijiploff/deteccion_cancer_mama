import Spinner from './Spinner'
import ConfidenceGauge from './ConfidenceGauge'
import { useLanguage } from '../context/LanguageContext'

function ConsensusBadge({ consensus }) {
  const { t } = useLanguage()
  const styles = {
    full_agreement: 'bg-benign/15 text-benign border-benign/30',
    majority: 'bg-accent/15 text-accent border-accent/30',
    disagreement: 'bg-malignant/15 text-malignant border-malignant/30',
  }
  const key = consensus || 'disagreement'
  return (
    <span className={`inline-block rounded-full border px-3 py-1 font-mono text-[11px] ${styles[key] || styles.disagreement}`}>
      {t(`result.consensus.${key}`)}
    </span>
  )
}

function StatusDot({ status }) {
  const color = status === 'success' ? 'bg-benign' : status === 'error' ? 'bg-malignant' : 'bg-muted'
  return <span className={`inline-block h-2 w-2 rounded-full ${color}`} />
}

function formatPercent(value) {
  return typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : 'N/D'
}

function statusLabel(status, tFn) {
  if (status === 'success') return tFn('result.status_executed')
  if (status === 'error') return tFn('result.status_error')
  return tFn('result.status_unavailable')
}

export default function ResultPanel({ status, result, errorMessage, onRetry }) {
  const { t } = useLanguage()

  return (
    <div className="flex flex-col gap-3">
      <h2 className="font-display text-sm font-semibold tracking-tight">
        {t('result.title')}
      </h2>

      <div className="flex min-h-[240px] flex-col rounded-xl border border-line bg-surface px-5 py-6">
        {status === 'idle' && (
          <div className="flex flex-1 items-center justify-center">
            <p className="font-mono text-xs text-muted">
              {t('result.idle_message')}
            </p>
          </div>
        )}

        {status === 'loading' && (
          <div className="flex flex-1 items-center justify-center">
            <Spinner label={t('result.loading')} />
          </div>
        )}

        {status === 'success' && result && (
          <div className="flex w-full flex-col gap-5">
            <div className="flex items-center justify-between">
              <span
                className={`inline-block rounded-full px-4 py-1.5 font-display text-[15px] font-semibold tracking-tight ${
                  result.label === 'BENIGN'
                    ? 'bg-benign/15 text-benign'
                    : 'bg-malignant/15 text-malignant'
                }`}
              >
                {result.label === 'BENIGN' ? t('result.benign_badge') : t('result.malignant_badge')}
              </span>
              <ConsensusBadge consensus={result.consensus} />
            </div>

            <ConfidenceGauge
              benign={result.probabilities.benign}
              malignant={result.probabilities.malignant}
            />

            {result.warning && (
              <p
                role="alert"
                className="rounded-lg border border-malignant/30 bg-malignant/5 px-3 py-2 font-mono text-[12px] text-malignant"
              >
                {result.warning}
              </p>
            )}

            <div className="overflow-x-auto">
              <table className="w-full border-collapse font-mono text-[11px]">
                <thead>
                  <tr className="border-b border-line text-left text-muted">
                    <th className="pb-2 pr-3 font-medium">{t('result.table.model')}</th>
                    <th className="pb-2 pr-3 font-medium">{t('result.table.diagnosis')}</th>
                    <th className="pb-2 pr-3 font-medium">{t('result.table.prob_benign')}</th>
                    <th className="pb-2 pr-3 font-medium">{t('result.table.prob_malignant')}</th>
                    <th className="pb-2 pr-3 font-medium">{t('result.table.confidence')}</th>
                    <th className="pb-2 pr-3 font-medium">{t('result.table.time')}</th>
                    <th className="pb-2 font-medium">{t('result.table.status')}</th>
                  </tr>
                </thead>
                <tbody>
                  {result.models.map((m, i) => (
                    <tr key={i} className="border-b border-line/50">
                      <td className="py-2.5 pr-3 text-ink">{m.model_name}</td>
                      <td className="py-2.5 pr-3">
                        {m.model_label ? (
                          <span className={m.model_label === 'MALIGNANT' ? 'text-malignant font-semibold' : 'text-benign font-semibold'}>
                            {m.model_label === 'BENIGN' ? t('result.model_benign') : t('result.model_malignant')}
                          </span>
                        ) : (
                          <span className="text-muted">{t('result.na')}</span>
                        )}
                      </td>
                      <td className="py-2.5 pr-3 text-ink">
                        {formatPercent(m.benign_prob)}
                      </td>
                      <td className="py-2.5 pr-3 text-ink">
                        {formatPercent(m.malignant_prob)}
                      </td>
                      <td className="py-2.5 pr-3 text-ink">
                        {formatPercent(m.confidence)}
                      </td>
                      <td className="py-2.5 pr-3 text-muted">
                        {typeof m.processing_time_ms === 'number' ? `${m.processing_time_ms.toFixed(0)} ms` : t('result.na')}
                      </td>
                      <td className="py-2.5">
                        <div className="flex items-center gap-2">
                          <StatusDot status={m.status} />
                          <span className="text-[10px] text-muted">{statusLabel(m.status, t)}</span>
                        </div>
                        {m.error && <p className="mt-1 max-w-[220px] text-[10px] text-muted">{m.error}</p>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="font-mono text-[11px] text-muted">
              {t('result.processed', { time: result.processing_time_ms.toFixed(1) })}
            </p>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-1 flex-col items-center justify-center gap-4">
            <p
              role="alert"
              className="font-mono text-[13px] text-malignant"
            >
              {errorMessage || t('result.error_message')}
            </p>
            <button
              type="button"
              onClick={onRetry}
              className="rounded-lg border border-line px-4 py-2 font-mono text-xs text-ink transition-colors hover:border-accent hover:text-accent"
            >
              {t('result.retry_button')}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
