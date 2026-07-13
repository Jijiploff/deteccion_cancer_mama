# Manual de Instalación

Sistema de Diagnóstico Automatizado de Cáncer de Mama mediante Aprendizaje Automático.

## 1. Requisitos del Sistema

### Hardware
| Componente | Requisito Mínimo | Recomendado |
|------------|-----------------|-------------|
| Procesador | Dual-core 2.0 GHz | Quad-core 3.0 GHz+ |
| RAM | 4 GB | 8 GB+ |
| Disco | 10 GB libres | 20 GB+ (SSD) |
| GPU | No requerida | NVIDIA GTX 1060+ (para entrenamiento) |

### Software
| Componente | Versión | Descarga |
|------------|---------|----------|
| Docker | 24+ | https://docs.docker.com/get-docker/ |
| Docker Compose | 2.20+ | Incluido con Docker Desktop |
| Python | 3.10+ | https://www.python.org/downloads/ |
| Node.js | 20+ | https://nodejs.org/ |
| Git | 2.40+ | https://git-scm.com/ |

### Navegadores Soportados
- Google Chrome 90+
- Mozilla Firefox 90+
- Microsoft Edge 90+
- Safari 15+

## 2. Despliegue con Docker (Recomendado)

### 2.1 Clonar el Repositorio
`ash
git clone https://github.com/tu-usuario/deteccion_cancer_mama.git
cd deteccion_cancer_mama
`

### 2.2 Agregar el Modelo Entrenado
Coloca el archivo del modelo entrenado (\modelo_cancer_mama.keras\) en la carpeta:
`
backend/models/
`

### 2.3 Configurar Variables de Entorno (Opcional)
Edita \docker-compose.yml\ o crea un archivo \.env\:

`env
# Backend
MODEL_PATH=/app/models/modelo_cancer_mama.keras
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
APPLY_CLAHE=true
PREDICTION_THRESHOLD=0.5
MAX_FILE_SIZE_MB=5
RATE_LIMIT_PREDICT=10/minute
RATE_LIMIT_DEFAULT=60/minute
HISTORY_MAX_ITEMS=50

# Frontend
VITE_API_URL=http://localhost:8000
`

### 2.4 Construir y Ejecutar
`ash
docker-compose up --build
`

### 2.5 Verificar la Instalación
- **Frontend**: http://localhost:3000
- **Backend (health check)**: http://localhost:8000/health
- **Documentación API (Swagger)**: http://localhost:8000/docs

### 2.6 Detener los Servicios
`ash
docker-compose down
`

## 3. Despliegue Manual (Sin Docker)

### 3.1 Backend (FastAPI)

`ash
# Crear y activar entorno virtual
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
`

### 3.2 Frontend (React + Vite)

`ash
cd frontend
npm install
npm run dev
`

El frontend estará disponible en http://localhost:5173.

## 4. Entrenamiento del Modelo en Google Colab

### 4.1 Preparación del Dataset
1. Descarga el dataset CBIS-DDSM y Wisconsin Breast Cancer Database
2. Sube los archivos a Google Drive en la siguiente estructura:
`
DataSet/
├── BreastCancer_Images/jpeg/
├── CSVFiles/
│   ├── calc_case_description_train_set.csv
│   ├── calc_case_description_test_set.csv
│   ├── mass_case_description_train_set.csv
│   ├── mass_case_description_test_set.csv
│   ├── meta.csv
│   └── dicom_info.csv
├── BreastCancer_Tabular/
│   └── data.csv
└── Database/
`

### 4.2 Ejecutar el Notebook
1. Abre Google Colab: https://colab.research.google.com/
2. Sube el notebook o copia el código de \docs/_CODIGO_FUENTE_CONTENIDO.txt\
3. Ejecuta las celdas en orden:
   - Montar Google Drive
   - Instalar dependencias
   - Importar librerías
   - Verificar estructura de Drive
   - Análisis Exploratorio (EDA)
   - Entrenamiento de modelos
   - Evaluación y reportes

### 4.3 Obtener el Modelo Entrenado
El modelo entrenado se guardará en:
`
/content/drive/MyDrive/DataSet/Resultados/modelo_cancer_mama.keras
`

Descarga este archivo y colócalo en \ackend/models/\.

## 5. Despliegue en Producción

### 5.1 Backend en Render

1. Crea una cuenta en https://render.com
2. Conecta tu repositorio de GitHub
3. Crea un nuevo **Web Service**
   - **Name**: \cancer-mama-backend\
   - **Root Directory**: \ackend\
   - **Runtime**: \Docker\
   - **Build Command**: (dejar vacío)
   - **Start Command**: (dejar vacío)
   - **Port**: \8000\
4. Variables de entorno:
   `
   MODEL_PATH=/app/models/modelo_cancer_mama.keras
   ENVIRONMENT=production
   APPLY_CLAHE=true
   PREDICTION_THRESHOLD=0.5
   LOG_LEVEL=INFO
   RATE_LIMIT_PREDICT=10/minute
   RATE_LIMIT_DEFAULT=60/minute
   `
5. Sube el modelo entrenado como artefacto o usa un volumen persistente
6. Haz clic en **Deploy**

### 5.2 Frontend en Vercel

1. Crea una cuenta en https://vercel.com
2. Importa el repositorio de GitHub
3. Configura:
   - **Root Directory**: \rontend\
   - **Build Command**: \
pm run build\
   - **Output Directory**: \dist\
4. Variables de entorno:
   `
   VITE_API_URL=https://tu-backend.onrender.com
   `
5. Haz clic en **Deploy**

## 6. Solución de Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| El backend no inicia | Puerto 8000 ocupado | Cambia el puerto en \docker-compose.yml\ |
| Error "Model not found" | Modelo no está en \ackend/models/\ | Coloca el archivo \.keras\ en la carpeta models |
| Error de conexión a Drive | Ruta incorrecta | Verifica que la estructura de carpetas coincida |
| Imágenes no cargan | Formato incorrecto | Usa JPG o PNG, máximo 5MB |
| Frontend no conecta con backend | CORS mal configurado | Verifica \FRONTEND_URL\ o \VITE_API_URL\ |
