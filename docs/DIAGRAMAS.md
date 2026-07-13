# Diagramas del Sistema

## 1. Diagrama de Arquitectura

```mermaid
graph TB
    subgraph "Cliente"
        BROWSER["Navegador Web"]
    end

    subgraph "Frontend (Vercel / Localhost:3000)"
        REACT["React App (Vite + Tailwind)"]
        NGINX["Nginx (servir SPA)"]
        REACT --> NGINX
    end

    subgraph "Backend (Render / Localhost:8000)"
        FASTAPI["FastAPI + Uvicorn"]
        MODEL_HANDLER["ModelHandler (TensorFlow/Keras)"]
        SECURITY["Security (validacion archivos)"]
        SCHEMAS["Schemas (Pydantic)"]
        HISTORY["Historial (deque en memoria)"]
        FASTAPI --> MODEL_HANDLER
        FASTAPI --> SECURITY
        FASTAPI --> SCHEMAS
        FASTAPI --> HISTORY
    end

    subgraph "Almacenamiento"
        MODEL_FILE["modelo_cancer_mama.keras (TensorFlow SavedModel)"]
    end

    subgraph "Google Colab (Entrenamiento)"
        COLAB["Jupyter Notebook"]
        DRIVE["Google Drive (CBIS-DDSM + Wisconsin)"]
        TRAINING["Pipeline de Entrenamiento - EDA - 5 Modelos - Cross-validation - Hyperparameter Tuning"]
        REPORTS["Reportes (PDF, Word, Excel)"]
        COLAB --> DRIVE
        COLAB --> TRAINING
        TRAINING --> REPORTS
        TRAINING --> MODEL_FILE
    end

    BROWSER <-->|HTTP/HTTPS| NGINX
    NGINX <-->|API Calls| FASTAPI
    MODEL_HANDLER --> MODEL_FILE
```

## 2. Diagrama de Modelo de Datos

```mermaid
classDiagram
    class PredictionResponse {
        +str prediction_id
        +str label
        +float confidence
        +PredictionProbabilities probabilities
        +float processing_time_ms
        +datetime timestamp
        +str filename
        +Optional[str] warning
    }

    class PredictionProbabilities {
        +float benign
        +float malignant
    }

    class HistoryItem {
        +str prediction_id
        +str filename
        +str label
        +float confidence
        +datetime timestamp
    }

    class HistoryResponse {
        +int total
        +list[HistoryItem] items
    }

    class HealthResponse {
        +str status
        +bool model_loaded
        +str model_path
        +float uptime_seconds
        +str version
        +str environment
    }

    class ErrorResponse {
        +str error
        +str detail
    }

    PredictionResponse --> PredictionProbabilities
    HistoryResponse --> "*" HistoryItem
```

## 3. Diagrama de Componentes

```mermaid
graph TB
    subgraph "Frontend (React)"
        APP["App (State Machine)"]
        HEADER["Header"]
        HERO["Hero"]
        UPLOAD["UploadPanel (drag and drop + validacion)"]
        RESULT["ResultPanel"]
        GAUGE["ConfidenceGauge (barra probabilidades)"]
        HISTORY["HistoryList"]
        FOOTER["Footer"]
        SPINNER["Spinner"]
        TOOLTIP["Tooltip"]
        API["api.js (fetch wrapper)"]
        DARK["useDarkMode"]
        HIST_HOOK["useHistory"]

        APP --> HEADER
        APP --> HERO
        APP --> UPLOAD
        APP --> RESULT
        APP --> HISTORY
        APP --> FOOTER
        RESULT --> GAUGE
        RESULT --> SPINNER
        UPLOAD --> SPINNER
        APP --> API
        APP --> DARK
        APP --> HIST_HOOK
        HIST_HOOK --> API
    end

    subgraph "Backend (FastAPI)"
        MAIN["main.py (endpoints + middleware)"]
        CONFIG["config.py (Settings)"]
        LOGGING["logging_config.py"]
        MODEL_HANDLER["model_handler.py (carga, preprocesamiento, predict)"]
        SECURITY["security.py (validacion uploads)"]
        SCHEMAS["schemas.py (modelos Pydantic)"]

        MAIN --> CONFIG
        MAIN --> LOGGING
        MAIN --> MODEL_HANDLER
        MAIN --> SECURITY
        MAIN --> SCHEMAS
    end

    subgraph "Infraestructura"
        DOCKER["Docker Compose"]
        DOCKER_BE["Backend Container (Python 3.10-slim)"]
        DOCKER_FE["Frontend Container (Node build + Nginx)"]
        VOLUME["Volumen: ./backend/models"]
        NETWORK["Red: cancer-mama-net"]

        DOCKER --> DOCKER_BE
        DOCKER --> DOCKER_FE
        DOCKER_BE --> VOLUME
        DOCKER_BE --> NETWORK
        DOCKER_FE --> NETWORK
    end

    API <-->|HTTP| MAIN
    MODEL_HANDLER -->|load/predict| TF["TensorFlow/Keras"]
```

## 4. Diagramas de Secuencia

### 4.1 Flujo de Prediccion

```mermaid
sequenceDiagram
    actor Usuario
    participant Frontend as Frontend (React)
    participant API as api.js
    participant Backend as Backend (FastAPI)
    participant Security as security.py
    participant Handler as model_handler.py
    participant Model as TensorFlow Model

    Usuario->>Frontend: Arrastra imagen al UploadPanel
    Frontend->>Frontend: Valida tipo y tamano
    Frontend->>Frontend: Muestra preview + spinner
    Frontend->>API: POST /predict (FormData)

    API->>Backend: Envia peticion HTTP

    Backend->>Security: validate_upload_image(file)
    Security->>Security: Verifica content-type
    Security->>Security: Verifica extension
    Security->>Security: Verifica tamano
    Security-->>Backend: bytes de imagen

    Backend->>Handler: predict(raw_bytes)
    Handler->>Handler: _preprocess()
    Handler->>Handler: Decodificar PIL RGB
    Handler->>Handler: Redimensionar 224x224
    Handler->>Handler: Aplicar CLAHE (LAB)
    Handler->>Handler: Normalizar [0,1]
    Handler->>Handler: Expand dims (batch)

    Handler->>Model: model.predict(tensor)
    Model-->>Handler: raw_output (sigmoid/softmax)

    Handler->>Handler: Interpretar salida
    Handler->>Handler: Calcular label, confidence
    Handler-->>Backend: dict con resultados

    Backend->>Backend: Generar UUID
    Backend->>Backend: Guardar en history deque
    Backend-->>API: PredictionResponse (JSON)

    API-->>Frontend: Respuesta JSON
    Frontend->>Frontend: Mostrar ResultPanel
    Frontend->>Frontend: Actualizar ConfidenceGauge
    Frontend->>Frontend: Recargar HistoryList
    Frontend-->>Usuario: Muestra diagnostico
```

### 4.2 Flujo de Health Check

```mermaid
sequenceDiagram
    participant Frontend as Frontend (React)
    participant Backend as Backend (FastAPI)
    participant Handler as model_handler.py

    Note over Frontend: Al cargar la pagina
    Frontend->>Backend: GET /health
    Backend->>Handler: Verificar is_loaded
    Handler-->>Backend: True / False
    Backend-->>Frontend: HealthResponse

    alt model_loaded = true
        Frontend->>Frontend: Habilitar UI
    else model_loaded = false
        Frontend->>Frontend: Mostrar banner de error
    end
```

### 4.3 Flujo de Entrenamiento en Colab

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Colab as Google Colab
    participant Drive as Google Drive
    participant Model as Modelos

    User->>Colab: Abrir notebook
    Colab->>Colab: Montar Google Drive
    Colab->>Colab: Instalar dependencias

    Note over Colab: PASO 1: EDA
    Colab->>Drive: Cargar CSVs + imagenes
    Colab->>Colab: Analisis exploratorio
    Colab->>Colab: Graficos de distribucion
    Colab->>Drive: Guardar exploratory_report.txt

    Note over Colab: PASO 2: Entrenamiento
    Colab->>Model: Entrenar CNN Transfer Learning
    Colab->>Model: Entrenar XGBoost Tabular
    Colab->>Model: Entrenar Ensemble Hibrido
    Colab->>Model: Entrenar Hybrid VGG16+CLAHE
    Colab->>Model: Entrenar Hybrid Custom CNN+Canny

    Note over Colab: PASO 3: Evaluacion
    Colab->>Colab: Cross-validation (5 folds)
    Colab->>Colab: Hyperparameter tuning
    Colab->>Colab: Pruebas estadisticas (McNemar)

    Note over Colab: PASO 4: Reportes
    Colab->>Drive: Guardar modelos (.keras, .pkl)
    Colab->>Drive: Exportar PDF, Word, Excel
    Colab->>Drive: Tablas comparativas + graficos

    User->>Drive: Descargar mejor modelo
    User->>User: Colocar en backend/models/
```

### 4.4 Flujo de Historial

```mermaid
sequenceDiagram
    participant Frontend as Frontend (React)
    participant API as api.js
    participant Backend as Backend (FastAPI)
    participant Memory as deque (memoria)

    Note over Frontend: Al cargar / tras prediccion
    Frontend->>API: fetchHistory()
    API->>Backend: GET /history
    Backend->>Memory: Obtener items
    Memory-->>Backend: list[HistoryItem]
    Backend-->>API: HistoryResponse
    API-->>Frontend: items + total
    Frontend->>Frontend: Renderizar HistoryList

    Note over Frontend: Usuario hace clic en Limpiar
    Frontend->>API: clearHistory()
    API->>Backend: DELETE /history
    Backend->>Memory: clear()
    Backend-->>API: {"message": "Historial limpiado"}
    API-->>Frontend: Confirmacion
    Frontend->>Frontend: Vaciar lista
```

## 5. Diagramas de Estados

### 5.1 Estados de la Aplicacion

```mermaid
stateDiagram-v2
    [*] --> idle: App iniciada

    idle --> loading: Usuario selecciona imagen
    idle --> idle: Error de validacion (tipo/tamano)

    loading --> success: Prediccion exitosa
    loading --> error: Error de red o API
    loading --> idle: Cancelar (no implementado)

    success --> loading: Nueva imagen seleccionada
    success --> idle: Recargar pagina

    error --> loading: Reintentar
    error --> idle: Recargar pagina

    state idle {
        [*] --> checking_api
        checking_api --> api_ok: /health responde
        checking_api --> api_down: /health falla
        api_ok --> [*]
        api_down --> [*]
    }

    state loading {
        [*] --> uploading
        uploading --> processing: Imagen recibida
        processing --> classifying: Preprocesamiento OK
        classifying --> [*]: Resultado obtenido
    }

    state success {
        [*] --> show_result
        show_result --> show_warning: confidence < 65%
        show_warning --> [*]
        show_result --> [*]
    }
```

### 5.2 Estados del Modelo

```mermaid
stateDiagram-v2
    [*] --> not_loaded: App inicia

    not_loaded --> loading_model: lifespan startup
    loading_model --> loaded: load() exitoso
    loading_model --> error: load() falla

    loaded --> predicting: POST /predict
    predicting --> loaded: predict() exitoso
    predicting --> loaded: predict() falla (error imagen)

    error --> loading_model: Reinicio de app
    error --> [*]: App detenida

    loaded --> [*]: App detenida (shutdown)
```

### 5.3 Estados del Historial

```mermaid
stateDiagram-v2
    [*] --> empty: Sin predicciones

    empty --> populated: POST /predict exitoso
    populated --> populated: Nueva prediccion agregada

    populated --> empty: DELETE /history
    populated --> populated: Vista recargada

    state populated {
        [*] --> has_items
        has_items --> full: 50 items alcanzados
        full --> has_items: Nuevo item, se descarta el mas antiguo (FIFO)
    }
```

## 6. Diagrama de Despliegue

```mermaid
graph TB
    subgraph "Desarrollo Local"
        DEV_FE["Frontend Dev (Vite :5173)"]
        DEV_BE["Backend Dev (Uvicorn :8000)"]
        DEV_FE -->|HTTP| DEV_BE
    end

    subgraph "Docker (Local)"
        DOCKER_FE["Frontend (Nginx :3000)"]
        DOCKER_BE["Backend (FastAPI :8000)"]
        DOCKER_VOL["Volumen ./backend/models"]
        DOCKER_NET["Red interna"]

        DOCKER_FE -->|API calls| DOCKER_BE
        DOCKER_BE --> DOCKER_VOL
        DOCKER_FE --> DOCKER_NET
        DOCKER_BE --> DOCKER_NET
    end

    subgraph "Produccion"
        VERCEL["Vercel (Frontend React SPA)"]
        RENDER["Render (Backend FastAPI Docker)"]

        DNS["Usuario"] -->|HTTPS| VERCEL
        VERCEL -->|HTTPS| RENDER
        RENDER -->|healthcheck| RENDER
    end

    subgraph "Entrenamiento"
        COLAB["Google Colab"]
        GDRIVE["Google Drive (Dataset + Resultados)"]
        GITHUB["GitHub (Control de versiones)"]
        JIRA["Jira (Documentacion)"]

        COLAB --> GDRIVE
        COLAB -->|modelo.keras| RENDER
        COLAB --> GITHUB
    end
```
