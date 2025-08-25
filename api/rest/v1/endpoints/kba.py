"""
KBA (Knowledge Base Assistant) API endpoints.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import tempfile
import base64
from pathlib import Path

from core.ingestion.export import KBAExporter
from core.ingestion.modes import get_workflow_mode, list_available_modes, validate_sources_for_mode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kba", tags=["KBA"])


# Request/Response Models
class KBASource(BaseModel):
    """Source input for KBA processing."""
    type: str = Field(..., description="Source type: pdf, url, md, txt, docx")
    content: Optional[str] = Field(None, description="Content or base64 encoded file")
    url: Optional[str] = Field(None, description="URL for web content")
    filename: Optional[str] = Field(None, description="Original filename")


class KBARequest(BaseModel):
    """Request model for KBA processing."""
    client: str = Field(..., description="Client name", min_length=2)
    workflow_mode: str = Field(..., description="KBA workflow mode")
    sources: List[KBASource] = Field(..., description="List of sources to process", min_items=1, max_items=15)
    custom_instructions: Optional[str] = Field(None, description="Additional processing instructions")
    output_format: str = Field("default", description="Output format: default, rag_compatible")


class KBAResponse(BaseModel):
    """Response model for KBA processing."""
    success: bool
    workflow_id: str
    message: str
    export_info: Optional[Dict[str, Any]] = None
    files: Optional[List[str]] = None
    download_url: Optional[str] = None


class KBAListResponse(BaseModel):
    """Response model for listing KBA exports."""
    exports: List[Dict[str, Any]]
    total: int


# API Endpoints
@router.get("/modes", response_model=Dict[str, Any])
async def get_available_modes():
    """
    Get available KBA workflow modes.
    
    Returns:
        Dictionary with available modes and their configurations
    """
    try:
        from core.ingestion.modes import get_mode_info
        
        available_modes = list_available_modes()
        mode_info = get_mode_info()
        
        return {
            "available_modes": available_modes,
            "mode_details": {mode: mode_info[mode] for mode in available_modes}
        }
    except Exception as e:
        logger.error(f"Failed to get KBA modes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get KBA modes: {str(e)}")


@router.post("/process", response_model=KBAResponse)
async def process_kba(request: KBARequest):
    """
    Process sources through KBA workflow.
    
    Args:
        request: KBA processing request
        
    Returns:
        KBA processing response with export information
    """
    try:
        logger.info(f"🔄 Starting KBA processing: {request.workflow_mode} for {request.client}")
        
        # Validate workflow mode
        workflow_mode = get_workflow_mode(request.workflow_mode)
        
        # Validate source count
        if not validate_sources_for_mode(request.workflow_mode, len(request.sources)):
            mode_sources = workflow_mode.required_sources
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source count for {request.workflow_mode}. "
                       f"Required: {mode_sources['min']}-{mode_sources['max']}, "
                       f"provided: {len(request.sources)}"
            )
        
        # Convert sources to workflow format
        sources = []
        for source in request.sources:
            source_dict = {
                "type": source.type,
                "filename": source.filename
            }
            
            if source.url:
                source_dict["url"] = source.url
            if source.content:
                source_dict["content"] = source.content
                
            sources.append(source_dict)
        
        # Create workflow context
        from core.infrastructure.workflows.registry import workflow_registry
        
        context = {
            "client": request.client,
            "workflow_mode": request.workflow_mode,
            "sources": sources,
            "custom_instructions": request.custom_instructions,
            "output_format": request.output_format
        }
        
        # Execute KBA workflow
        handler = workflow_registry.get_handler('kba_ingestion')
        result = await handler.execute(context)
        
        # Extract export information from result
        export_info = result.get('workflow_summary', {})
        files = result.get('exported_files', [])
        
        response = KBAResponse(
            success=True,
            workflow_id=export_info.get('workflow_id', 'unknown'),
            message=f"KBA processing completed successfully for {request.client}",
            export_info=export_info,
            files=files,
            download_url=f"/api/v1/kba/download/{request.client}/{request.workflow_mode}/{export_info.get('workflow_id')}"
        )
        
        logger.info(f"✅ KBA processing completed: {response.workflow_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ KBA processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"KBA processing failed: {str(e)}")


@router.post("/upload", response_model=KBAResponse)
async def upload_and_process(
    client: str = Form(...),
    workflow_mode: str = Form(...),
    provider: str = Form("openai"),
    model: str = Form("gpt-4o"),
    temperature: float = Form(0.7),
    custom_instructions: Optional[str] = Form(None),
    output_format: str = Form("default"),
    files: List[UploadFile] = File(...)
):
    """
    Upload files and process through KBA workflow.
    
    Args:
        client: Client name
        workflow_mode: KBA workflow mode
        custom_instructions: Optional processing instructions
        output_format: Output format
        files: List of uploaded files
        
    Returns:
        KBA processing response
    """
    try:
        logger.info(f"📁 Processing {len(files)} uploaded files for {client}")
        
        # Convert uploaded files to sources
        sources = []
        for file in files:
            # Read file content
            content = await file.read()
            
            # Detect file type from extension
            file_ext = Path(file.filename).suffix.lower().lstrip('.')
            if file_ext == 'pdf':
                # Encode PDF as base64
                content_str = base64.b64encode(content).decode('utf-8')
            else:
                # Decode text files
                content_str = content.decode('utf-8')
            
            source = KBASource(
                type=file_ext,
                content=content_str,
                filename=file.filename
            )
            sources.append(source)
        
        # Create request and process
        request = KBARequest(
            client=client,
            workflow_mode=workflow_mode,
            sources=sources,
            custom_instructions=custom_instructions,
            output_format=output_format
        )

        # Convert to dict and ensure sources are proper dictionaries
        request_dict = request.dict()

        # Convert sources to proper dictionaries
        converted_sources = []
        for source in request_dict['sources']:
            if hasattr(source, 'dict'):
                converted_sources.append(source.dict())
            elif isinstance(source, dict):
                converted_sources.append(source)
            else:
                # Convert object to dict manually
                converted_sources.append({
                    'type': getattr(source, 'type', 'unknown'),
                    'content': getattr(source, 'content', ''),
                    'filename': getattr(source, 'filename', ''),
                    'url': getattr(source, 'url', None)
                })

        request_dict['sources'] = converted_sources
        request_dict['provider'] = provider
        request_dict['model'] = model
        request_dict['temperature'] = temperature
        
        return await _process_kba_request_dict(request_dict)
        
    except Exception as e:
        logger.error(f"❌ File upload and processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@router.get("/exports", response_model=KBAListResponse)
async def list_exports(client: Optional[str] = None):
    """
    List KBA exports.
    
    Args:
        client: Optional client filter
        
    Returns:
        List of KBA exports
    """
    try:
        exporter = KBAExporter()
        exports = exporter.list_exports(client=client)
        
        return KBAListResponse(
            exports=exports,
            total=len(exports)
        )
        
    except Exception as e:
        logger.error(f"Failed to list exports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list exports: {str(e)}")


@router.get("/exports/{client}/{workflow_mode}/{workflow_id}")
async def get_export(client: str, workflow_mode: str, workflow_id: str, version: str = "v1.0.0"):
    """
    Get specific KBA export information.
    
    Args:
        client: Client name
        workflow_mode: Workflow mode
        workflow_id: Workflow ID
        version: Version (default: v1.0.0)
        
    Returns:
        Export information
    """
    try:
        exporter = KBAExporter()
        export_info = exporter.get_export(client, workflow_mode, workflow_id, version)
        
        if not export_info:
            raise HTTPException(status_code=404, detail="Export not found")
        
        return export_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get export: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get export: {str(e)}")


@router.get("/download/{client}/{workflow_mode}/{workflow_id}")
async def download_export(client: str, workflow_mode: str, workflow_id: str, version: str = "v1.0.0"):
    """
    Download KBA export as ZIP file.
    
    Args:
        client: Client name
        workflow_mode: Workflow mode
        workflow_id: Workflow ID
        version: Version (default: v1.0.0)
        
    Returns:
        ZIP file with all export files
    """
    try:
        exporter = KBAExporter()
        export_info = exporter.get_export(client, workflow_mode, workflow_id, version)
        
        if not export_info:
            raise HTTPException(status_code=404, detail="Export not found")
        
        # Create ZIP file
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            export_path = Path(export_info['path'])
            
            # Add all files to ZIP
            for file_path in export_path.glob("*"):
                if file_path.is_file():
                    zip_file.write(file_path, file_path.name)
        
        zip_buffer.seek(0)
        
        # Save to temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(zip_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            path=tmp_file_path,
            filename=f"{client}_{workflow_mode}_{workflow_id}.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download export: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download export: {str(e)}")


@router.get("/file/{client}/{workflow_mode}/{workflow_id}/{filename}")
async def get_file(client: str, workflow_mode: str, workflow_id: str, filename: str, version: str = "v1.0.0"):
    """
    Get specific file from KBA export.

    Args:
        client: Client name
        workflow_mode: Workflow mode
        workflow_id: Workflow ID
        filename: File name
        version: Version (default: v1.0.0)

    Returns:
        File content
    """
    try:
        exporter = KBAExporter()
        export_info = exporter.get_export(client, workflow_mode, workflow_id, version)

        if not export_info:
            raise HTTPException(status_code=404, detail="Export not found")

        file_path = Path(export_info['path']) / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Determine media type
        if filename.endswith('.md'):
            media_type = "text/markdown"
        elif filename.endswith('.json'):
            media_type = "application/json"
        elif filename.endswith('.html'):
            media_type = "text/html"
        else:
            media_type = "text/plain"

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file: {str(e)}")


@router.get("/preview/{client}/{workflow_mode}/{workflow_id}/{filename}")
async def preview_file(client: str, workflow_mode: str, workflow_id: str, filename: str, version: str = "v1.0.0"):
    """
    Get file content preview for display in UI.

    Args:
        client: Client name
        workflow_mode: Workflow mode
        workflow_id: Workflow ID
        filename: File name
        version: Version (default: v1.0.0)

    Returns:
        File content with metadata for preview
    """
    try:
        exporter = KBAExporter()
        export_info = exporter.get_export(client, workflow_mode, workflow_id, version)

        if not export_info:
            raise HTTPException(status_code=404, detail="Export not found")

        file_path = Path(export_info['path']) / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Read file content
        content = file_path.read_text(encoding='utf-8')

        # Get file stats
        file_stats = file_path.stat()

        # Determine file type and format content
        file_type = "text"
        if filename.endswith('.md'):
            file_type = "markdown"
        elif filename.endswith('.json'):
            file_type = "json"
        elif filename.endswith('.html'):
            file_type = "html"

        # Create preview response
        preview_data = {
            "filename": filename,
            "file_type": file_type,
            "content": content,
            "size_bytes": file_stats.st_size,
            "word_count": len(content.split()),
            "line_count": len(content.split('\n')),
            "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "download_url": f"/api/v1/kba/file/{client}/{workflow_mode}/{workflow_id}/{filename}?version={version}"
        }

        return preview_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file: {str(e)}")


async def _process_kba_request_dict(request_dict: dict) -> KBAResponse:
    """Process KBA request with model parameters."""
    try:
        # Extract model parameters
        provider = request_dict.pop('provider', 'openai')
        model = request_dict.pop('model', 'gpt-4o')
        temperature = request_dict.pop('temperature', 0.7)

        # Create KBA request
        request = KBARequest(**request_dict)

        # Add model parameters to the workflow context
        workflow_context = {
            'client': request.client,
            'workflow_mode': request.workflow_mode,
            'sources': request.sources,
            'custom_instructions': request.custom_instructions,
            'output_format': request.output_format,
            'provider': provider,
            'model': model,
            'temperature': temperature
        }

        # Process KBA workflow
        logger.info(f"🔄 Starting KBA processing: {request.workflow_mode} for {request.client} with {provider}/{model}")

        # Get workflow handler
        from core.infrastructure.workflows.registry import workflow_registry
        handler = workflow_registry.get_handler('kba_ingestion')

        # Execute workflow
        result = await handler.execute(workflow_context)

        # Create response
        response = KBAResponse(
            success=True,
            workflow_id=result.get('workflow_id'),
            message=f"KBA processing completed successfully for {request.client}",
            export_info=result.get('workflow_summary', {}),
            files=result.get('exported_files', []),
            download_url=f"/api/v1/kba/download/{request.client}/{request.workflow_mode}/{result.get('workflow_id')}"
        )

        logger.info(f"✅ KBA processing completed: {result.get('workflow_id')}")
        return response

    except Exception as e:
        logger.error(f"❌ KBA processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"KBA processing failed: {str(e)}")
