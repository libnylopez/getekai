# UVG-Agent 🎓

**Sistema de Consultas Inteligentes con RAG (Retrieval-Augmented Generation)**

API REST desarrollada con FastAPI que integra Claude Sonnet 4 de Anthropic y la plataforma Nuclia para proporcionar respuestas precisas basadas en documentos académicos mediante búsqueda híbrida y generación de lenguaje natural.

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Diagrama de Flujo](#-diagrama-de-flujo)
- [Solución de Problemas](#-solución-de-problemas)
- [Tecnologías](#-tecnologías)

---

## 🎯 Descripción General

UVG-Agent es un servicio backend inteligente que implementa un pipeline completo de RAG (Retrieval-Augmented Generation) para responder preguntas académicas. El sistema:

1. **Preprocesa** las consultas del usuario con IA para optimizarlas
2. **Busca** información relevante en Nuclia usando búsqueda híbrida (keyword + semántica)
3. **Extrae** metadata completa de los documentos (títulos, páginas, scores, URLs)
4. **Construye** un contexto enriquecido con los fragmentos más relevantes
5. **Genera** respuestas precisas usando Claude Sonnet 4

---

## ✨ Características

### Funcionalidades Principales

- 🚀 **API REST con FastAPI** - Alto rendimiento y documentación automática
- 🤖 **Claude Sonnet 4** - Modelo de lenguaje más avanzado de Anthropic
- 📚 **Integración con Nuclia** - Plataforma RAG profesional
- 🔍 **Búsqueda Híbrida** - Combina búsqueda por palabras clave y semántica
- 📊 **Filtrado Inteligente** - Control de relevancia con `min_score`
- 📄 **Metadata Enriquecida** - Títulos, páginas, scores y URLs de documentos
- ⚙️ **Preprocesamiento de Consultas** - Optimización automática con LLM
- 🎯 **Pipeline RAG Completo** - Proceso end-to-end automatizado
- 🔧 **Altamente Configurable** - Parámetros ajustables por consulta
- 📝 **Código Modular** - Arquitectura limpia y extensible

---

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Cliente       │ (Postman, Frontend, etc.)
└────────┬────────┘
         │ HTTP POST /ask
         ▼
┌─────────────────┐
│   FastAPI       │ (app/main.py)
│   - CORS        │
│   - Validación  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Agent         │ (app/agent.py)
│   - Orquesta    │
│   - Pipeline    │
└────────┬────────┘
         │
         ├─────────────────────┐
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│   LLM Module    │   │  Nuclia Client  │
│  (app/llm.py)   │   │ (app/nuclia.py) │
└────────┬────────┘   └────────┬────────┘
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│  Claude API     │   │   Nuclia API    │
│  (Anthropic)    │   │   (Search)      │
└─────────────────┘   └─────────────────┘
```

---

## 📁 Estructura del Proyecto

```
UVG-Agent-sonnet/
│
├── app/                          # Código principal de la aplicación
│   ├── __init__.py              # Inicialización del paquete Python
│   ├── main.py                  # ⭐ Punto de entrada FastAPI (endpoints)
│   ├── agent.py                 # ⭐ Orquestador del pipeline RAG
│   ├── llm.py                   # ⭐ Integración con Claude (Anthropic)
│   ├── nuclia.py                # ⭐ Cliente de Nuclia (búsqueda)
│   ├── clients.py               # Inicialización de clientes API
│   ├── config.py                # Exportación de configuración
│   ├── schemas.py               # Modelos Pydantic (validación)
│   └── settings.py              # Cargador de variables de entorno
│
├── .env                         # Variables de entorno (NO subir a Git)
├── .env.example                 # Plantilla de configuración
├── .gitignore                   # Archivos excluidos de Git
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

### 📄 Descripción de Archivos Clave

#### `app/main.py` - API FastAPI (Punto de Entrada)
**Propósito:** Define los endpoints HTTP y configura el servidor.

**Funcionalidades:**
- Define endpoint `GET /health` para verificación de estado
- Define endpoint `POST /ask` para consultas inteligentes
- Configura middleware CORS para permitir peticiones desde cualquier origen
- Maneja errores HTTP y respuestas estructuradas

**Imports clave:**
- `FastAPI` - Framework web
- `CORSMiddleware` - Manejo de CORS
- `ask_agent` - Función principal del agente RAG

---

#### `app/agent.py` - Orquestador RAG
**Propósito:** Implementa el pipeline completo de RAG.

**Funciones principales:**

1. **`ask_agent(question, size, max_chunks, use_semantic, min_score)`**
   - Orquesta el flujo completo del pipeline
   - Preprocesa la consulta
   - Realiza búsqueda híbrida en Nuclia
   - Construye contexto con metadata
   - Genera respuesta con Claude
   - Retorna dict con `answer` y `sources`

2. **`extract_sources_info(search_json, max_chunks, score_threshold)`**
   - Extrae información estructurada de los resultados de Nuclia
   - Obtiene títulos, páginas, scores, URLs de cada fuente
   - Filtra por score mínimo
   - Retorna lista de diccionarios con metadata completa

**Flujo de datos:**
```
consulta → preproceso → búsqueda → extracción → contexto → generación → respuesta
```

---

#### `app/llm.py` - Integración con Claude
**Propósito:** Gestiona las llamadas a la API de Anthropic.

**Función principal:**

**`preprocess_query(question)`**
- Optimiza consultas conversacionales para búsqueda
- Extrae palabras clave relevantes
- Transforma preguntas naturales en consultas efectivas
- Ejemplo: *"¿Cómo puedo inscribirme?"* → *"inscripción proceso pasos"*

**Parámetros de llamada a Claude:**
- `model`: claude-sonnet-4-20250514
- `max_tokens`: 100 (para preproceso), 800 (para respuesta)
- `temperature`: 0.0 (preproceso), 0.2 (respuesta)
- `system`: Instrucciones del sistema

---

#### `app/nuclia.py` - Cliente Nuclia
**Propósito:** Interactúa con la API de Nuclia para búsqueda.

**Funciones principales:**

1. **`nuclia_search(query, size, features, filters, min_score, vectorset)`**
   - Realiza búsqueda híbrida en Nuclia
   - Soporta búsqueda por keyword y semántica
   - Permite filtrado por score mínimo
   - Retorna JSON con resultados y metadata

   **Parámetros:**
   - `query`: Texto a buscar
   - `size`: Número de resultados (default: 20)
   - `features`: `['keyword', 'semantic']` para búsqueda híbrida
   - `min_score`: Umbral de relevancia (0.0-1.0)
   - `vectorset`: Modelo de vectores (`multilingual-2024-05-06`)

2. **`build_context(search_json, max_chunks, include_metadata, score_threshold)`**
   - Construye contexto enriquecido desde resultados
   - Incluye títulos de documentos y números de página
   - Filtra por score de relevancia
   - Formatea con separadores para el LLM

---

#### `app/schemas.py` - Validación con Pydantic
**Propósito:** Define modelos de datos con validación automática.

**Modelo `AskBody`:**
```python
class AskBody(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    size: Optional[int] = Field(default=30, ge=1, le=100)
    max_chunks: Optional[int] = Field(default=20, ge=1, le=50)
    use_semantic: Optional[bool] = Field(default=True)
    min_score: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
```

**Validaciones:**
- `query`: Obligatorio, 2-2000 caracteres
- `size`: 1-100 resultados
- `max_chunks`: 1-50 párrafos
- `use_semantic`: Boolean
- `min_score`: 0.0-1.0 (decimal)

---

#### `app/settings.py` - Configuración
**Propósito:** Carga y valida variables de entorno.

**Variables configurables:**
- `NUCLIA_API_BASE`: URL base de Nuclia API
- `KB`: ID del Knowledge Base
- `NUCLIA_TOKEN`: Token de autenticación Nuclia
- `ANTHROPIC_KEY`: API key de Anthropic
- `CLAUDE_MODEL`: Modelo de Claude a usar
- `INSTRUCTIONS`: Instrucciones del sistema para el agente

**Funcionalidad de limpieza:**
- Elimina espacios y comillas
- Proporciona valores por defecto
- Valida formato de variables

---

#### `app/config.py` - Exportación
**Propósito:** Re-exporta configuración para fácil importación.

Permite hacer:
```python
from app.config import CLAUDE_MODEL, KB, HEADERS
```

En lugar de:
```python
from app.settings import settings
CLAUDE_MODEL = settings.CLAUDE_MODEL
```

---

#### `app/clients.py` - Clientes API
**Propósito:** Inicializa clientes de APIs externas.

**Cliente Anthropic:**
```python
from anthropic import Anthropic
client = Anthropic(api_key=ANTHROPIC_KEY)
```

Este cliente se usa en `llm.py` para llamadas a Claude.

---

## 🔧 Requisitos Previos

### Software Necesario

- **Python 3.10 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)

### Cuentas Requeridas

1. **Anthropic Account**
   - Registrarse en: https://console.anthropic.com/
   - Obtener API key de Claude

2. **Nuclia Account**
   - Registrarse en: https://nuclia.com/
   - Crear un Knowledge Base
   - Obtener API token y KB ID

---

## 🚀 Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone <tu-repositorio-url>
cd UVG-Agent-sonnet
```

### Paso 2: Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
# En macOS/Linux:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias instaladas:**
- `fastapi>=0.110` - Framework web
- `uvicorn[standard]>=0.27` - Servidor ASGI
- `requests>=2.31` - Cliente HTTP
- `anthropic>=0.30` - SDK de Anthropic
- `python-dotenv>=1.0` - Gestión de .env
- `pydantic>=2.6` - Validación de datos

---

## ⚙️ Configuración

### Paso 1: Crear Archivo de Variables de Entorno

```bash
cp .env.example .env
```

### Paso 2: Editar el Archivo `.env`

Abre `.env` con tu editor favorito y configura:

```env
# ========================================
# Configuración de Nuclia
# ========================================
NUCLIA_API_BASE=https://aws-us-east-2-1.rag.progress.cloud/api/v1
KB=tu-knowledge-base-id-aqui
NUCLIA_TOKEN=tu-nuclia-token-aqui

# ========================================
# Configuración de Anthropic (Claude)
# ========================================
ANTHROPIC_KEY=sk-ant-api03-tu-api-key-aqui
CLAUDE_MODEL=claude-sonnet-4-20250514

# ========================================
# Instrucciones del Sistema (Opcional)
# ========================================
INSTRUCTIONS=Eres un asesor académico de la UVG Altiplano. Responde usando solo el contexto proporcionado. Si no hay información suficiente, indícalo claramente.
```

### ¿Dónde Obtener las Credenciales?

#### Nuclia:
1. Ve a https://nuclia.cloud/
2. Crea una cuenta o inicia sesión
3. Crea un Knowledge Base
4. Ve a Settings → API Keys
5. Copia el `KB ID` y el `API Token`

#### Anthropic:
1. Ve a https://console.anthropic.com/
2. Crea una cuenta o inicia sesión
3. Ve a API Keys
4. Genera una nueva API key
5. Copia la key (empieza con `sk-ant-`)

---

## 🎯 Uso

### Iniciar el Servidor

```bash
# Activar entorno virtual (si no está activo)
source .venv/bin/activate

# Iniciar servidor con recarga automática
uvicorn app.main:app --reload

# Iniciar en puerto específico
uvicorn app.main:app --reload --port 8000

# Iniciar con logs detallados
uvicorn app.main:app --reload --log-level debug
```

**Salida esperada:**
```
INFO:     Will watch for changes in these directories: ['/path/to/UVG-Agent-sonnet']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Verificar que el Servidor Está Corriendo

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "ok"
}
```

### Acceder a la Documentación Interactiva

Abre tu navegador en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Aquí puedes probar los endpoints directamente desde el navegador.

---

## 📡 API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Descripción:** Verifica que el servicio esté funcionando correctamente.

**Parámetros:** Ninguno

**Respuesta:**
```json
{
  "status": "ok"
}
```

**Ejemplo:**
```bash
curl http://localhost:8000/health
```

---

### 2. Consulta Inteligente (RAG)

**Endpoint:** `POST /ask`

**Descripción:** Realiza una consulta usando el pipeline RAG completo.


#### Respuesta Exitosa (200 OK)

```json
{
  "answer": "Para inscribirte en un curso de la UVG Altiplano, debes seguir estos pasos: 1) Acceder al portal estudiantil...",
  "sources": [
    {
      "id": 1,
      "title": "Guía de Inscripción 2025",
      "text": "El proceso de inscripción se realiza en línea a través del portal estudiantil...",
      "score": 0.892,
      "page": 5,
      "field": "file/document",
      "resource_id": "abc123def456",
      "url": "https://uvg.edu.gt/docs/guia-inscripcion.pdf",
      "url_type": "external",
      "has_url": true
    },
    {
      "id": 2,
      "title": "Manual del Estudiante",
      "text": "Los requisitos para inscripción incluyen: certificado de estudios...",
      "score": 0.765,
      "page": 12,
      "field": "file/document",
      "resource_id": "def456ghi789",
      "url": "https://nuclia.cloud/view/...",
      "url_type": "nuclia",
      "has_url": true
    }
  ],
  "model": "claude-sonnet-4-20250514",
  "nuclia_kb": "5a222e22-1ea8-4aad-9282-bbd025ea6412",
  "params": {
    "size": 30,
    "max_chunks": 10,
    "use_semantic": true,
    "min_score": 0.5
  }
}
```


## 🔍 Ejemplos de Uso

### Ejemplo 1: Consulta Básica con cURL

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuáles son los requisitos para inscribirse en la UVG?"
  }'
```

### Ejemplo 2: Prueba en Postman

#### Configuración en Postman:

1. **Método**: `POST`
2. **URL**: `http://localhost:8000/ask`
3. **Headers**:
   - Key: `Content-Type`
   - Value: `application/json`
4. **Body** (selecciona "raw" y "JSON"):

```json
{
  "query": "¿Cómo puedo contactar con la administración de la UVG?",
  "size": 30,
  "max_chunks": 10,
  "use_semantic": true,
  "min_score": 0.5
}
```

5. **Click en "Send"**

#### Respuesta Esperada:

**Status:** `200 OK`

**Body:**
```json
{
  "answer": "Para contactar con la administración de la UVG Altiplano, puedes usar los siguientes medios...",
  "sources": [
    {
      "id": 1,
      "title": "Directorio de Contacto UVG",
      "text": "Teléfono: 7931-0814, Email: ca.info@uvg.edu.gt",
      "score": 0.95,
      "page": 1,
      "url": "https://altiplano.uvg.edu.gt/contacto",
      "url_type": "external",
      "has_url": true
    }
  ],
  "model": "claude-sonnet-4-20250514"
}
```

---

## 📊 Diagrama de Flujo

### Pipeline RAG Completo

```mermaid
sequenceDiagram
    participant Cliente as Cliente<br/>(Postman/Frontend)
    participant FastAPI as FastAPI<br/>(main.py)
    participant Agent as Agent<br/>(agent.py)
    participant LLM as LLM Module<br/>(llm.py)
    participant Claude as Claude API<br/>(Anthropic)
    participant NucliaClient as Nuclia Client<br/>(nuclia.py)
    participant NucliaAPI as Nuclia API<br/>(Search)

    Note over Cliente,NucliaAPI: 1. Inicio de Consulta
    Cliente->>FastAPI: POST /ask {query, size, max_chunks, use_semantic, min_score}
    FastAPI->>FastAPI: Validar con Pydantic (schemas.py)
    
    Note over FastAPI,Agent: 2. Orquestación
    FastAPI->>Agent: ask_agent(question, **params)
    
    Note over Agent,Claude: 3. Preprocesamiento
    Agent->>LLM: preprocess_query(question)
    LLM->>Claude: messages.create()<br/>(optimizar consulta)
    Claude-->>LLM: consulta_optimizada
    LLM-->>Agent: consulta_optimizada
    
    Note over Agent,NucliaAPI: 4. Búsqueda Híbrida
    Agent->>NucliaClient: nuclia_search(query, size, features=['keyword','semantic'])
    NucliaClient->>NucliaAPI: GET /kb/{KB}/search<br/>?q=consulta&features=keyword,semantic&size=30
    NucliaAPI-->>NucliaClient: JSON {resources, paragraphs, scores}
    NucliaClient-->>Agent: search_results
    
    Note over Agent: 5. Procesamiento de Resultados
    Agent->>Agent: extract_sources_info()<br/>(extraer metadata: títulos, páginas, URLs, scores)
    Agent->>NucliaClient: build_context()<br/>(construir contexto enriquecido)
    NucliaClient-->>Agent: contexto formateado
    
    Note over Agent,Claude: 6. Generación de Respuesta
    Agent->>LLM: messages.create()<br/>(system + contexto + pregunta)
    LLM->>Claude: Generar respuesta basada en contexto
    Claude-->>LLM: answer
    LLM-->>Agent: answer
    
    Note over Agent,Cliente: 7. Respuesta Final
    Agent-->>FastAPI: {answer, sources, search_results}
    FastAPI-->>Cliente: 200 OK<br/>{answer, sources, model, nuclia_kb, params}
```

### Explicación del Flujo

1. **Cliente envía consulta** → FastAPI recibe POST /ask
2. **Validación** → Pydantic valida los parámetros del body
3. **Preprocesamiento** → Claude optimiza la consulta para búsqueda
4. **Búsqueda híbrida** → Nuclia busca con keyword + semántica
5. **Extracción** → Se extrae metadata (títulos, páginas, URLs, scores)
6. **Construcción de contexto** → Se formatea para el LLM
7. **Generación** → Claude genera respuesta basada en contexto
8. **Respuesta** → Cliente recibe answer + sources estructuradas

---
