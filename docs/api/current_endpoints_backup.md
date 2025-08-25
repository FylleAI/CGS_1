# Current API Endpoints - Pre-KBA Refactor Backup

This document captures the current API endpoints before the KBA refactoring for backward compatibility reference.

## API Structure

**Base URL**: `http://localhost:8000`
**API Version**: v1
**Documentation**: `/docs` (Swagger UI)

## Current Endpoints

### 1. Content Generation (`/api/v1/content`)

#### POST `/api/v1/content/generate`
- **Purpose**: Generate content using AI workflows
- **Current Workflow Types**:
  - `enhanced_article` - Enhanced Article Handler
  - `premium_newsletter` - Premium Newsletter Handler  
  - `siebert_premium_newsletter` - Siebert Premium Newsletter Handler

**Request Model**:
```json
{
  "topic": "string",
  "content_type": "article",
  "content_format": "markdown", 
  "client_profile": "string",
  "workflow_type": "string",
  "provider": "openai",
  "model": "gpt-4o",
  "temperature": 0.7,
  "target_word_count": 1000,
  "target": "string",
  "context": "string",
  "tone": "professional",
  "include_statistics": true,
  "include_examples": true,
  "newsletter_topic": "string",
  "edition_number": 1,
  "featured_sections": ["string"],
  "custom_instructions": "string"
}
```

### 2. Workflows (`/api/v1/workflows`)

#### GET `/api/v1/workflows`
- **Purpose**: List available workflows
- **Returns**: Array of workflow definitions

#### POST `/api/v1/workflows/execute`
- **Purpose**: Execute a specific workflow
- **Request**:
```json
{
  "workflow_id": "string",
  "parameters": {}
}
```

### 3. Agents (`/api/v1/agents`)

#### GET `/api/v1/agents`
- **Purpose**: List available AI agents
- **Returns**: Array of agent configurations

#### GET `/api/v1/agents/{agent_id}`
- **Purpose**: Get specific agent details

### 4. System (`/api/v1/system`)

#### GET `/api/v1/system/status`
- **Purpose**: Get system status and health

#### GET `/api/v1/system/config`
- **Purpose**: Get system configuration

### 5. Knowledge Base (`/api/v1`)

#### Existing knowledge base endpoints (to be expanded for KBA)

### 6. Logging

#### Various logging endpoints for system monitoring

### 7. Health & Root

#### GET `/health`
- **Purpose**: Health check endpoint
- **Returns**: `{"status": "healthy", "service": "cgsref-api", "version": "1.0.0"}`

#### GET `/`
- **Purpose**: Root endpoint with API information

## Current Workflow Registry

The system currently registers these workflow handlers:
- `enhanced_article` → `EnhancedArticleHandler`
- `premium_newsletter` → `PremiumNewsletterHandler`
- `siebert_premium_newsletter` → `SiebertPremiumNewsletterHandler`

## Dependencies and Infrastructure

### Core Dependencies
- FastAPI for REST API
- Pydantic for data validation
- CrewAI for agent orchestration
- LangChain for LLM integration
- Multiple LLM providers (OpenAI, Anthropic, etc.)

### Current Architecture
- Clean Architecture with Domain/Application/Infrastructure layers
- Repository pattern for data access
- Factory pattern for LLM providers
- Workflow registry for dynamic execution

## Notes for KBA Refactoring

1. **Preserve Backward Compatibility**: Existing endpoints should continue working
2. **Workflow Registry**: Will need to add KBA workflow handlers
3. **File Management**: New endpoints needed for file upload/download/preview
4. **Multi-source Input**: Current system handles single topic input, KBA needs multiple sources
5. **Output Structure**: Current system returns single content, KBA needs structured file sets

## New KBA Endpoints (Added)

### 8. Knowledge Base Assistant (`/api/v1/kba`)

#### GET `/api/v1/kba/modes`
- **Purpose**: Get available KBA workflow modes
- **Returns**: Available modes and their configurations

#### POST `/api/v1/kba/process`
- **Purpose**: Process sources through KBA workflow
- **Request**:
```json
{
  "client": "string",
  "workflow_mode": "brand_kba_4docs",
  "sources": [
    {
      "type": "pdf|url|md|txt|docx",
      "content": "string",
      "url": "string",
      "filename": "string"
    }
  ],
  "custom_instructions": "string",
  "output_format": "default"
}
```

#### POST `/api/v1/kba/upload`
- **Purpose**: Upload files and process through KBA workflow
- **Content-Type**: multipart/form-data

#### GET `/api/v1/kba/exports`
- **Purpose**: List KBA exports
- **Query**: `?client=string` (optional filter)

#### GET `/api/v1/kba/exports/{client}/{workflow_mode}/{workflow_id}`
- **Purpose**: Get specific export information

#### GET `/api/v1/kba/download/{client}/{workflow_mode}/{workflow_id}`
- **Purpose**: Download complete export as ZIP file

#### GET `/api/v1/kba/file/{client}/{workflow_mode}/{workflow_id}/{filename}`
- **Purpose**: Download specific file from export

## Migration Strategy

- Keep existing endpoints functional
- Add new KBA-specific endpoints under `/api/v1/kba`
- Gradually deprecate old content generation workflows
- Maintain API versioning for smooth transition
