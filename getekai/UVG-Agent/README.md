# UVG-Agent 🎓

Un agente inteligente backend basado en FastAPI que integra el LLM de Anthropic (Claude Sonnet 4) y Nuclia para gestión y recuperación de conocimiento mediante RAG. Este proyecto proporciona una API simple y extensible para interactuar con modelos de lenguaje grandes y bases de conocimiento, con un frontend moderno que muestra resultados de búsqueda con visualización de fuentes similares a Nuclia.

## ✨ Características Principales
- 🚀 **API REST** construida con FastAPI
- 🤖 **Integración con Claude Sonnet 4** (Anthropic) - Modelo más avanzado
- 📚 **Cliente Nuclia** para búsqueda RAG (keyword + semántica)semántica
- 🎯 **Código modular** y extensible


## 📋 Requisitos
- Python 3.10+
- Ver `requirements.txt` para las dependencias de Python

## 🚀 Instalación Rápida
1. **Clonar el repositorio:**
   ```bash
   git clone <repo-url>
   cd UVG-Agent-sonnet
   ```
2. **Crear un entorno virtual (recomendado):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   ```
   Luego edita el archivo `.env` y configura:
   - `NUCLIA_API_BASE`: URL base de la API de Nuclia
   - `KB`: ID de tu Knowledge Base en Nuclia
   - `NUCLIA_TOKEN`: Tu token de autenticación de Nuclia
   - `ANTHROPIC_KEY`: Tu API key de Anthropic
   - `CLAUDE_MODEL`: Modelo de Claude a usar (por defecto: claude-sonnet-4-20250514)
   - `INSTRUCTIONS`: Instrucciones del sistema para el agente (opcional)

## 🎯 Uso

### Opción 1: Script de Inicio Rápido (Recomendado) ⭐
```bash
# Dale permisos (solo la primera vez)
chmod +x start-enhanced.sh

# Ejecuta el script
./start-enhanced.sh
```

Luego abre el frontend:
```bash
open frontend/uvg-agent-enhanced.html
```

### Opción 2: Inicio Manual

**1. Iniciar Backend:**
```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```


### Acceso a la API:
- **API Backend**: `http://localhost:8000`
- **Documentación Interactiva (Swagger)**: `http://localhost:8000/docs`
- **Documentación Alternativa (ReDoc)**: `http://localhost:8000/redoc`

## Endpoints de la API

### 1. Verificación de Salud
**GET** `/health`

Verifica si la API está funcionando.

**Ejemplo de Solicitud:**
```bash
curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "ok"
}
```

---

### 2. Ask Agent (RAG Personalizado)
**POST** `/ask`

Realiza una pregunta usando un pipeline RAG personalizado: preprocesa la consulta con LLM, busca en Nuclia, construye contexto y genera una respuesta con Claude.

**Cuerpo de la Solicitud:**
```json
{
  "query": "¿Cómo puedo inscribirme en un curso?",
  "size": 30,
  "max_chunks": 10,
  "use_semantic": true,
  "min_score": 0.5
}
```

**Parámetros:**
- `query` (string, **requerido**): La pregunta a realizar (2-2000 caracteres)
- `size` (integer, opcional): Número de resultados de búsqueda a recuperar de Nuclia (1-100, por defecto: 30)
- `max_chunks` (integer, opcional): Número máximo de párrafos a incluir en el contexto (1-50, por defecto: 20)
- `use_semantic` (boolean, opcional): Activar búsqueda semántica además de keyword (por defecto: true)
- `min_score` (float, opcional): Score mínimo de relevancia (0.0-1.0, por defecto: 0.0)

**Ejemplo de Solicitud en Postman:**

1. **Método**: `POST`
2. **URL**: `http://localhost:8000/ask`
3. **Headers**:
   - `Content-Type: application/json`
4. **Body** (raw JSON):
```json
{
  "query": "¿Cómo puedo inscribirme en un curso?",
  "size": 30,
  "max_chunks": 10,
  "use_semantic": true,
  "min_score": 0.5
}
```

**Ejemplo con cURL:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cómo puedo inscribirme en un curso?",
    "size": 30,
    "max_chunks": 10,
    "use_semantic": true,
    "min_score": 0.5
  }'
```

**Respuesta Exitosa:**
```json
{
  "answer": "Para inscribirte en un curso en la UVG...",
  "sources": [
    {
      "id": "doc123/chunk1",
      "title": "Guía de Inscripción UVG",
      "text": "El proceso de inscripción...",
      "score": 0.89,
      "page": 5,
      "url": "https://...",
      "url_type": "external",
      "has_url": true
    }
  ],
  "model": "claude-sonnet-4-20250514"
}
```

**Diagrama de Flujo del Pipeline RAG:**

```mermaid
sequenceDiagram
    participant Cliente as Cliente (Frontend/Postman)
    participant API as FastAPI /ask
    participant LLM as Claude (Anthropic)
    participant Nuclia as Nuclia Search API

    Cliente->>API: POST /ask { query, size, max_chunks }
    
    Note over API: 1. Preprocesar consulta
    API->>LLM: preprocess_query(query)
    LLM-->>API: consulta_optimizada
    
    Note over API: 2. Búsqueda en Nuclia
    API->>Nuclia: GET /kb/{KB}/search?q=consulta&features=[keyword,semantic]
    Nuclia-->>API: JSON { resources, paragraphs, scores }
    
    Note over API: 3. Extraer fuentes
    API->>API: extract_sources_info(max_chunks, min_score)
    
    Note over API: 4. Construir contexto
    API->>API: build_context(sources)
    
    Note over API: 5. Generar respuesta
    API->>LLM: messages.create(system + context + query)
    LLM-->>API: answer
    
    API-->>Cliente: 200 { answer, sources, model }
```

---

## Estructura del Proyecto

### Archivos Principales del Backend

- **`app/main.py`** - Punto de entrada de la aplicación FastAPI. Define los endpoints HTTP (`/health`, `/ask`) y configura el middleware CORS.

- **`app/agent.py`** - Lógica de orquestación del agente RAG. Implementa el pipeline completo: preprocesamiento de consultas, búsqueda en Nuclia, extracción de fuentes con URLs y metadata, construcción de contexto, y generación de respuestas con Claude.

- **`app/llm.py`** - Módulo de integración con LLM. Contiene la función `preprocess_query()` que usa Claude para optimizar las preguntas de usuario en mejores consultas de búsqueda.

- **`app/nuclia.py`** - Cliente de la API de Nuclia. Proporciona funciones para búsqueda híbrida (`nuclia_search`) con soporte de keyword + semantic search, y construcción de contexto con metadata completa.

- **`app/clients.py`** - Inicialización de clientes API. Crea la instancia del cliente Anthropic usado en toda la aplicación.

- **`app/schemas.py`** - Modelos Pydantic para validación de solicitudes/respuestas. Define el esquema `AskBody` con validación de campos y parámetros de configuración (query, size, max_chunks, use_semantic, min_score).

- **`app/settings.py`** - Cargador de configuración y variables de entorno. Usa `python-dotenv` para cargar claves API, nombres de modelos e instrucciones del sistema desde el archivo `.env`.

- **`app/config.py`** - Exportaciones de configuración. Re-exporta configuraciones como constantes a nivel de módulo para importación fácil.

### Configuración

- **`.env.example`** - Plantilla de variables de entorno.
- **`.gitignore`** - Archivos y directorios excluidos del control de versiones.
- **`requirements.txt`** - Dependencias Python del proyecto.
- **`start-enhanced.sh`** - Script de inicio rápido del servidor.

---

