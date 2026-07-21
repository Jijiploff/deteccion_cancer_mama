const translations = {
  site: {
    title: { es: 'Detección de Cáncer de Mama', en: 'Breast Cancer Detection' },
    lang: { es: 'es', en: 'en' },
  },
  header: {
    title: { es: 'Apoyo Diagnóstico', en: 'Diagnostic Support' },
    subtitle: { es: 'Clasificación de mamografías', en: 'Mammography Classification' },
    dashboard: { es: 'Dashboard', en: 'Dashboard' },
    logout: { es: 'Salir', en: 'Log out' },
    theme_light: { es: 'Cambiar a modo claro', en: 'Switch to light mode' },
    theme_dark: { es: 'Cambiar a modo oscuro', en: 'Switch to dark mode' },
    language: { es: 'Cambiar idioma a inglés', en: 'Switch language to Spanish' },
  },
  hero: {
    badge: { es: 'Sistema de apoyo diagnóstico · Deep Learning', en: 'Diagnostic support system · Deep Learning' },
    heading1: { es: 'Lee la mamografía con detalle.', en: 'Read the mammogram in detail.' },
    heading2: { es: 'Decide con criterio clínico.', en: 'Decide with clinical judgment.' },
    description: {
      es: 'Sube una imagen de mamografía y el modelo entrenado con CBIS-DDSM estima la probabilidad de hallazgos benignos o malignos en segundos. Cada resultado incluye su nivel de confianza para apoyar, no reemplazar, el criterio del especialista.',
      en: 'Upload a mammogram image and the model trained on CBIS-DDSM estimates the probability of benign or malignant findings in seconds. Each result includes its confidence level to support, not replace, the specialist\'s judgment.',
    },
    note: {
      es: 'Herramienta de apoyo, no un diagnóstico definitivo. La confirmación siempre corresponde a un profesional médico calificado.',
      en: 'Support tool, not a definitive diagnosis. Confirmation always rests with a qualified medical professional.',
    },
  },
  footer: {
    line1: { es: 'Sistema de apoyo diagnóstico · No sustituye el criterio médico profesional.', en: 'Diagnostic support system · Does not replace professional medical judgment.' },
    line2: { es: 'Modelo entrenado con CBIS-DDSM y Wisconsin Breast Cancer Dataset.', en: 'Model trained on CBIS-DDSM and Wisconsin Breast Cancer Dataset.' },
  },
  login: {
    title: { es: 'Apoyo Diagnóstico', en: 'Diagnostic Support' },
    subtitle: { es: 'Inicio de Sesión', en: 'Sign In' },
    username_label: { es: 'Usuario', en: 'Username' },
    password_label: { es: 'Contraseña', en: 'Password' },
    username_placeholder: { es: 'admin', en: 'admin' },
    password_placeholder: { es: '••••••••', en: '••••••••' },
    logging_in: { es: 'Ingresando...', en: 'Signing in...' },
    login_button: { es: 'Ingresar', en: 'Sign In' },
    invalid_credentials: { es: 'Credenciales inválidas', en: 'Invalid credentials' },
  },
  upload: {
    title: { es: 'Visor de imagen', en: 'Image Viewer' },
    drop_hint: { es: 'Arrastra la imagen aquí o', en: 'Drag image here or' },
    drop_link: { es: 'haz clic para seleccionarla', en: 'click to select' },
    format_hint: { es: 'JPG o PNG · máx. {max}MB', en: 'JPG or PNG · max {max}MB' },
    format_error: { es: 'Formato no soportado. Usa JPG o PNG.', en: 'Unsupported format. Use JPG or PNG.' },
    size_error: { es: 'El archivo supera el límite de {max}MB.', en: 'File exceeds the {max}MB limit.' },
    alt_preview: { es: 'Vista previa de la mamografía cargada', en: 'Preview of the loaded mammogram' },
  },
  clinical_form: {
    title: { es: 'Características Wisconsin', en: 'Wisconsin Features' },
    description: {
      es: 'Llena los campos disponibles para activar el modelo Tabular RF. Los valores se pre-rellenan con las medias del dataset.',
      en: 'Fill in the available fields to activate the Tabular RF model. Values are pre-filled with dataset means.',
    },
    fields: {
      radius_mean: { es: 'Radio medio', en: 'Mean Radius' },
      texture_mean: { es: 'Textura media', en: 'Mean Texture' },
      perimeter_mean: { es: 'Perímetro medio', en: 'Mean Perimeter' },
      area_mean: { es: 'Área media', en: 'Mean Area' },
      smoothness_mean: { es: 'Suavidad media', en: 'Mean Smoothness' },
      compactness_mean: { es: 'Compacidad media', en: 'Mean Compactness' },
      concavity_mean: { es: 'Concavidad media', en: 'Mean Concavity' },
      concave_points_mean: { es: 'Pts. cóncavos medios', en: 'Mean Concave Points' },
      symmetry_mean: { es: 'Simetría media', en: 'Mean Symmetry' },
      fractal_dimension_mean: { es: 'Dimensión fractal media', en: 'Mean Fractal Dimension' },
      radius_se: { es: 'Error estándar radio', en: 'Radius SE' },
      texture_se: { es: 'Error estándar textura', en: 'Texture SE' },
      perimeter_se: { es: 'Error estándar perímetro', en: 'Perimeter SE' },
      area_se: { es: 'Error estándar área', en: 'Area SE' },
      smoothness_se: { es: 'Error estándar suavidad', en: 'Smoothness SE' },
      compactness_se: { es: 'Error estándar compacidad', en: 'Compactness SE' },
      concavity_se: { es: 'Error estándar concavidad', en: 'Concavity SE' },
      concave_points_se: { es: 'Error estándar pts. cóncavos', en: 'Concave Points SE' },
      symmetry_se: { es: 'Error estándar simetría', en: 'Symmetry SE' },
      fractal_dimension_se: { es: 'Error estándar dim. fractal', en: 'Fractal Dimension SE' },
      radius_worst: { es: 'Radio peor', en: 'Worst Radius' },
      texture_worst: { es: 'Textura peor', en: 'Worst Texture' },
      perimeter_worst: { es: 'Perímetro peor', en: 'Worst Perimeter' },
      area_worst: { es: 'Área peor', en: 'Worst Area' },
      smoothness_worst: { es: 'Suavidad peor', en: 'Worst Smoothness' },
      compactness_worst: { es: 'Compacidad peor', en: 'Worst Compactness' },
      concavity_worst: { es: 'Concavidad peor', en: 'Worst Concavity' },
      concave_points_worst: { es: 'Pts. cóncavos peor', en: 'Worst Concave Points' },
      symmetry_worst: { es: 'Simetría peor', en: 'Worst Symmetry' },
      fractal_dimension_worst: { es: 'Dim. fractal peor', en: 'Worst Fractal Dimension' },
    },
  },
  result: {
    title: { es: 'Resultado', en: 'Result' },
    idle_message: { es: 'Sube una mamografía para obtener el análisis.', en: 'Upload a mammogram to get the analysis.' },
    loading: { es: 'Analizando imagen…', en: 'Analyzing image…' },
    benign_badge: { es: 'BENIGNO', en: 'BENIGN' },
    malignant_badge: { es: 'MALIGNO', en: 'MALIGNANT' },
    consensus: {
      full_agreement: { es: 'Consenso total', en: 'Full agreement' },
      majority: { es: 'Mayoría', en: 'Majority' },
      disagreement: { es: 'Sin consenso', en: 'Disagreement' },
    },
    table: {
      model: { es: 'Modelo', en: 'Model' },
      diagnosis: { es: 'Diagnóstico', en: 'Diagnosis' },
      prob_benign: { es: 'Prob. Benigna', en: 'Prob. Benign' },
      prob_malignant: { es: 'Prob. Maligna', en: 'Prob. Malignant' },
      confidence: { es: 'Confianza', en: 'Confidence' },
      time: { es: 'Tiempo', en: 'Time' },
      status: { es: 'Estado', en: 'Status' },
    },
    model_benign: { es: 'Benigno', en: 'Benign' },
    model_malignant: { es: 'Maligno', en: 'Malignant' },
    na: { es: 'N/D', en: 'N/A' },
    processed: { es: 'Procesado en {time} ms', en: 'Processed in {time} ms' },
    status_executed: { es: 'Ejecutado', en: 'Executed' },
    status_error: { es: 'Error', en: 'Error' },
    status_unavailable: { es: 'No disponible', en: 'Unavailable' },
    error_message: { es: 'Error al procesar la imagen.', en: 'Error processing the image.' },
    retry_button: { es: 'Reintentar', en: 'Retry' },
  },
  gauge: {
    benign: { es: 'BENIGNO', en: 'BENIGN' },
    malignant: { es: 'MALIGNO', en: 'MALIGNANT' },
    aria_label: { es: 'Probabilidad benigno {benign}%, probabilidad maligno {malignant}%', en: 'Probability benign {benign}%, probability malignant {malignant}%' },
  },
  dashboard: {
    title: { es: 'Dashboard', en: 'Dashboard' },
    welcome: { es: 'Bienvenido, {username}', en: 'Welcome, {username}' },
    logout: { es: 'Cerrar Sesión', en: 'Log Out' },
    total_diagnoses: { es: 'Total Diagnósticos', en: 'Total Diagnoses' },
    malignant: { es: 'Malignos', en: 'Malignant' },
    benign: { es: 'Benignos', en: 'Benign' },
    api_status: { es: 'API Status', en: 'API Status' },
    online: { es: 'Online', en: 'Online' },
    offline: { es: 'Offline', en: 'Offline' },
    history_title: { es: 'Historial de Diagnósticos', en: 'Diagnosis History' },
    loading: { es: 'Cargando...', en: 'Loading...' },
    no_history: { es: 'No hay diagnósticos aún. Sube una imagen para comenzar.', en: 'No diagnoses yet. Upload an image to start.' },
    table: {
      file: { es: 'Archivo', en: 'File' },
      result: { es: 'Resultado', en: 'Result' },
      confidence: { es: 'Confianza', en: 'Confidence' },
      date: { es: 'Fecha', en: 'Date' },
    },
  },
  history: {
    title: { es: 'Historial reciente', en: 'Recent history' },
    clear: { es: 'Limpiar', en: 'Clear' },
    loading: { es: 'Cargando historial…', en: 'Loading history…' },
    empty: { es: 'Aún no hay diagnósticos registrados en esta sesión del servidor.', en: 'No diagnoses registered in this server session yet.' },
    malignant: { es: 'Maligno', en: 'Malignant' },
    benign: { es: 'Benigno', en: 'Benign' },
  },
  app: {
    service_unavailable: {
      es: 'El servicio de diagnóstico no está disponible en este momento. Intenta más tarde.',
      en: 'The diagnostic service is not available at this time. Try again later.',
    },
    unexpected_error: { es: 'Ocurrió un error inesperado.', en: 'An unexpected error occurred.' },
  },
  spinner: {
    processing: { es: 'Procesando', en: 'Processing' },
    loading: { es: 'Cargando', en: 'Loading' },
  },
}

function deepGet(obj, path) {
  return path.split('.').reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : undefined), obj)
}

export function t(language, key, params = {}) {
  const value = deepGet(translations, key)
  if (!value) return key
  const text = value[language]
  if (!text) return key
  return text.replace(/\{(\w+)\}/g, (_, p) => params[p] !== undefined ? params[p] : `{${p}}`)
}

export default translations
