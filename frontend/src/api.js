// URL del backend. En Vercel, define VITE_API_URL en las variables de entorno del proyecto.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    let detail = `Error ${response.status}`
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch {
      // el cuerpo no era JSON, nos quedamos con el mensaje genérico
    }
    throw new ApiError(detail, response.status)
  }
  return response.json()
}

export async function checkHealth() {
  const response = await fetch(`${API_URL}/health`)
  return handleResponse(response)
}

export async function predictImage(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    body: formData,
  })
  return handleResponse(response)
}

export async function fetchHistory() {
  const response = await fetch(`${API_URL}/history`)
  return handleResponse(response)
}

export async function clearHistory() {
  const response = await fetch(`${API_URL}/history`, { method: 'DELETE' })
  return handleResponse(response)
}

export { ApiError }