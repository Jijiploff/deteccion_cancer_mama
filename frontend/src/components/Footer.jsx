export default function Footer() {
  return (
    <footer className="border-t border-line px-5 py-8 sm:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-1 font-mono text-[11px] text-muted">
        <p>Sistema de apoyo diagnóstico · No sustituye el criterio médico profesional.</p>
        <p>Modelo entrenado con CBIS-DDSM y Wisconsin Breast Cancer Dataset.</p>
      </div>
    </footer>
  )
}