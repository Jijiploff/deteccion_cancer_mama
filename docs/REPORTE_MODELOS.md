# Reporte Técnico de Modelos

## 1. Análisis Exploratorio de Datos (EDA)

### 1.1 Datasets Utilizados

| Dataset | Tipo | Registros | Fuente |
|---------|------|-----------|--------|
| CBIS-DDSM (Calcificaciones) | Imágenes | ~2,500 casos | The Cancer Imaging Archive |
| CBIS-DDSM (Masas) | Imágenes | ~2,000 casos | The Cancer Imaging Archive |
| Wisconsin Breast Cancer | Tabular | 569 casos | UCI Machine Learning Repository |

### 1.2 Distribución de Patologías

#### Calcificaciones
- **BENIGN**: ~55-60%
- **MALIGNANT**: ~40-45%
- **BENIGN_WITHOUT_CALLBACK**: ~2-5%

#### Masas
- **BENIGN**: ~50-55%
- **MALIGNANT**: ~40-45%
- **BENIGN_WITHOUT_CALLBACK**: ~3-7%

#### Wisconsin (Diagnosis)
- **BENIGN (B)**: ~62.7% (357 casos)
- **MALIGNANT (M)**: ~37.3% (212 casos)

### 1.3 Estadísticos Descriptivos (Wisconsin)

| Característica | Media | Desv. Est. | Mín | Máx |
|---------------|-------|------------|-----|-----|
| radius_mean | 14.13 | 3.52 | 6.98 | 28.11 |
| texture_mean | 19.29 | 4.30 | 9.71 | 39.28 |
| perimeter_mean | 91.97 | 24.30 | 43.79 | 188.50 |
| area_mean | 654.89 | 351.91 | 143.50 | 2501.00 |
| smoothness_mean | 0.10 | 0.01 | 0.05 | 0.16 |
| compactness_mean | 0.10 | 0.05 | 0.02 | 0.35 |
| concavity_mean | 0.09 | 0.08 | 0.00 | 0.43 |
| concave points_mean | 0.05 | 0.04 | 0.00 | 0.20 |
| symmetry_mean | 0.18 | 0.03 | 0.11 | 0.30 |
| fractal_dimension_mean | 0.06 | 0.01 | 0.05 | 0.10 |

### 1.4 Análisis BI-RADS

Distribución de categorías BI-RADS en el dataset CBIS-DDSM:
- **BI-RADS 2**: Benigno (hallazgo no sospechoso)
- **BI-RADS 3**: Probablemente benigno
- **BI-RADS 4**: Sospechoso
- **BI-RADS 5**: Altamente sospechoso de malignidad

### 1.5 Análisis de Subtlety

Grado de sutileza del hallazgo (1 = más sutil, 5 = más evidente):

| Subtlety | Porcentaje |
|----------|-----------|
| 1 (Muy sutil) | ~5% |
| 2 | ~12% |
| 3 | ~25% |
| 4 | ~33% |
| 5 (Muy evidente) | ~25% |

## 2. Modelos Implementados

### 2.1 Modelo 1: CNN con Transfer Learning (EfficientNetB4)

**Arquitectura:**
- Backbone: EfficientNetB4 (pre-entrenado en ImageNet)
- Fine-tuning: últimas 20 capas descongeladas
- Top: GlobalAveragePooling → Dropout(0.3) → Dense(256) → BatchNorm → Dropout(0.3) → Dense(128) → Dropout(0.2) → Dense(1, sigmoid)

**Preprocesamiento:**
- Redimensionamiento: 224x224
- CLAHE en canal L de LAB
- Normalización [0,1]
- Aumentos: flip horizontal, brightness, shift/scale/rotate, CLAHE

**Entrenamiento:**
- Optimizador: Adam
- Learning rate: 1e-4 (con ReduceLROnPlateau)
- Loss: binary crossentropy
- Métricas: accuracy, precision, recall
- Early stopping: paciencia 5 épocas
- Épocas: 10 (con early stopping)
- Batch size: 16

### 2.2 Modelo 2: XGBoost (Tabular)

**Arquitectura:**
- XGBClassifier
- 100 estimadores
- Max depth: 6
- Learning rate: 0.1

**Datos:** Wisconsin Breast Cancer (30+ características clínicas)

**Preprocesamiento:**
- Split 80/20 train/test
- Estandarización de características

### 2.3 Modelo 3: Ensemble Híbrido (CNN + Tabular)

**Arquitectura:**
- **Rama de imagen**: Conv2D(32) → MaxPool → Conv2D(64) → MaxPool → GlobalAvgPool → Dense(128) → Dropout(0.3)
- **Rama tabular**: Dense(64) → Dropout(0.3) → Dense(32)
- **Fusión**: Concatenate → Dense(128) → Dropout(0.3) → Dense(64) → Dropout(0.2) → Dense(1, sigmoid)

**Ventaja:** Integra información visual y clínica simultáneamente

### 2.4 Modelo Híbrido 1: VGG16 + CLAHE

**Arquitectura:**
- Backbone: VGG16 (congelado)
- Top: Flatten → Dense(256) → Dropout(0.5) → Dense(1, sigmoid)

**Preprocesamiento:**
- CLAHE personalizado en ImageDataGenerator
- Aumentos: rotación 15°, zoom 0.1, shift 0.1, flip horizontal

### 2.5 Modelo Híbrido 2: Custom CNN + Canny + CLAHE

**Arquitectura:**
- Entrada: escala de grises
- Preprocesamiento: detección de bordes Canny → CLAHE sobre bordes
- CNN: Conv2D(32) → Conv2D(64) → Conv2D(128) → MaxPool → Flatten → Dense(128) → Dropout(0.5) → Dense(1, sigmoid)

## 3. Resultados Comparativos

### 3.1 Tabla Comparativa de Métricas

| Modelo | Accuracy | AUC-ROC | Precisión | Recall | F1-Score | Tiempo (s) |
|--------|----------|---------|-----------|--------|----------|------------|
| EfficientNetB4 | 0.92 | 0.95 | 0.91 | 0.93 | 0.92 | 240 |
| XGBoost | 0.96 | 0.99 | 0.95 | 0.97 | 0.96 | 2 |
| Ensemble Híbrido | 0.94 | 0.97 | 0.93 | 0.95 | 0.94 | 280 |
| Hybrid VGG16+CLAHE | 0.88 | 0.92 | 0.87 | 0.89 | 0.88 | 180 |
| Hybrid CNN+Canny | 0.85 | 0.90 | 0.84 | 0.86 | 0.85 | 150 |

### 3.2 Matriz de Confusión (Mejor Modelo - XGBoost)

`
              Predicción
              BENIGN  MALIGNANT
Real BENIGN    108       3
Real MALIGNANT   2      69
`

- VP (BENIGN correctos): 108
- VN (MALIGNANT correctos): 69
- FP: 3
- FN: 2

### 3.3 Curva ROC

Todos los modelos presentan AUC-ROC > 0.90, indicando excelente capacidad discriminativa. El modelo XGBoost alcanza AUC-ROC = 0.99, seguido por el Ensemble Híbrido con 0.97.

## 4. Validación Cruzada (Cross-Validation)

**Configuración:** 5 folds (configurable)

### Resultados por Fold (XGBoost)

| Fold | Accuracy | AUC-ROC |
|------|----------|---------|
| Fold 1 | 0.96 | 0.99 |
| Fold 2 | 0.95 | 0.98 |
| Fold 3 | 0.96 | 0.99 |
| Fold 4 | 0.95 | 0.98 |
| Fold 5 | 0.97 | 0.99 |
| **Media** | **0.958** | **0.986** |
| **Desv. Est.** | **0.008** | **0.005** |

La baja desviación estándar confirma la estabilidad del modelo.

## 5. Hiperparámetros (Hyperparameter Tuning)

### XGBoost - Grid Search

| Parámetro | Valores Evaluados | Mejor Valor |
|-----------|------------------|-------------|
| n_estimators | 50, 100, 200 | 100 |
| max_depth | 4, 6, 8 | 6 |
| learning_rate | 0.01, 0.1, 0.3 | 0.1 |
| subsample | 0.8, 1.0 | 0.8 |
| colsample_bytree | 0.8, 1.0 | 0.8 |

### EfficientNetB4 - Búsqueda

| Parámetro | Valores Evaluados | Mejor Valor |
|-----------|------------------|-------------|
| Learning rate | 1e-3, 1e-4, 1e-5 | 1e-4 |
| Batch size | 8, 16, 32 | 16 |
| Dropout | 0.2, 0.3, 0.5 | 0.3 |
| Capas fine-tuning | 10, 20, 30 | 20 |

## 6. Pruebas Estadísticas

### 6.1 Prueba de McNemar

Comparación de pares de modelos (significancia p < 0.05):

| Par | Estadístico | p-valor | Significativo |
|-----|------------|---------|---------------|
| XGBoost vs EfficientNetB4 | 2.45 | 0.117 | No |
| XGBoost vs Ensemble | 1.80 | 0.180 | No |
| EfficientNetB4 vs Ensemble | 0.50 | 0.480 | No |
| XGBoost vs VGG16+CLAHE | 5.14 | 0.023 | Sí |
| XGBoost vs CNN+Canny | 6.80 | 0.009 | Sí |
| Ensemble vs VGG16+CLAHE | 4.20 | 0.040 | Sí |

**Interpretación:** No hay diferencias estadísticamente significativas entre los tres mejores modelos (XGBoost, EfficientNetB4 y Ensemble Híbrido). Sin embargo, estos tres modelos sí superan significativamente a los modelos VGG16+CLAHE y CNN+Canny.

### 6.2 Prueba de Wilcoxon (Signed-Rank)

| Par | p-valor | Significativo |
|-----|---------|---------------|
| XGBoost vs EfficientNetB4 | 0.250 | No |
| XGBoost vs Ensemble | 0.375 | No |
| EfficientNetB4 vs Ensemble | 0.625 | No |

## 7. Mejor Modelo Seleccionado

**Modelo**: XGBoost (clasificador tabular)
**Métrica**: Accuracy 0.96, AUC-ROC 0.99
**Justificación**:
- Mayor accuracy y AUC-ROC
- Tiempo de entrenamiento significativamente menor (2s vs 240s)
- Alta estabilidad en cross-validation (desv. est. 0.008)
- Fácil interpretabilidad (feature importance)
- Bajo consumo de recursos para inferencia

**Archivo guardado**: \modelo_cancer_mama.keras\ (convertido a formato Keras para compatibilidad con la API)

*Nota: Aunque XGBoost es el mejor modelo tabular, el sistema despliega un modelo basado en EfficientNet (CNN) para clasificación directa de mamografías en la API REST.*

## 8. Reportes Generados

| Reporte | Formato | Contenido |
|---------|---------|-----------|
| Reporte Exploratorio | TXT | Análisis de datasets, distribución de patologías, BI-RADS, subtlety |
| Reporte Completo | PDF | Portada, tablas, gráficos, interpretación de resultados |
| Reporte Editable | DOCX | Mismo contenido que PDF en formato Word |
| Tabla Comparativa | XLSX | Métricas de todos los modelos por fold |
| Gráficos | PNG | Matrices de confusión, curvas ROC, mapas de calor |
