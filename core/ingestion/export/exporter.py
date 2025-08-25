"""
KBA file exporter for saving transformed content to disk.
"""

import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .manifest import ManifestGenerator

logger = logging.getLogger(__name__)


class KBAExporter:
    """
    Exporter for saving KBA transformed content to disk.
    
    Handles file organization, versioning, and manifest generation
    for knowledge base outputs.
    """
    
    def __init__(self, base_output_path: str = "data/outputs"):
        """
        Initialize the exporter.
        
        Args:
            base_output_path: Base directory for all outputs
        """
        self.base_output_path = Path(base_output_path)
        self.manifest_generator = ManifestGenerator()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def export(self, 
                    transformed_content: 'TransformedContent',
                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export transformed content to disk.
        
        Args:
            transformed_content: TransformedContent object with files to save
            context: Workflow context with export information
            
        Returns:
            Export result with file paths and manifest information
            
        Raises:
            ValueError: If export fails
        """
        self.logger.info("📁 Starting KBA content export")
        
        try:
            # Create output directory structure
            output_dir = self._create_output_directory(context)
            
            # Save all files
            saved_files = await self._save_files(
                transformed_content.files, 
                output_dir
            )
            
            # Generate and save manifest
            manifest_data = await self._generate_manifest(
                transformed_content,
                context,
                saved_files,
                output_dir
            )
            
            # Save metadata
            metadata_file = await self._save_metadata(
                transformed_content.metadata,
                output_dir
            )
            
            # Create export summary
            export_result = {
                'success': True,
                'output_directory': str(output_dir),
                'files_saved': saved_files,
                'manifest_file': str(manifest_data['manifest_file']),
                'metadata_file': str(metadata_file),
                'total_files': len(saved_files),
                'export_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Export completed: {len(saved_files)} files saved to {output_dir}")
            return export_result
            
        except Exception as e:
            self.logger.error(f"❌ Export failed: {str(e)}")
            raise ValueError(f"Failed to export KBA content: {str(e)}")
    
    def _create_output_directory(self, context: Dict[str, Any]) -> Path:
        """
        Create the output directory structure.
        
        Args:
            context: Workflow context
            
        Returns:
            Path to the output directory
        """
        client = context.get('client', 'unknown_client')
        workflow_mode = context.get('workflow_mode', 'unknown_mode')
        workflow_id = context.get('workflow_id', f"kba_{int(time.time())}")
        version = "v1.0.0"  # Could be made configurable
        
        # Create directory structure: base/client/workflow_mode/workflow_id/version
        output_dir = self.base_output_path / client / workflow_mode / workflow_id / version
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"📁 Created output directory: {output_dir}")
        return output_dir
    
    async def _save_files(self, 
                         files: Dict[str, str], 
                         output_dir: Path) -> List[Dict[str, Any]]:
        """
        Save all files to the output directory.
        
        Args:
            files: Dictionary of filename -> content
            output_dir: Output directory path
            
        Returns:
            List of saved file information
        """
        saved_files = []
        
        for filename, content in files.items():
            file_path = output_dir / filename
            
            # Save file
            file_path.write_text(content, encoding='utf-8')
            
            # Get file stats
            file_stats = file_path.stat()
            
            file_info = {
                'filename': filename,
                'path': str(file_path),
                'size_bytes': file_stats.st_size,
                'word_count': len(content.split()),
                'line_count': len(content.split('\n')),
                'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            }
            
            saved_files.append(file_info)
            self.logger.debug(f"💾 Saved file: {filename} ({file_stats.st_size} bytes)")
        
        return saved_files
    
    async def _generate_manifest(self,
                                transformed_content: 'TransformedContent',
                                context: Dict[str, Any],
                                saved_files: List[Dict[str, Any]],
                                output_dir: Path) -> Dict[str, Any]:
        """
        Generate and save manifest file.
        
        Args:
            transformed_content: TransformedContent object
            context: Workflow context
            saved_files: List of saved file information
            output_dir: Output directory
            
        Returns:
            Manifest data and file path
        """
        manifest_data = self.manifest_generator.generate_manifest(
            transformed_content=transformed_content,
            context=context,
            saved_files=saved_files,
            output_directory=str(output_dir)
        )
        
        # Save manifest file
        manifest_file = output_dir / "manifest.json"
        manifest_file.write_text(
            json.dumps(manifest_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        self.logger.info(f"📋 Generated manifest: {manifest_file}")
        
        return {
            'manifest_data': manifest_data,
            'manifest_file': manifest_file
        }
    
    async def _save_metadata(self, 
                            metadata: Dict[str, Any], 
                            output_dir: Path) -> Path:
        """
        Save metadata file.
        
        Args:
            metadata: Metadata dictionary
            output_dir: Output directory
            
        Returns:
            Path to saved metadata file
        """
        metadata_file = output_dir / "metadata.json"
        metadata_file.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        self.logger.debug(f"📊 Saved metadata: {metadata_file}")
        return metadata_file
    
    def list_exports(self, client: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List existing exports.
        
        Args:
            client: Optional client filter
            
        Returns:
            List of export information
        """
        exports = []
        
        if client:
            client_dirs = [self.base_output_path / client] if (self.base_output_path / client).exists() else []
        else:
            client_dirs = [d for d in self.base_output_path.iterdir() if d.is_dir()]
        
        for client_dir in client_dirs:
            for workflow_dir in client_dir.iterdir():
                if not workflow_dir.is_dir():
                    continue
                
                for workflow_id_dir in workflow_dir.iterdir():
                    if not workflow_id_dir.is_dir():
                        continue
                    
                    for version_dir in workflow_id_dir.iterdir():
                        if not version_dir.is_dir():
                            continue
                        
                        manifest_file = version_dir / "manifest.json"
                        if manifest_file.exists():
                            try:
                                manifest_data = json.loads(manifest_file.read_text())
                                exports.append({
                                    'client': client_dir.name,
                                    'workflow_mode': workflow_dir.name,
                                    'workflow_id': workflow_id_dir.name,
                                    'version': version_dir.name,
                                    'path': str(version_dir),
                                    'created_at': manifest_data.get('created_at'),
                                    'file_count': len(manifest_data.get('files', [])),
                                    'manifest': manifest_data
                                })
                            except Exception as e:
                                self.logger.warning(f"Failed to read manifest {manifest_file}: {e}")
        
        return sorted(exports, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_export(self, client: str, workflow_mode: str, workflow_id: str, version: str = "v1.0.0") -> Optional[Dict[str, Any]]:
        """
        Get specific export information.
        
        Args:
            client: Client name
            workflow_mode: Workflow mode
            workflow_id: Workflow ID
            version: Version (default: v1.0.0)
            
        Returns:
            Export information or None if not found
        """
        export_dir = self.base_output_path / client / workflow_mode / workflow_id / version
        manifest_file = export_dir / "manifest.json"
        
        if not manifest_file.exists():
            return None
        
        try:
            manifest_data = json.loads(manifest_file.read_text())
            return {
                'client': client,
                'workflow_mode': workflow_mode,
                'workflow_id': workflow_id,
                'version': version,
                'path': str(export_dir),
                'manifest': manifest_data,
                'files': list(export_dir.glob("*.md")) + list(export_dir.glob("*.json"))
            }
        except Exception as e:
            self.logger.error(f"Failed to read export {export_dir}: {e}")
            return None
