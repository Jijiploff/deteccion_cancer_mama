# Sistema de Diagnóstico de Cáncer de Mama

Sistema automatizado de apoyo diagnóstico para clasificación de mamografías en hallazgos benignos o malignos mediante aprendizaje profundo (Deep Learning).

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + Vite 5 + Tailwind CSS 3 |
| Backend | FastAPI + Uvicorn |
| Modelo | TensorFlow/Keras (EfficientNet) |
| Contenedores | Docker + docker-compose |
| Despliegue | Render (backend) + Vercel (frontend) |

## Estructura del Proyecto

````
deteccion_cancer_mama/
├── backend/              # API RESTful (FastAPI)
│   ├── app/              # Código fuente del backend
│   ├── models/           # Modelos entrenados (.keras)
│   ├── Dockerfile        # Imagen para contenedor
│   └── requirements.txt  # Dependencias Python
├── frontend/             # Interfaz de usuario (React)
│   ├── src/              # Componentes y hooks
│   ├── Dockerfile        # Construcción multi-etapa
│   └── nginx.conf        # Configuración de Nginx
├── docs/                 # Documentación del proyecto
└── docker-compose.yml    # Orquestación de servicios
````

## Inicio Rápido

### Con Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Documentación API: http://localhost:8000/docs

### Sin Docker

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Documentación

- [Manual de Instalación](docs/MANUAL_DE_INSTALACION.md)
- [Manual de Usuario](docs/MANUAL_DE_USUARIO.md)
- [Diagramas del Sistema](docs/DIAGRAMAS.md)
- [Reporte Técnico de Modelos](docs/REPORTE_MODELOS.md)

## Despliegue

- **Backend**: Render (servicio web desde Dockerfile)
- **Frontend**: Vercel (importar repositorio, build `npm run build`)
- **Versiones**: GitHub
- **Documentación**: Jira

## Licencia

Proyecto académico - Grupo 07
