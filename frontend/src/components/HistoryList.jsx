export default function HistoryList({ items, loading, onClear }) {
  return (
    <section className="mx-auto max-w-6xl px-5 pb-20 pt-4 sm:px-8">
      <div className="flex items-center justify-between border-b border-line pb-3">
        <h2 className="font-display text-sm font-semibold tracking-tight">
          Historial reciente
        </h2>
        {items.length > 0 && (
          <button
            type="button"
            onClick={onClear}
            className="font-mono text-[11px] uppercase tracking-wider text-muted transition-colors hover:text-malignant"
          >
            Limpiar
          </button>
        )}
      </div>

      {loading && (
        <p className="py-6 font-mono text-xs text-muted">Cargando historial…</p>
      )}

      {!loading && items.length === 0 && (
        <p className="py-6 text-[13px] text-muted">
          Aún no hay diagnósticos registrados en esta sesión del servidor.
        </p>
      )}

      {!loading && items.length > 0 && (
        <ul className="divide-y divide-line">
          {items.map((item) => {
            const isMalignant = item.label === 'MALIGNANT'
            return (
              <li key={item.prediction_id} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <span
                    aria-hidden="true"
                    className={`h-2 w-2 flex-shrink-0 rounded-full ${
                      isMalignant ? 'bg-malignant' : 'bg-benign'
                    }`}
                  />
                  <span className="truncate font-body text-sm text-ink">
                    {item.filename}
                  </span>
                </div>
                <div className="flex flex-shrink-0 items-center gap-4 font-mono text-[11px] text-muted">
                  <span className={isMalignant ? 'text-malignant' : 'text-benign'}>
                    {isMalignant ? 'Maligno' : 'Benigno'} · {Math.round(item.confidence * 100)}%
                  </span>
                  <span>{new Date(item.timestamp).toLocaleString('es-PE')}</span>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}