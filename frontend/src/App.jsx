import { useCallback, useEffect, useState } from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import UploadPanel from './components/UploadPanel'
import ResultPanel from './components/ResultPanel'
import HistoryList from './components/HistoryList'
import Footer from './components/Footer'
import { useDarkMode } from './hooks/useDarkMode'
import { useHistory } from './hooks/useHistory'
import { predictImage, checkHealth } from './api'

export default function App() {
  const [isDark, setIsDark] = useDarkMode()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [result, setResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)
  const [apiAvailable, setApiAvailable] = useState(true)

  const { items: historyItems, loading: historyLoading, reload, clear } = useHistory()

  useEffect(() => {
    checkHealth()
      .then((data) => setApiAvailable(data.model_loaded))
      .catch(() => setApiAvailable(false))
  }, [])

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const runPrediction = useCallback(async (selectedFile) => {
    setFile(selectedFile)
    setPreviewUrl(URL.createObjectURL(selectedFile))
    setStatus('loading')
    setErrorMessage(null)

    try {
      const data = await predictImage(selectedFile)
      setResult(data)
      setStatus('success')
      reload()
    } catch (err) {
      setErrorMessage(err.message || 'Ocurrió un error inesperado.')
      setStatus('error')
    }
  }, [reload])

  const handleRetry = () => {
    if (file) runPrediction(file)
  }

  return (
    <div className="min-h-screen bg-bg font-body text-ink">
      <Header isDark={isDark} onToggleDark={setIsDark} />
      <main>
        <Hero />

        {!apiAvailable && (
          <div className="mx-auto max-w-6xl px-5 sm:px-8">
            <p
              role="alert"
              className="mb-6 rounded-lg border border-malignant/30 bg-malignant/5 px-4 py-3 font-mono text-[12px] text-malignant"
            >
              El servicio de diagnóstico no está disponible en este momento. Intenta más tarde.
            </p>
          </div>
        )}

        <section className="mx-auto grid max-w-6xl gap-8 px-5 pb-16 sm:px-8 md:grid-cols-2 md:gap-6">
          <UploadPanel
            onFileSelected={runPrediction}
            previewUrl={previewUrl}
            isLoading={status === 'loading'}
            filename={file?.name}
          />
          <ResultPanel
            status={status}
            result={result}
            errorMessage={errorMessage}
            onRetry={handleRetry}
          />
        </section>

        <HistoryList items={historyItems} loading={historyLoading} onClear={clear} />
      </main>
      <Footer />
    </div>
  )
}