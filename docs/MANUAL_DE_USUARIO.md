# Manual de Usuario

Sistema de Diagnóstico Automatizado de Cáncer de Mama mediante Aprendizaje Automático.

## 1. Introducción

Este manual describe el uso del sistema de apoyo diagnóstico para clasificación de mamografías. El sistema utiliza un modelo de deep learning (EfficientNet) entrenado con los datasets CBIS-DDSM y Wisconsin Breast Cancer Database para estimar la probabilidad de que un hallazgo sea benigno o maligno.

**Importante**: Esta herramienta es de **apoyo diagnóstico**. No reemplaza el criterio de un profesional médico calificado.

## 2. Acceso al Sistema

### 2.1 Local (Desarrollo)
- **Frontend**: http://localhost:3000 (Docker) o http://localhost:5173 (Vite)
- **Backend**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs

### 2.2 Producción
- **Frontend**: https://[tu-dominio].vercel.app
- **Backend**: https://[tu-dominio].onrender.com

## 3. Interfaz de Usuario

La aplicación consta de las siguientes secciones:

### 3.1 Encabezado (Header)
- Logo "BC" (Breast Cancer)
- Título "Apoyo Diagnóstico - Clasificación de mamografías"
- Botón de cambio de modo (claro/oscuro)

### 3.2 Sección Hero
- Descripción del sistema
- Aviso: herramienta de apoyo, no reemplaza al especialista

### 3.3 Panel de Carga (UploadPanel)
- Área de arrastrar y soltar (drag & drop)
- Soporta formatos: JPG y PNG
- Tamaño máximo: 5MB
- Vista previa de la imagen seleccionada

### 3.4 Panel de Resultados (ResultPanel)
- **label**: BENIGN (benigno) o MALIGNANT (maligno)
- **Confianza**: porcentaje de confianza en la predicción
- **Probabilidades**: barra comparativa benigno vs maligno
- **Advertencia**: si la confianza es baja (<65%)

### 3.5 Historial (HistoryList)
- Lista de diagnósticos recientes
- Muestra: nombre de archivo, resultado y fecha/hora
- Botón para limpiar el historial

### 3.6 Pie de Página (Footer)
- Aviso legal
- Créditos de los datasets utilizados

## 4. Flujo de Uso

### 4.1 Realizar un Diagnóstico

1. Abre la aplicación en el navegador
2. Arrastra una mamografía en formato JPG o PNG al panel de carga, o haz clic para seleccionar un archivo
3. El sistema mostrará una vista previa de la imagen y comenzará el análisis automáticamente
4. En segundos se mostrará el resultado:
   - **BENIGN** (color verde): alta probabilidad de hallazgo benigno
   - **MALIGNANT** (color rojo/terracota): alta probabilidad de hallazgo maligno
5. Revisa la barra de confianza para ver las probabilidades detalladas
6. El resultado se agregará automáticamente al historial

### 4.2 Interpretar Resultados

| Campo | Descripción |
|-------|-------------|
| **label** | Clasificación: BENIGN o MALIGNANT |
| **confidence** | Nivel de confianza (0-100%) |
| **benign_prob** | Probabilidad de benignidad (0-100%) |
| **malignant_prob** | Probabilidad de malignidad (0-100%) |
| **warning** | Aparece si la confianza es <65% |

### 4.3 Gestionar Historial

- El historial muestra los últimos 50 diagnósticos
- Cada entrada incluye: nombre de archivo, resultado (Benigno/Maligno), confianza y fecha
- Usa el botón **"Limpiar"** para borrar el historial

## 5. Entrenamiento de Modelos en Google Colab

### 5.1 Acceso al Notebook
1. Ve a https://colab.research.google.com/
2. Abre el notebook del proyecto o crea uno nuevo y pega el código de entrenamiento
3. Conecta Google Drive cuando se solicite

### 5.2 Ejecución del Análisis Exploratorio (EDA)
Ejecuta la clase \BreastCancerEDA\:
- Verifica la estructura de archivos en Drive
- Carga y analiza los datasets
- Genera gráficos de distribución de patologías
- Analiza BI-RADS, subtlety y métricas
- Guarda reporte en: \Resultados/exploratory_report.txt\

### 5.3 Entrenamiento de Modelos

El sistema entrena 5 modelos:

| Modelo | Tipo | Descripción |
|--------|------|-------------|
| CNN Transfer Learning | Clásico | EfficientNetB4/ResNet50/DenseNet121 fine-tuning |
| XGBoost Tabular | Clásico | Clasificador sobre datos de Wisconsin |
| Ensemble Híbrido | Híbrido | Fusión de CNN (imagen) + red fully connected (tabulares) |
| Hybrid VGG16+CLAHE | Híbrido | VGG16 con preprocesamiento CLAHE |
| Hybrid Custom CNN+Canny | Híbrido | CNN personalizada con detección de bordes Canny + CLAHE |

### 5.4 Generación de Reportes

Al finalizar el entrenamiento, el sistema genera:
- **PDF**: Reporte completo con portada, tablas, gráficos y conclusiones
- **Word**: Reporte en formato editable
- **Excel**: Tablas comparativas de métricas
- **Gráficos**: Matrices de confusión, curvas ROC, mapas de calor

Los reportes se guardan en: \Resultados/reportes/\

### 5.5 Guardar el Mejor Modelo
El mejor modelo se guarda automáticamente como:
`
Resultados/modelo_cancer_mama.keras
`
Descarga este archivo para usarlo en la API.

## 6. API REST

### 6.1 Health Check
`
GET /health
`
Verifica el estado del servicio y si el modelo está cargado.

### 6.2 Predicción
`
POST /predict
Content-Type: multipart/form-data
Body: file (imagen JPG/PNG)
`
Devuelve la clasificación de la mamografía.

### 6.3 Historial
`
GET /history   -> Obtener historial
DELETE /history -> Limpiar historial
`

## 7. Métricas y Evaluación

| Métrica | Descripción |
|---------|-------------|
| Precisión (Accuracy) | Proporción de predicciones correctas |
| Matriz de Confusión | VP, VN, FP, FN |
| AUC-ROC | Área bajo la curva ROC |
| Coeficiente de Matthews | Medida robusta para clases desbalanceadas |
| Prueba de McNemar | Comparación estadística entre pares de modelos |

## 8. Solución de Problemas

| Problema | Solución |
|----------|----------|
| "El servicio no está disponible" | Espera unos segundos y recarga la página |
| "Archivo no soportado" | Convierte la imagen a JPG o PNG |
| "Archivo excede el límite" | Reduce el tamaño de la imagen a menos de 5MB |
| El modelo no se carga | Verifica que \modelo_cancer_mama.keras\ esté en \ackend/models/\ |
| Resultados inconsistentes | Confianza baja (<65%): el modelo no está seguro; consulta a un especialista |
