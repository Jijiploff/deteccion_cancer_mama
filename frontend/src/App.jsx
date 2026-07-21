import { useCallback, useEffect, useState } from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import UploadPanel from './components/UploadPanel'
import ClinicalForm, { WISCONSIN_DEFAULTS } from './components/ClinicalForm'
import ResultPanel from './components/ResultPanel'
import HistoryList from './components/HistoryList'
import Dashboard from './components/Dashboard'
import Login from './components/Login'
import Footer from './components/Footer'
import HelpChatbot from './components/Helpchatbot'
import { useDarkMode } from './hooks/useDarkMode'
import { useHistory } from './hooks/useHistory'
import { predictImage, checkHealth } from './api'

const INITIAL_WISCONSIN = Object.fromEntries(
  Object.entries(WISCONSIN_DEFAULTS).map(([k, v]) => [k, String(v)])
)

export default function App() {
  const [isDark, setIsDark] = useDarkMode()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)
  const [apiAvailable, setApiAvailable] = useState(true)
  const [wisconsinData, setWisconsinData] = useState({ ...INITIAL_WISCONSIN })

  const [token, setToken] = useState(localStorage.getItem('token'))
  const [username, setUsername] = useState(localStorage.getItem('username'))
  const [page, setPage] = useState(token ? 'home' : 'login')

  const { items: historyItems, loading: historyLoading, reload, clear } = useHistory()

  useEffect(() => {
    checkHealth()
      .then((data) => setApiAvailable(data.models_loaded?.CNN || false))
      .catch(() => setApiAvailable(false))
  }, [])

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const handleLogin = (t, u) => {
    setToken(t)
    setUsername(u)
    setPage('home')
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setToken(null)
    setUsername(null)
    setPage('login')
  }

  const runPrediction = useCallback(async (selectedFile) => {
    setFile(selectedFile)
    setPreviewUrl(URL.createObjectURL(selectedFile))
    setStatus('loading')
    setErrorMessage(null)

    try {
      const wisconsinPayload = {}
      for (const [key, value] of Object.entries(wisconsinData)) {
        if (key in WISCONSIN_DEFAULTS && value !== '' && value !== undefined) {
          wisconsinPayload[key] = value
        }
      }

      const data = await predictImage(selectedFile, wisconsinPayload)
      setResult(data)
      setStatus('success')
      reload()
    } catch (err) {
      setErrorMessage(err.message || 'Ocurrió un error inesperado.')
      setStatus('error')
    }
  }, [wisconsinData, reload])

  const handleRetry = () => {
    if (file) runPrediction(file)
  }

  const handleWisconsinChange = (key, value) => {
    setWisconsinData((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <div className="min-h-screen bg-bg font-body text-ink">
      <Header
        isDark={isDark}
        onToggleDark={setIsDark}
        username={username}
        onLogout={() => { handleLogout(); setPage('login') }}
        onDashboard={() => setPage('dashboard')}
      />
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
          <div className="flex flex-col gap-6">
            <UploadPanel
              onFileSelected={runPrediction}
              previewUrl={previewUrl}
              isLoading={status === 'loading'}
              filename={file?.name}
            />
            <ClinicalForm
              show={true}
              formData={wisconsinData}
              onChange={handleWisconsinChange}
            />
          </div>
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
      <HelpChatbot />
    </div>
  )
}
