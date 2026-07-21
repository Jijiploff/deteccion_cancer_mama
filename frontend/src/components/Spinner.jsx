import { useLanguage } from '../context/LanguageContext'

export default function Spinner({ label }) {
  const { t } = useLanguage()

  return (
    <div className="flex items-center gap-2.5" role="status">
      <svg
        className="h-4 w-4 animate-spin text-accent"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle
          cx="12"
          cy="12"
          r="9"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeOpacity="0.25"
        />
        <path
          d="M21 12a9 9 0 0 0-9-9"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
        />
      </svg>
      <span className="font-mono text-xs text-muted">{label || t('spinner.processing')}</span>
      <span className="sr-only">{t('spinner.loading')}</span>
    </div>
  )
}