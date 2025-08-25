# KBA (Knowledge Base Assistant) System

## Overview

The Knowledge Base Assistant (KBA) is a comprehensive system that transforms multiple input sources into structured knowledge base files. It replaces the legacy content generation workflows with a more flexible and powerful ingestion pipeline.

## Key Features

- **Multi-source ingestion**: PDF, URL, Markdown, Text, and DOCX files
- **Intelligent parsing**: Format-specific parsers with metadata extraction
- **Flexible transformation**: Multiple workflow modes for different output types
- **Structured export**: Organized file output with versioning and manifests
- **REST API**: Complete API for integration and automation
- **File management**: Download, preview, and management capabilities

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Sources │───▶│     Parsers     │───▶│  Transformers   │───▶│    Exporters    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
│                      │                      │                      │
│ • PDF files          │ • PDFParser          │ • BrandKBATransformer│ • KBAExporter
│ • Web URLs           │ • URLParser          │ • FAQTransformer     │ • ManifestGenerator
│ • Markdown files     │ • MarkdownParser     │ • DocTransformer     │ • File organization
│ • Text files         │ • TextParser         │ • TrainingTransformer│ • Versioning
│ • DOCX files         │ • DocxParser         │                      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Workflow Modes

### 1. Brand KBA (brand_kba_4docs)
**Purpose**: Create comprehensive brand knowledge base from company documents

**Output Files**:
- `company_profile_brand_voice.md` - Company profile and brand voice guidelines
- `production_guide.md` - Content production guidelines and processes
- `quality_standards.md` - Quality standards and compliance requirements
- `voice_examples.md` - Voice examples and cultural context

**Requirements**: 2-15 sources, 3-7 minutes processing time

### 2. FAQ KBA (faq_kba)
**Purpose**: Generate structured FAQ from various sources

**Output Files**:
- `faq.md` - Formatted FAQ in markdown
- `faq.json` - Structured FAQ data

**Requirements**: 1-10 sources, 2-5 minutes processing time

### 3. Documentation KBA (documentation_kba)
**Purpose**: Create technical documentation knowledge base

**Output Files**:
- `overview.md` - System overview and introduction
- `user_guide.md` - User guide and tutorials
- `api_reference.md` - API reference documentation
- `troubleshooting.md` - Troubleshooting guide and FAQ

**Requirements**: 2-20 sources, 4-8 minutes processing time

### 4. Training KBA (training_kba)
**Purpose**: Build training material knowledge base

**Output Files**:
- `training_overview.md` - Training program overview
- `modules.md` - Training modules and curriculum
- `exercises.md` - Practical exercises and examples
- `assessment.md` - Assessment criteria and tests

**Requirements**: 3-25 sources, 5-10 minutes processing time

## API Endpoints

### Get Available Modes
```http
GET /api/v1/kba/modes
```

### Process KBA Request
```http
POST /api/v1/kba/process
Content-Type: application/json

{
  "client": "company_name",
  "workflow_mode": "brand_kba_4docs",
  "sources": [
    {
      "type": "pdf",
      "content": "base64_encoded_content",
      "filename": "document.pdf"
    },
    {
      "type": "url",
      "url": "https://example.com/page"
    }
  ],
  "custom_instructions": "Focus on brand guidelines",
  "output_format": "default"
}
```

### Upload and Process Files
```http
POST /api/v1/kba/upload
Content-Type: multipart/form-data

client: company_name
workflow_mode: brand_kba_4docs
files: [file1.pdf, file2.md]
```

### List Exports
```http
GET /api/v1/kba/exports?client=company_name
```

### Download Export
```http
GET /api/v1/kba/download/{client}/{workflow_mode}/{workflow_id}
```

### Get Specific File
```http
GET /api/v1/kba/file/{client}/{workflow_mode}/{workflow_id}/{filename}
```

## File Organization

```
data/outputs/
├── {client}/
│   ├── {workflow_mode}/
│   │   ├── {workflow_id}/
│   │   │   ├── v1.0.0/
│   │   │   │   ├── *.md (output files)
│   │   │   │   ├── manifest.json
│   │   │   │   └── metadata.json
```

## Supported Input Formats

| Format | Extension | Parser | Features |
|--------|-----------|--------|----------|
| PDF | .pdf | PDFParser | Text extraction, metadata, multi-page |
| Web URL | http/https | URLParser | Content extraction, readability filtering |
| Markdown | .md | MarkdownParser | Frontmatter support, structure preservation |
| Text | .txt | TextParser | Plain text processing |
| Word | .docx | DocxParser | Text extraction, document properties |

## Migration from Legacy System

### Deprecated Workflows
The following workflows are deprecated and will be removed:
- `enhanced_article` → Use `documentation_kba` or `training_kba`
- `premium_newsletter` → Use `brand_kba_4docs` for brand guidelines
- `siebert_premium_newsletter` → Use `brand_kba_4docs` for brand guidelines

### Migration Steps
1. **Identify current workflow usage**
2. **Map to appropriate KBA workflow mode**
3. **Update API calls to use `/api/v1/kba/` endpoints**
4. **Test with sample data**
5. **Update client integrations**

## Error Handling

The KBA system includes comprehensive error handling:

- **Validation errors**: Invalid input parameters
- **Parsing errors**: Unsupported file formats or corrupted files
- **Transformation errors**: Workflow mode issues
- **Export errors**: File system or permission issues

All errors include detailed messages and suggested solutions.

## Performance Considerations

- **File size limits**: 50MB per file (configurable)
- **Source limits**: 15 sources per workflow (configurable)
- **Timeout settings**: Differentiated by task type
  - Extraction: 5 minutes
  - Transformation: 10 minutes
  - Export: 3 minutes
- **Parallel processing**: Enabled for multiple sources

## Security

- **Input validation**: All inputs are validated and sanitized
- **File type verification**: Magic number checking for uploaded files
- **Path traversal protection**: Secure file handling
- **Rate limiting**: API rate limiting (if configured)

## Monitoring and Logging

- **Comprehensive logging**: All operations are logged with structured data
- **Performance metrics**: Processing times and resource usage
- **Error tracking**: Detailed error reporting and stack traces
- **Audit trail**: Complete workflow execution history

## Future Enhancements

The following features are planned for future releases:

### Visualization KBA (visualization_kba) - Coming Soon
- Interactive dashboards
- Knowledge graphs
- Data visualizations

### Listening KBA (listening_kba) - Coming Soon
- Auto-updating knowledge bases
- Source monitoring
- Change notifications

### Segmented KBA (segmented_kba) - Coming Soon
- Content segmentation
- Interactive cards
- Advanced search and recommendations
