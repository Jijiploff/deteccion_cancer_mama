export default function Header({ isDark, onToggleDark, username, onLogout, onDashboard }) {
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-surface/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 sm:px-8">
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className="flex h-9 w-9 items-center justify-center rounded-full border border-accent/40 bg-accent/10 font-mono text-sm font-medium text-accent"
          >
            BC
          </span>
          <div className="leading-tight">
            <p className="font-display text-[15px] font-semibold tracking-tight">
              Apoyo Diagnóstico
            </p>
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted">
              Clasificación de mamografías
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {username && (
            <>
              <span className="hidden text-sm text-muted sm:block">{username}</span>
              {onDashboard && (
                <button
                  type="button"
                  onClick={onDashboard}
                  className="rounded-lg border border-line px-3 py-1.5 text-xs text-ink transition-colors hover:bg-line/20"
                >
                  Dashboard
                </button>
              )}
              {onLogout && (
                <button
                  type="button"
                  onClick={onLogout}
                  className="rounded-lg border border-line px-3 py-1.5 text-xs text-ink transition-colors hover:bg-line/20"
                >
                  Salir
                </button>
              )}
            </>
          )}

          <button
            type="button"
            onClick={() => onToggleDark(!isDark)}
            aria-pressed={isDark}
            aria-label={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
            className="group flex h-9 w-9 items-center justify-center rounded-full border border-line text-ink transition-colors hover:border-accent/50 hover:text-accent"
          >
            {isDark ? (
              <svg viewBox="0 0 24 24" fill="none" className="h-[18px] w-[18px]" aria-hidden="true">
                <circle cx="12" cy="12" r="4.5" stroke="currentColor" strokeWidth="1.6" />
                <path
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                  d="M12 2.5v2M12 19.5v2M21.5 12h-2M4.5 12h-2M18.4 5.6l-1.4 1.4M7 17l-1.4 1.4M18.4 18.4L17 17M7 7 5.6 5.6"
                />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" className="h-[18px] w-[18px]" aria-hidden="true">
                <path
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinejoin="round"
                  d="M20 14.2A8.5 8.5 0 1 1 9.8 4a6.7 6.7 0 0 0 10.2 10.2Z"
                />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}
