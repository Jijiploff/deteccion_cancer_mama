const WISCONSIN_DEFAULTS = {
  radius_mean: 14.127, texture_mean: 19.290, perimeter_mean: 91.969, area_mean: 654.889,
  smoothness_mean: 0.096, compactness_mean: 0.104, concavity_mean: 0.089, concave_points_mean: 0.049,
  symmetry_mean: 0.181, fractal_dimension_mean: 0.063,
  radius_se: 0.405, texture_se: 1.217, perimeter_se: 2.866, area_se: 40.337,
  smoothness_se: 0.007, compactness_se: 0.025, concavity_se: 0.032, concave_points_se: 0.012,
  symmetry_se: 0.021, fractal_dimension_se: 0.004,
  radius_worst: 16.269, texture_worst: 25.677, perimeter_worst: 107.261, area_worst: 880.583,
  smoothness_worst: 0.132, compactness_worst: 0.254, concavity_worst: 0.272, concave_points_worst: 0.115,
  symmetry_worst: 0.290, fractal_dimension_worst: 0.084,
}

import { useLanguage } from '../context/LanguageContext'

const WISCONSIN_FIELDS = [
  { key: 'radius_mean', step: 0.01 },
  { key: 'texture_mean', step: 0.01 },
  { key: 'perimeter_mean', step: 0.01 },
  { key: 'area_mean', step: 0.01 },
  { key: 'smoothness_mean', step: 0.001 },
  { key: 'compactness_mean', step: 0.001 },
  { key: 'concavity_mean', step: 0.001 },
  { key: 'concave_points_mean', step: 0.001 },
  { key: 'symmetry_mean', step: 0.001 },
  { key: 'fractal_dimension_mean', step: 0.001 },
  { key: 'radius_se', step: 0.001 },
  { key: 'texture_se', step: 0.001 },
  { key: 'perimeter_se', step: 0.001 },
  { key: 'area_se', step: 0.01 },
  { key: 'smoothness_se', step: 0.0001 },
  { key: 'compactness_se', step: 0.0001 },
  { key: 'concavity_se', step: 0.0001 },
  { key: 'concave_points_se', step: 0.0001 },
  { key: 'symmetry_se', step: 0.0001 },
  { key: 'fractal_dimension_se', step: 0.0001 },
  { key: 'radius_worst', step: 0.01 },
  { key: 'texture_worst', step: 0.01 },
  { key: 'perimeter_worst', step: 0.01 },
  { key: 'area_worst', step: 0.01 },
  { key: 'smoothness_worst', step: 0.001 },
  { key: 'compactness_worst', step: 0.001 },
  { key: 'concavity_worst', step: 0.001 },
  { key: 'concave_points_worst', step: 0.001 },
  { key: 'symmetry_worst', step: 0.001 },
  { key: 'fractal_dimension_worst', step: 0.001 },
]

export default function ClinicalForm({ show, formData, onChange }) {
  const { t } = useLanguage()

  if (!show) return null

  const handleChange = (key) => (e) => {
    onChange(key, e.target.value)
  }

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-line bg-surface p-5">
      <h2 className="font-display text-sm font-semibold tracking-tight">
        {t('clinical_form.title')}
      </h2>
      <p className="font-mono text-[11px] text-muted">
        {t('clinical_form.description')}
      </p>

      <div className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
        {WISCONSIN_FIELDS.map(({ key, step }) => (
          <div key={key}>
            <label className="font-mono text-[10px] text-muted">{t(`clinical_form.fields.${key}`)}</label>
            <input
              type="number" step={step}
              value={formData[key]}
              onChange={handleChange(key)}
              className="mt-0.5 w-full rounded-lg border border-line bg-bg px-2 py-1.5 font-mono text-[11px] text-ink outline-none focus:border-accent"
            />
          </div>
        ))}
      </div>
    </div>
  )
}

export { WISCONSIN_DEFAULTS, WISCONSIN_FIELDS }
