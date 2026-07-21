import { useLanguage } from '../context/LanguageContext'

export default function Footer() {
  const { t } = useLanguage()

  return (
    <footer className="border-t border-line px-5 py-8 sm:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-1 font-mono text-[11px] text-muted">
        <p>{t('footer.line1')}</p>
        <p>{t('footer.line2')}</p>
      </div>
    </footer>
  )
}