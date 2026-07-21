import { useLanguage } from '../context/LanguageContext'

export default function Hero() {
  const { t } = useLanguage()

  return (
    <section className="mx-auto max-w-6xl px-5 pb-10 pt-14 sm:px-8 sm:pt-20">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-accent">
        {t('hero.badge')}
      </p>
      <h1 className="mt-4 max-w-2xl font-display text-3xl font-semibold leading-[1.15] tracking-tight sm:text-5xl">
        {t('hero.heading1')}
        <br />
        {t('hero.heading2')}
      </h1>
      <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-muted">
        {t('hero.description')}
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
          {t('hero.note')}
        </span>
      </div>
    </section>
  )
}