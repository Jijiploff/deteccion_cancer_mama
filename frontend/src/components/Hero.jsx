export default function Hero() {
  return (
    <section className="mx-auto max-w-6xl px-5 pb-10 pt-14 sm:px-8 sm:pt-20">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-accent">
        Sistema de apoyo diagnóstico · Deep Learning
      </p>
      <h1 className="mt-4 max-w-2xl font-display text-3xl font-semibold leading-[1.15] tracking-tight sm:text-5xl">
        Lee la mamografía con detalle.
        <br />
        Decide con criterio clínico.
      </h1>
      <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-muted">
        Sube una imagen de mamografía y el modelo entrenado con CBIS-DDSM estima
        la probabilidad de hallazgos benignos o malignos en segundos. Cada
        resultado incluye su nivel de confianza para apoyar, no reemplazar, el
        criterio del especialista.
      </p>
      <div
        role="note"
        className="mt-6 inline-flex max-w-xl items-start gap-2.5 rounded-lg border border-line bg-surface px-4 py-3 text-[13px] leading-relaxed text-muted"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6" />
          <path d="M12 8v5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          <circle cx="12" cy="16" r="0.9" fill="currentColor" />
        </svg>
        <span>
          Herramienta de apoyo, no un diagnóstico definitivo. La confirmación
          siempre corresponde a un profesional médico calificado.
        </span>
      </div>
    </section>
  )
}