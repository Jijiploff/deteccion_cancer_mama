export default function ConfidenceGauge({ benign, malignant }) {
  const benignPct = Math.round(benign * 100)
  const malignantPct = Math.round(malignant * 100)

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between font-mono text-[11px] text-muted">
        <span>BENIGNO</span>
        <span>MALIGNO</span>
      </div>
      <div
        role="img"
        aria-label={`Probabilidad benigno ${benignPct}%, probabilidad maligno ${malignantPct}%`}
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