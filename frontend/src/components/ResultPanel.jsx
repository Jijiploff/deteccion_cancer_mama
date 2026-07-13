import Spinner from './Spinner'
import ConfidenceGauge from './ConfidenceGauge'

function ConsensusBadge({ consensus }) {
  const styles = {
    full_agreement: 'bg-benign/15 text-benign border-benign/30',
    majority: 'bg-accent/15 text-accent border-accent/30',
    disagreement: 'bg-malignant/15 text-malignant border-malignant/30',
  }
  const labels = {
    full_agreement: 'Consenso total',
    majority: 'Mayoría',
    disagreement: 'Sin consenso',
  }
  return (
    <span className={`inline-block rounded-full border px-3 py-1 font-mono text-[11px] ${styles[consensus] || styles.disagreement}`}>
      {labels[consensus] || consensus}
    </span>
  )
}

function StatusDot({ status }) {
  const color = status === 'success' ? 'bg-benign' : status === 'error' ? 'bg-malignant' : 'bg-muted'
  return <span className={`inline-block h-2 w-2 rounded-full ${color}`} />
}

export default function ResultPanel({ status, result, errorMessage, onRetry }) {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="font-display text-sm font-semibold tracking-tight">
        Resultado
      </h2>

      <div className="flex min-h-[240px] flex-col rounded-xl border border-line bg-surface px-5 py-6">
        {status === 'idle' && (
          <div className="flex flex-1 items-center justify-center">
            <p className="font-mono text-xs text-muted">
              Sube una mamografía para obtener el análisis.
            </p>
          </div>
        )}

        {status === 'loading' && (
          <div className="flex flex-1 items-center justify-center">
            <Spinner label="Analizando imagen…" />
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
                {result.label === 'BENIGN' ? 'BENIGNO' : 'MALIGNO'}
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
                    <th className="pb-2 pr-3 font-medium">Modelo</th>
                    <th className="pb-2 pr-3 font-medium">Diagnóstico</th>
                    <th className="pb-2 pr-3 font-medium">Confianza</th>
                    <th className="pb-2 pr-3 font-medium">Tiempo</th>
                    <th className="pb-2 font-medium">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {result.models.map((m, i) => (
                    <tr key={i} className="border-b border-line/50">
                      <td className="py-2.5 pr-3 text-ink">{m.model_name}</td>
                      <td className="py-2.5 pr-3">
                        <span className={m.model_label === 'MALIGNANT' ? 'text-malignant font-semibold' : 'text-benign font-semibold'}>
                          {m.model_label === 'BENIGN' ? 'Benigno' : 'Maligno'}
                        </span>
                      </td>
                      <td className="py-2.5 pr-3 text-ink">
                        {(m.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 pr-3 text-muted">
                        {m.processing_time_ms.toFixed(0)} ms
                      </td>
                      <td className="py-2.5">
                        <StatusDot status={m.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="font-mono text-[11px] text-muted">
              Procesado en {result.processing_time_ms.toFixed(1)} ms
            </p>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-1 flex-col items-center justify-center gap-4">
            <p
              role="alert"
              className="font-mono text-[13px] text-malignant"
            >
              {errorMessage || 'Error al procesar la imagen.'}
            </p>
            <button
              type="button"
              onClick={onRetry}
              className="rounded-lg border border-line px-4 py-2 font-mono text-xs text-ink transition-colors hover:border-accent hover:text-accent"
            >
              Reintentar
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
