# Manual de Implementación: Descarga de Modelos desde Google Drive

## Problema

Los modelos de machine learning (`cnn_efficientnet_20260707_061411.keras` ~148 MB,
`best_cnn_efficientnet.h5` ~109 MB) superan el límite de 100 MB de GitHub, por lo que
no pueden subirse al repositorio. Este manual explica cómo alojarlos en Google Drive
y hacer que FastAPI los descargue automáticamente al iniciar.

---

## 1. Subir los modelos a Google Drive

1. Ve a [https://drive.google.com](https://drive.google.com) e inicia sesión con tu cuenta de Google.
2. Haz clic en **"+ Nuevo" → "Subir archivo"**.
3. Sube los **4 archivos** que están en la carpeta `backend/models/` de tu proyecto:

   | Archivo | Tamaño aprox. |
   |---------|--------------|
   | `cnn_efficientnet_20260707_061411.keras` | 148 MB |
   | `best_cnn_efficientnet.h5` | 109 MB |
   | `ensemble_20260707_061411.keras` | 291 KB |
   | `tabular_20260707_061411.pkl` | 117 KB |

> **Nota:** La subida puede tardar unos minutos para los archivos grandes.

---

## 2. Obtener los FILE_ID de cada modelo

Cada archivo en Google Drive tiene un identificador único (`FILE_ID`) que necesitamos
para la descarga programática.

1. En Google Drive, localiza uno de los archivos subidos.
2. Haz clic derecho sobre el archivo → **"Compartir"** → **"Compartir"**.
3. En la ventana que aparece, haz clic en **"Cualquier persona con el enlace"**.
   Asegúrate de que el permiso sea **"Lector"**.
4. Haz clic en **"Copiar enlace"**.
5. El enlace tiene este formato:

   ```
   https://drive.google.com/file/d/1ABCdefGHIjklMNOpqrSTUvwXYZ12345/view?usp=sharing
   ```

6. El **FILE_ID** es la parte que está entre `/d/` y `/view`:

   ```
   1ABCdefGHIjklMNOpqrSTUvwXYZ12345
   ```

7. Repite los pasos 2 a 6 para los **4 archivos**.

Guarda los 4 FILE_ID en un bloc de notas, los necesitarás después.

---

## 3. Configurar las variables de entorno

1. Abre el archivo `backend/.env` en tu editor de código.
2. Agrega los FILE_ID al final del archivo, reemplazando los valores de ejemplo
   con los tuyos:

   ```env
   CNN_MODEL_FILE_ID=1ABCdefGHIjklMNOpqrSTUvwXYZ12345
   ENSEMBLE_MODEL_FILE_ID=2DEFghiJKlmnoPQRstuVWXyz67890
   TABULAR_MODEL_FILE_ID=3GHIjklMNOPqrSTUvwxYZabc90123
   ```

3. Guarda el archivo.

> **Importante:** `backend/.env` está en `.gitignore`, por lo que los FILE_ID
> nunca se subirán al repositorio de GitHub.

---

## 4. Verificar que los modelos están excluidos de git

El archivo `.gitignore` que creamos en la raíz del proyecto ya contiene:

```
backend/models/
backend/.env
```

Esto asegura que:

- Los archivos de modelos (`.keras`, `.h5`, `.pkl`) **no** se suben a GitHub.
- El archivo `.env` con tus FILE_ID **no** se sube a GitHub.
- Cualquier desarrollador que clone el repo podrá descargar los modelos
  automáticamente al ejecutar la aplicación.

Puedes verificar que git no está trackeando los modelos con:

```bash
git ls-files backend/models/
```

Si no muestra nada, estás listo.

---

## 5. Cómo funciona el sistema de descarga

### Flujo general

```
Inicio de FastAPI
       │
       ▼
model_handler.load()
       │
       ├── ¿Hay CNN_MODEL_FILE_ID configurado?
       │      ├── Sí → ¿Ya existe el archivo local?
       │      │         ├── Sí → Saltar descarga
       │      │         └── No  → Descargar de Google Drive (gdown)
       │      └── No  → Usar archivo local en backend/models/
       │
       ├── (lo mismo para Ensemble y XGBoost)
       │
       ▼
   Modelos cargados y listos para predicción
```

### Si el archivo local ya existe

El sistema **no** lo descarga de nuevo, lo usa directamente. Esto evita
descargar 148 MB cada vez que reinicias la app.

### Si falla la descarga

El módulo `download_models.py` reintenta hasta 3 veces con un intervalo
entre intentos. Si aún así falla, el modelo se marca como `"error"` en
el endpoint `/health` y la API igual puede funcionar con los modelos
que sí se cargaron.

---

## 6. Usar con Docker local

### Opción A: Usar modelos locales (sin build args)

Si tienes los modelos en `backend/models/` localmente, Docker los incluirá
en la imagen automáticamente:

```bash
docker-compose up --build
```

### Opción B: Descargar modelos durante el build

Si no tienes los modelos localmente (por ejemplo, después de clonar el repo),
puedes pasar los FILE_ID como build args:

```bash
docker build \
  --build-arg CNN_MODEL_FILE_ID=1ABCdefGHIjklMNOpqrSTUvwXYZ12345 \
  --build-arg ENSEMBLE_MODEL_FILE_ID=2DEFghiJKlmnoPQRstuVWXyz67890 \
  --build-arg TABULAR_MODEL_FILE_ID=3GHIjklMNOPqrSTUvwxYZabc90123 \
  -t backend-api \
  ./backend
```

O con docker-compose, edita `docker-compose.yml` y agrega los build args
en el servicio `backend`:

```yaml
services:
  backend:
    build:
      context: ./backend
      args:
        CNN_MODEL_FILE_ID: 1ABCdefGHIjklMNOpqrSTUvwXYZ12345
        ENSEMBLE_MODEL_FILE_ID: 2DEFghiJKlmnoPQRstuVWXyz67890
        TABULAR_MODEL_FILE_ID: 3GHIjklMNOPqrSTUvwxYZabc90123
```

---

## 7. Usar en Render (producción)

1. En tu dashboard de Render, ve a tu servicio backend.
2. Ve a **"Environment"** (o "Environment Variables").
3. Agrega las 3 variables de entorno:

   | Variable | Valor |
   |----------|-------|
   | `CNN_MODEL_FILE_ID` | `1ABCdefGHIjklMNOpqrSTUvwXYZ12345` |
   | `ENSEMBLE_MODEL_FILE_ID` | `2DEFghiJKlmnoPQRstuVWXyz67890` |
   | `TABULAR_MODEL_FILE_ID` | `3GHIjklMNOPqrSTUvwxYZabc90123` |

4. Guarda y redeploya.

Render usará el `Dockerfile` que ya incluye el paso `RUN python -m app.download_models`.
Los modelos se descargarán durante el build y quedarán incluidos en la imagen.

---

## 8. Verificar que todo funciona

1. Inicia la aplicación (local o Docker).
2. Abre en el navegador: `http://localhost:8000/docs` (Swagger UI).
3. Revisa el endpoint `GET /health`. Deberías ver:

   ```json
   {
     "status": "healthy",
     "models_loaded": {
       "CNN": true,
       "Ensemble": true,
       "XGBoost": true
     },
     "environment": "development"
   }
   ```

4. Si algún modelo no se cargó, revisa los logs del servidor para ver
   si hubo error en la descarga.

---

## 9. Ejemplo de logs esperados

Cuando la aplicación inicia y los modelos no existen localmente, verás:

```
INFO | Iniciando aplicación, cargando modelos...
INFO | Descargando CNN (EfficientNet) desde Google Drive (file_id=1ABC...)
Downloading...
From: https://drive.google.com/uc?id=1ABC...
To: C:\...\backend\models\cnn_efficientnet_20260707_061411.keras
100%|████████████████████| 148M/148M [00:45<00:00, 3.2MB/s]
INFO | CNN (EfficientNet) descargado correctamente (155667931 bytes)
INFO | Modelo CNN cargado correctamente.
INFO | ... (similar para Ensemble y XGBoost)
```

Si los modelos ya existen localmente:

```
INFO | Iniciando aplicación, cargando modelos...
INFO | CNN (EfficientNet) ya existe en ...models\cnn_efficientnet_20260707_061411.keras, saltando descarga
INFO | Modelo CNN cargado correctamente.
```

---

## 10. Solución de problemas

### Error: "gdown: No module named gdown"

Ejecuta:

```bash
pip install gdown>=5.1.0
```

### Error: "Download returned 403 Forbidden"

Asegúrate de que el archivo en Google Drive tenga el permiso
**"Cualquier persona con el enlace → Lector"**. Si está como
"Restringido", la descarga automática fallará.

### Error: "El archivo descargado está vacío o es corrupto"

El sistema reintenta automáticamente hasta 3 veces. Si persiste,
verifica que el FILE_ID sea correcto y que el archivo en Google
Drive no esté dañado.

### Los modelos no aparecen después de clonar el repo

Es normal. Ejecuta la aplicación y los modelos se descargarán
automáticamente al iniciar. O puedes ejecutar manualmente:

```bash
cd backend
python -m app.download_models
```
