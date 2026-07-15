import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

/**
 * Base de conocimiento del asistente.
 * Cada entrada tiene palabras clave (sin tildes, en minúscula) y una respuesta.
 * El motor de búsqueda es local (no requiere backend) para que el asistente
 * funcione siempre, incluso si el servicio de predicción está offline.
 */
const FAQ = [
  {
    keywords: ['subir', 'cargar', 'arrastrar', 'archivo', 'jpg', 'png', 'foto', 'mamografia', 'imagen'],
    answer:
      'Para analizar una mamografía, arrastra el archivo al visor de imagen o haz clic sobre él para seleccionarlo desde tu equipo. Se aceptan JPG o PNG de hasta 5MB. El análisis comienza automáticamente al soltar o seleccionar el archivo.',
  },
  {
    keywords: ['assessment', 'bi-rads', 'birads'],
    answer:
      'Assessment es la categoría BI-RADS (0 a 6) asignada por el radiólogo. Es un dato clínico opcional: si lo completas junto con Subtlety, Edad y Densidad, se activan los modelos Ensemble y XGBoost además del modelo de imagen.',
  },
  {
    keywords: ['subtlety', 'sutileza'],
    answer:
      'Subtlety mide qué tan sutil o evidente es el hallazgo en la imagen, en una escala de 1 (muy sutil) a 5 (muy evidente).',
  },
  {
    keywords: ['densidad', 'density'],
    answer:
      'La densidad mamaria se califica de 1 (mayormente grasa) a 4 (extremadamente densa), según BI-RADS. Un tejido más denso puede dificultar la lectura de la mamografía.',
  },
  {
    keywords: ['edad'],
    answer: 'La edad de la paciente es un dato clínico adicional que ayuda a contextualizar el resultado junto con los otros campos.',
  },
  {
    keywords: ['campos clinicos', 'datos clinicos', 'significan los campos', 'que significan los campos'],
    answer:
      'Los campos clínicos son 4 datos que puedes ingresar junto con la imagen: Assessment (categoría BI-RADS de 0 a 6 asignada por el radiólogo), Subtlety (qué tan evidente es el hallazgo, de 1 a 5), Edad de la paciente, y Densidad mamaria (de 1, mayormente grasa, a 4, extremadamente densa). Completar estos 4 campos activa los modelos Ensemble y XGBoost además del modelo de imagen. También existe una sección opcional de 30 campos Wisconsin con medidas morfológicas del núcleo celular, que vienen pre-rellenadas con valores promedio y puedes ajustar si tienes datos propios.',
  },
  {
    keywords: ['wisconsin', '30 campos', 'caracteristicas', 'radio', 'textura', 'perimetro', 'concavidad'],
    answer:
      'Los 30 campos Wisconsin son medidas morfológicas del núcleo celular (radio, textura, perímetro, área, suavidad, concavidad, etc.), cada una en su versión media, error estándar y peor caso. Son opcionales y se abren en la sección "Características Wisconsin": vienen pre-rellenadas con los promedios del dataset, y puedes ajustarlas si cuentas con valores propios.',
  },
  {
    keywords: ['que modelos usan', 'modelos que usa', 'cuantos modelos', 'modelos de ia', 'que ia usan', 'modelos', 'cnn', 'ensemble', 'xgboost', 'cuantos son'],
    answer:
      'El sistema combina 6 modelos: 2 que analizan exclusivamente la imagen (CNN y CCD), 2 que usan datos clínicos (Ensemble y XGBoost con datos de Wisconsin), y 2 modelos híbridos. En la tabla de resultados ves el diagnóstico de cada modelo (Benigno/Maligno), la probabilidad y el nivel de confianza. El "Consenso total" indica cuando todos los modelos coinciden en el diagnóstico, mientras que "Mayoría" y "Sin consenso" señalan desacuerdos que requieren atención clínica.',
  },
  {
    keywords: ['ccd', 'que es ccd', 'modelo ccd'],
    answer:
      'CCD (por sus siglas en inglés) es uno de los modelos que trabaja exclusivamente con la imagen de mamografía. Analiza las características visuales para estimar la probabilidad de que el hallazgo sea benigno o maligno.',
  },
  {
    keywords: ['consenso', 'acuerdo', 'mayoria', 'disagreement'],
    answer:
      '"Consenso total" significa que todos los modelos coinciden en el diagnóstico. "Mayoría" indica que la mayoría coincide pero no todos. "Sin consenso" señala un desacuerdo relevante entre modelos, lo que suele ameritar mayor atención clínica.',
  },
  {
    keywords: ['confianza', 'gauge', 'barra', 'porcentaje', 'probabilidad'],
    answer:
      'La barra de confianza muestra la probabilidad estimada de que el hallazgo sea benigno o maligno. Es un apoyo a la decisión, no un diagnóstico definitivo.',
  },
  {
    keywords: ['historial'],
    answer:
      'En "Historial reciente" ves los últimos diagnósticos procesados en esta sesión del servidor, con archivo, resultado, confianza y fecha. Puedes borrarlo con el botón "Limpiar".',
  },
  {
    keywords: ['idioma', 'bilingue', 'ingles', 'cambiar idioma', 'english', 'language'],
    answer:
      'El sistema tiene modo bilingüe: puedes cambiar el idioma de la interfaz (español/inglés) con el selector de idioma. Los textos, etiquetas de los campos y resultados se adaptan al idioma elegido.',
  },
  {
    keywords: ['diagnostico definitivo', 'reemplaza', 'confiar', 'seguro es'],
    answer:
      'Este sistema es una herramienta de apoyo diagnóstico: no reemplaza el criterio de un profesional médico calificado. La confirmación final siempre corresponde al especialista.',
  },
  {
    keywords: ['porque el ensemble dice nd', 'ensemble no disponible', 'modelo no disponible', 'nd', 'xgboost no disponible'],
    answer:
      'Si ves "N/D" en el modelo Ensemble o XGBoost, significa que no has completado los campos clínicos requeridos (Assessment, Subtlety, Edad y Densidad). Estos modelos necesitan esos datos para funcionar. Una vez que llenes los 4 campos, los modelos se activarán automáticamente y mostrarán su diagnóstico.',
  },
  {
    keywords: ['campos requeridos', 'campos obligatorios', 'campo asterisco', 'que campos son obligatorios'],
    answer:
      'Los campos obligatorios para activar los modelos clínicos son 4: Assessment (BI-RADS 0-6), Subtlety (1-5), Edad de la paciente y Densidad mamaria (1-4). Todos tienen un asterisco (*) y aparecen en la sección "Datos clínicos". Si ves "N/D" en Ensemble o XGBoost, completa estos 4 campos y el análisis se actualizará.',
  },
  {
    keywords: ['como se rellena los campos clinicos', 'donde pongo los datos clinicos', 'donde se ingresan', 'donde relleno'],
    answer:
      'Los datos clínicos se ingresan en el panel lateral, junto al visor de imagen. Primero están los 4 campos requeridos (Assessment, Subtlety, Edad y Densidad). Más abajo tienes la sección "Características Wisconsin" con 30 campos pre-rellenados con los promedios del dataset. Si tienes tus propios valores, puedes ajustarlos. Una vez que completes los campos requeridos, los modelos Ensemble y XGBoost se activarán automáticamente.',
  },
  {
    keywords: ['valores pre-rellenados', 'campos wisconsin automaticos', 'porque ya tienen valores', 'valores por defecto'],
    answer:
      'Los 30 campos Wisconsin aparecen pre-rellenados con los valores promedio del dataset de Wisconsin Breast Cancer. Esto permite que el modelo XGBoost y el Ensemble puedan funcionar incluso si no tienes esos datos. Si tienes mediciones reales de la paciente (ej. radio, textura, perímetro), puedes modificar esos valores para personalizar la predicción.',
  },
  {
    keywords: ['tamaño maximo', 'limite archivo', 'archivo pesado', '5mb', 'peso maximo'],
    answer:
      'El sistema acepta imágenes en formato JPG o PNG de hasta 5 MB. Si tu archivo pesa más, te recomendamos comprimirlo o reducir su resolución antes de subirlo. El sistema procesa automáticamente la imagen al arrastrarla o seleccionarla.',
  },
  {
    keywords: ['diagnostico benigno maligno', 'que significa benigno', 'que significa maligno', 'diferencia benigno maligno'],
    answer:
      'Benigno significa que el hallazgo NO es canceroso: no invade tejidos cercanos y no se propaga a otras partes del cuerpo. Maligno significa que SÍ es canceroso: puede crecer e invadir otros tejidos. El sistema estima la probabilidad de ambas categorías (ej. 78% Benigno - 22% Maligno) para apoyar la decisión clínica. La confirmación final siempre debe ser realizada por un profesional médico.',
  },
  {
    keywords: ['que pasa si no hay consenso', 'modelos contradicen', 'discrepancias entre modelos'],
    answer:
      'Cuando los modelos no coinciden en el diagnóstico, el sistema reporta "Sin consenso" o "Mayoría" (según el grado de acuerdo). En estos casos, el resultado debe interpretarse con mayor cautela y se recomienda consultar a un especialista, ya que la discrepancia entre modelos puede indicar que la imagen o los datos clínicos no son suficientemente claros.',
  },
  {
    keywords: ['fallo en el analisis', 'error al procesar', 'no se pudo analizar', 'no disponible', 'offline', 'falla', 'fallo', 'error'],
    answer:
      'Si ves "No disponible" en uno de los modelos, puede deberse a varias razones: el archivo no se subió correctamente, el formato no es compatible (solo JPG/PNG), los datos clínicos requeridos no se completaron para los modelos híbridos, o temporalmente el servicio no está respondiendo. Espera unos segundos y prueba a subir la imagen nuevamente. También puedes usar el botón "Reintentar" en el panel de resultado.',
  },
  {
    keywords: ['falsos positivos', 'falsos negativos', 'precision del modelo', 'exactitud'],
    answer:
      'El modelo fue entrenado con el dataset CBIS-DDSM para imágenes y Wisconsin Breast Cancer Dataset para datos clínicos. Tiene una alta precisión, pero ningún modelo es infalible: pueden ocurrir falsos positivos (diagnosticar maligno cuando es benigno) o falsos negativos (diagnosticar benigno cuando es maligno). Por eso siempre enfatizamos que es una herramienta de APOYO y la confirmación debe ser clínica.',
  },
  {
    keywords: ['para que sirve', 'proposito', 'finalidad', 'que es este sistema', 'que hace este sistema', 'objetivo'],
    answer:
      'Este sistema es una herramienta de apoyo diagnóstico para la clasificación de mamografías. Sube una imagen y, opcionalmente, datos clínicos, y el sistema combina 6 modelos de Deep Learning y Machine Learning para estimar la probabilidad de que el hallazgo sea benigno o maligno, junto con el nivel de confianza y el consenso entre modelos. Su objetivo es apoyar el criterio del especialista, no reemplazarlo: la confirmación final siempre corresponde a un profesional médico calificado.',
  },
  {
    keywords: ['funciones', 'opciones tiene', 'que ofrece'],
    answer:
      'En el sistema puedes: (1) subir una mamografía en JPG o PNG y obtener su análisis; (2) completar datos clínicos (Assessment, Subtlety, Edad, Densidad) y opcionalmente los 30 campos Wisconsin para mejorar la predicción; (3) ver el resultado con el diagnóstico, el consenso entre los 6 modelos y la barra de confianza; (4) revisar el historial reciente de diagnósticos; (5) alternar entre modo claro y oscuro con el ícono de sol/luna; (6) cambiar el idioma de la interfaz entre español e inglés (modo bilingüe); y (7) hacerme preguntas por texto o por voz, como estás haciendo ahora.',
  },
]

const DEFAULT_ANSWER =
  'No tengo una respuesta exacta para eso todavía. Puedo ayudarte con: cómo subir una imagen, los campos clínicos (Assessment, Subtlety, Edad, Densidad), los 30 campos Wisconsin, los 6 modelos que usa el sistema, cómo leer el consenso y la confianza, el historial, el modo claro/oscuro o el cambio de idioma. ¿Sobre cuál te gustaría saber más?'

const GREETING =
  'Hola, soy el asistente del sistema. Puedo explicarte cómo subir una mamografía, qué significan los campos clínicos, cómo interpretar el resultado, o resolver dudas sobre el historial, el idioma o el modo claro/oscuro. ¿En qué te ayudo?'

function normalize(text) {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

function findAnswer(question) {
  const q = normalize(question)
  let best = null
  let bestScore = 0
  for (const entry of FAQ) {
    let score = 0
    for (const kw of entry.keywords) {
      if (q.includes(normalize(kw))) score += 1
    }
    if (score > bestScore) {
      bestScore = score
      best = entry
    }
  }
  return best ? best.answer : DEFAULT_ANSWER
}

function ChatIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" aria-hidden="true">
      <path
        d="M4 5.5h16a1 1 0 0 1 1 1V15a1 1 0 0 1-1 1H9l-4.2 3.5a.5.5 0 0 1-.8-.4V16H4a1 1 0 0 1-1-1V6.5a1 1 0 0 1 1-1Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" aria-hidden="true">
      <path d="M6 6l12 12M18 6 6 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}

function MicIcon({ active }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" aria-hidden="true">
      <rect x="9" y="3" width="6" height="11" rx="3" stroke="currentColor" strokeWidth="1.6" />
      <path
        d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      {active && <circle cx="19" cy="6" r="2.5" className="fill-malignant" />}
    </svg>
  )
}

function SpeakerIcon({ muted }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" aria-hidden="true">
      <path d="M4 9.5h3l4.5-3.8v12.6L7 14.5H4v-5Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      {!muted && (
        <path d="M16.5 8.5a5 5 0 0 1 0 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      )}
      {muted && <path d="M17 9l4 6M21 9l-4 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />}
    </svg>
  )
}

function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" aria-hidden="true">
      <path d="M4 12 20 4l-6.5 16-2.5-7L4 12Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    </svg>
  )
}

export default function HelpChatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([{ role: 'bot', text: GREETING }])
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [ttsEnabled, setTtsEnabled] = useState(true)

  const recognitionRef = useRef(null)
  const listRef = useRef(null)

  const speechRecognitionSupported = useMemo(
    () => typeof window !== 'undefined' && (window.SpeechRecognition || window.webkitSpeechRecognition),
    []
  )
  const speechSynthesisSupported = useMemo(
    () => typeof window !== 'undefined' && 'speechSynthesis' in window,
    []
  )

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [messages, isOpen])

  const speak = useCallback(
    (text) => {
      if (!ttsEnabled || !speechSynthesisSupported) return
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'es-ES'
      utterance.rate = 1
      window.speechSynthesis.speak(utterance)
    },
    [ttsEnabled, speechSynthesisSupported]
  )

  const sendMessage = useCallback(
    (text) => {
      const trimmed = text.trim()
      if (!trimmed) return
      const answer = findAnswer(trimmed)
      setMessages((prev) => [...prev, { role: 'user', text: trimmed }, { role: 'bot', text: answer }])
      setInput('')
      speak(answer)
    },
    [speak]
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  const toggleListening = useCallback(() => {
    if (!speechRecognitionSupported) return

    if (isListening) {
      recognitionRef.current?.stop()
      return
    }

    const SpeechRecognitionImpl = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognitionImpl()
    recognition.lang = 'es-ES'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onstart = () => setIsListening(true)
    recognition.onerror = () => setIsListening(false)
    recognition.onend = () => setIsListening(false)
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript
      if (transcript) sendMessage(transcript)
    }

    recognitionRef.current = recognition
    recognition.start()
  }, [isListening, speechRecognitionSupported, sendMessage])

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop()
      if (speechSynthesisSupported) window.speechSynthesis.cancel()
    }
  }, [speechSynthesisSupported])

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen((v) => !v)}
        aria-label={isOpen ? 'Cerrar asistente' : 'Abrir asistente de ayuda'}
        aria-expanded={isOpen}
        className="fixed bottom-6 right-6 z-50 flex h-13 w-13 items-center justify-center rounded-full border border-accent/40 bg-accent text-white shadow-lightbox transition-transform hover:scale-105 active:scale-95"
        style={{ height: '52px', width: '52px' }}
      >
        {isOpen ? <CloseIcon /> : <ChatIcon />}
      </button>

      {isOpen && (
        <div
          role="dialog"
          aria-label="Asistente de ayuda"
          className="fixed bottom-24 right-6 z-50 flex h-[min(560px,70vh)] w-[min(360px,92vw)] flex-col overflow-hidden rounded-xl border border-line bg-surface shadow-lightbox"
        >
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <div className="leading-tight">
              <p className="font-display text-[13px] font-semibold text-ink">Asistente</p>
              <p className="font-mono text-[10px] uppercase tracking-wider text-muted">Ayuda del sistema</p>
            </div>
            {speechSynthesisSupported && (
              <button
                type="button"
                onClick={() => setTtsEnabled((v) => !v)}
                aria-pressed={ttsEnabled}
                aria-label={ttsEnabled ? 'Desactivar voz de respuestas' : 'Activar voz de respuestas'}
                className="flex h-8 w-8 items-center justify-center rounded-full border border-line text-ink transition-colors hover:border-accent/50 hover:text-accent"
              >
                <SpeakerIcon muted={!ttsEnabled} />
              </button>
            )}
          </div>

          <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <p
                  className={`max-w-[85%] rounded-lg px-3 py-2 text-[13px] leading-relaxed ${
                    m.role === 'user'
                      ? 'bg-accent text-white'
                      : 'border border-line bg-bg text-ink'
                  }`}
                >
                  {m.text}
                </p>
              </div>
            ))}
            {isListening && (
              <div className="flex justify-end">
                <p className="rounded-lg bg-accent/10 px-3 py-2 font-mono text-[11px] text-accent">
                  Escuchando…
                </p>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-line px-3 py-3">
            {speechRecognitionSupported && (
              <button
                type="button"
                onClick={toggleListening}
                aria-pressed={isListening}
                aria-label={isListening ? 'Detener dictado por voz' : 'Preguntar por voz'}
                className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full border transition-colors ${
                  isListening
                    ? 'border-malignant/50 bg-malignant/10 text-malignant'
                    : 'border-line text-ink hover:border-accent/50 hover:text-accent'
                }`}
              >
                <MicIcon active={isListening} />
              </button>
            )}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu pregunta…"
              className="min-w-0 flex-1 rounded-lg border border-line bg-bg px-3 py-2 font-body text-[13px] text-ink outline-none focus:border-accent"
            />
            <button
              type="submit"
              aria-label="Enviar pregunta"
              disabled={!input.trim()}
              className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-accent text-white transition-opacity hover:opacity-90 disabled:opacity-40"
            >
              <SendIcon />
            </button>
          </form>
        </div>
      )}
    </>
  )
}