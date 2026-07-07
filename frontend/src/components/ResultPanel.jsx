import { useCallback, useRef, useState } from 'react'

const ACCEPTED_TYPES = ['image/jpeg', 'image/jpg', 'image/png']
const MAX_SIZE_MB = 5

export default function UploadPanel({ onFileSelected, previewUrl, isLoading, filename }) {
  const [isDragging, setIsDragging] = useState(false)
  const [localError, setLocalError] = useState(null)
  const inputRef = useRef(null)

  const validateAndSelect = useCallback(
    (file) => {
      if (!file) return
      if (!ACCEPTED_TYPES.includes(file.type)) {
        setLocalError('Formato no soportado. Usa JPG o PNG.')
        return
      }
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        setLocalError(`El archivo supera el límite de ${MAX_SIZE_MB}MB.`)
        return
      }
      setLocalError(null)
      onFileSelected(file)
    },
    [onFileSelected]
  )

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    const file = event.dataTransfer.files?.[0]
    validateAndSelect(file)
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-sm font-semibold tracking-tight">
          Visor de imagen
        </h2>
        {filename && (
          <span className="truncate font-mono text-[11px] text-muted">{filename}</span>
        )}
      </div>

      <label
        htmlFor="mammography-upload"
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`film-grain relative flex aspect-square w-full cursor-pointer flex-col items-center justify-center overflow-hidden rounded-xl border bg-[#0c1114] transition-shadow duration-200 ${
          isDragging ? 'border-accent shadow-lightbox' : 'border-line'
        }`}
      >
        {previewUrl ? (
          <>
            <img
              src={previewUrl}
              alt="Vista previa de la mamografía cargada"
              className="h-full w-full object-contain"
            />
            {isLoading && (
              <div
                aria-hidden="true"
                className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-accent/25 to-transparent animate-scan"
              />
            )}
          </>
        ) : (
          <div className="flex flex-col items-center gap-3 px-6 text-center">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-8 w-8 text-accent/70"
              aria-hidden="true"
            >
              <path
                d="M12 16V4M12 4 7.5 8.5M12 4l4.5 4.5"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M4 16v2.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V16"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
              />
            </svg>
            <p className="font-body text-sm text-neutral-300">
              Arrastra la imagen aquí o
              <span className="text-accent"> haz clic para seleccionarla</span>
            </p>
            <p className="font-mono text-[11px] text-neutral-500">
              JPG o PNG · máx. {MAX_SIZE_MB}MB
            </p>
          </div>
        )}
        <input
          ref={inputRef}
          id="mammography-upload"
          type="file"
          accept="image/jpeg,image/png"
          className="sr-only"
          onChange={(e) => validateAndSelect(e.target.files?.[0])}
        />
      </label>

      {localError && (
        <p role="alert" className="font-mono text-[12px] text-malignant">
          {localError}
        </p>
      )}
    </div>
  )
}