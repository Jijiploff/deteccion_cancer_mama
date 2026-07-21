import { useLanguage } from '../context/LanguageContext'

export default function ConfidenceGauge({ benign, malignant }) {
  const { t } = useLanguage()
  const benignPct = Math.round(benign * 100)
  const malignantPct = Math.round(malignant * 100)

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between font-mono text-[11px] text-muted">
        <span>{t('gauge.benign')}</span>
        <span>{t('gauge.malignant')}</span>
      </div>
      <div
        role="img"
        aria-label={t('gauge.aria_label', { benign: benignPct, malignant: malignantPct })}
        className="flex h-3 w-full overflow-hidden rounded-full border border-line"
      >
        <div
          className="h-full bg-benign transition-all duration-700 ease-out"
          style={{ width: `${benignPct}%` }}
        />
        <div
          className="h-full bg-malignant transition-all duration-700 ease-out"
          style={{ width: `${malignantPct}%` }}
        />
      </div>
      <div className="flex items-center justify-between font-mono text-[13px]">
        <span className="text-benign">{benignPct}%</span>
        <span className="text-malignant">{malignantPct}%</span>
      </div>
    </div>
  )
}