# KBA Quick Start Guide

## 🚀 Getting Started with Knowledge Base Assistant

This guide will help you get started with the KBA system in just a few minutes.

## Prerequisites

- CGS system running on `http://localhost:8000`
- API access to the `/api/v1/kba/` endpoints
- Sample documents (PDF, MD, TXT, DOCX, or URLs)

## Step 1: Check Available Modes

First, check what workflow modes are available:

```bash
curl -X GET "http://localhost:8000/api/v1/kba/modes"
```

**Response:**
```json
{
  "available_modes": ["brand_kba_4docs", "faq_kba", "documentation_kba", "training_kba"],
  "mode_details": {
    "brand_kba_4docs": {
      "description": "Brand Knowledge Base - 4 Documents",
      "estimated_time": "3-7 minutes",
      "required_sources": {"min": 2, "max": 15},
      "output_count": 4,
      "enabled": true
    }
  }
}
```

## Step 2: Prepare Your Sources

### Option A: Using Content Directly

```json
{
  "client": "my_company",
  "workflow_mode": "brand_kba_4docs",
  "sources": [
    {
      "type": "md",
      "content": "# Company Brand Guide\n\nOur mission is...",
      "filename": "brand_guide.md"
    },
    {
      "type": "txt",
      "content": "Production guidelines:\n1. Research\n2. Draft\n3. Review",
      "filename": "guidelines.txt"
    }
  ],
  "custom_instructions": "Focus on brand consistency",
  "output_format": "default"
}
```

### Option B: Using URLs

```json
{
  "client": "my_company", 
  "workflow_mode": "documentation_kba",
  "sources": [
    {
      "type": "url",
      "url": "https://docs.example.com/api"
    },
    {
      "type": "url", 
      "url": "https://help.example.com/guide"
    }
  ]
}
```

## Step 3: Process Your Content

### Using JSON API

```bash
curl -X POST "http://localhost:8000/api/v1/kba/process" \
  -H "Content-Type: application/json" \
  -d '{
    "client": "my_company",
    "workflow_mode": "brand_kba_4docs",
    "sources": [
      {
        "type": "md",
        "content": "# Brand Guide\n\nOur company values...",
        "filename": "brand.md"
      }
    ]
  }'
```

### Using File Upload

```bash
curl -X POST "http://localhost:8000/api/v1/kba/upload" \
  -F "client=my_company" \
  -F "workflow_mode=brand_kba_4docs" \
  -F "files=@brand_guide.pdf" \
  -F "files=@style_guide.md"
```

**Success Response:**
```json
{
  "success": true,
  "workflow_id": "kba_1234567890",
  "message": "KBA processing completed successfully for my_company",
  "files": [
    "company_profile_brand_voice.md",
    "production_guide.md", 
    "quality_standards.md",
    "voice_examples.md"
  ],
  "download_url": "/api/v1/kba/download/my_company/brand_kba_4docs/kba_1234567890"
}
```

## Step 4: Access Your Results

### List All Exports

```bash
curl -X GET "http://localhost:8000/api/v1/kba/exports"
```

### Get Specific Export Info

```bash
curl -X GET "http://localhost:8000/api/v1/kba/exports/my_company/brand_kba_4docs/kba_1234567890"
```

### Download Individual File

```bash
curl -X GET "http://localhost:8000/api/v1/kba/file/my_company/brand_kba_4docs/kba_1234567890/company_profile_brand_voice.md"
```

### Download Complete Export (ZIP)

```bash
curl -X GET "http://localhost:8000/api/v1/kba/download/my_company/brand_kba_4docs/kba_1234567890" \
  -o my_company_kba.zip
```

## Step 5: Explore Your Knowledge Base

Your generated knowledge base will be organized like this:

```
data/outputs/my_company/brand_kba_4docs/kba_1234567890/v1.0.0/
├── company_profile_brand_voice.md  # Company profile and brand voice
├── production_guide.md             # Content production guidelines  
├── quality_standards.md            # Quality standards and compliance
├── voice_examples.md               # Voice examples and cultural context
├── manifest.json                   # Export metadata and checksums
└── metadata.json                   # Processing metadata
```

## Common Use Cases

### 1. Brand Guidelines from Company Documents

**Input**: Brand guide PDF, style guide, company website
**Mode**: `brand_kba_4docs`
**Output**: 4 structured brand guideline files

### 2. FAQ from Support Documents

**Input**: Support articles, help pages, documentation
**Mode**: `faq_kba`
**Output**: Structured FAQ in markdown and JSON

### 3. Technical Documentation

**Input**: API docs, user guides, technical specs
**Mode**: `documentation_kba`
**Output**: Organized technical documentation

### 4. Training Materials

**Input**: Training manuals, presentations, guides
**Mode**: `training_kba`
**Output**: Structured training curriculum

## Troubleshooting

### Common Issues

**Error: "Invalid source count"**
- Check the min/max source requirements for your workflow mode
- Brand KBA requires 2-15 sources

**Error: "Unsupported file type"**
- Supported formats: PDF, MD, TXT, DOCX, URL
- Check file extensions and content

**Error: "File too large"**
- Maximum file size is 50MB
- Consider splitting large files

**Error: "Parsing failed"**
- Check if PDF is text-based (not scanned images)
- Verify URLs are accessible
- Ensure text files are UTF-8 encoded

### Getting Help

1. Check the logs for detailed error messages
2. Verify your input format matches the examples
3. Test with smaller/simpler files first
4. Check the API documentation for parameter details

## Next Steps

- Explore different workflow modes
- Integrate KBA into your applications
- Set up automated processing workflows
- Customize output formats for your needs

## Python Example

```python
import requests

# Process KBA request
response = requests.post(
    "http://localhost:8000/api/v1/kba/process",
    json={
        "client": "my_company",
        "workflow_mode": "brand_kba_4docs", 
        "sources": [
            {
                "type": "md",
                "content": "# Brand Guide\n\nOur values...",
                "filename": "brand.md"
            }
        ]
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Success! Workflow ID: {result['workflow_id']}")
    print(f"Files: {result['files']}")
else:
    print(f"Error: {response.text}")
```

## JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/api/v1/kba/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    client: 'my_company',
    workflow_mode: 'brand_kba_4docs',
    sources: [
      {
        type: 'md',
        content: '# Brand Guide\n\nOur values...',
        filename: 'brand.md'
      }
    ]
  })
});

const result = await response.json();
console.log('KBA Result:', result);
```
