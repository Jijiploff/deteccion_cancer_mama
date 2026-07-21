import { useState } from 'react'
import { API_URL } from '../api'
import { useLanguage } from '../context/LanguageContext'

export default function Login({ onLogin }) {
  const { t } = useLanguage()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || t('login.invalid_credentials'))
      }

      const data = await res.json()
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', data.username)
      onLogin(data.access_token, data.username)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm rounded-xl border border-line bg-surface p-8 shadow-lg">
        <div className="mb-6 text-center">
          <span
            aria-hidden="true"
            className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-accent/40 bg-accent/10 font-mono text-lg font-medium text-accent"
          >
            BC
          </span>
          <h1 className="font-display text-xl font-semibold text-ink">
            {t('login.title')}
          </h1>
          <p className="mt-1 font-mono text-[11px] uppercase tracking-wider text-muted">
            {t('login.subtitle')}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="mb-1 block text-sm font-medium text-ink">
              {t('login.username_label')}
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-lg border border-line bg-bg px-3 py-2 text-sm text-ink placeholder:text-muted focus:border-accent focus:outline-none"
              placeholder={t('login.username_placeholder')}
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-ink">
              {t('login.password_label')}
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-line bg-bg px-3 py-2 text-sm text-ink placeholder:text-muted focus:border-accent focus:outline-none"
              placeholder={t('login.password_placeholder')}
              required
            />
          </div>

          {error && (
            <p role="alert" className="rounded-lg border border-malignant/30 bg-malignant/5 px-3 py-2 text-xs text-malignant">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent/90 disabled:opacity-50"
          >
            {loading ? t('login.logging_in') : t('login.login_button')}
          </button>
        </form>
      </div>
    </div>
  )
}
