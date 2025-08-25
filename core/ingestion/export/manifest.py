"""
Manifest generator for KBA exports.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class ManifestGenerator:
    """
    Generator for KBA export manifests.
    
    Creates comprehensive manifest files that describe the exported
    knowledge base content, including metadata, file information,
    and provenance data.
    """
    
    def __init__(self):
        """Initialize the manifest generator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate_manifest(self,
                         transformed_content: 'TransformedContent',
                         context: Dict[str, Any],
                         saved_files: List[Dict[str, Any]],
                         output_directory: str) -> Dict[str, Any]:
        """
        Generate a comprehensive manifest for the exported content.
        
        Args:
            transformed_content: TransformedContent object
            context: Workflow context
            saved_files: List of saved file information
            output_directory: Output directory path
            
        Returns:
            Manifest data dictionary
        """
        self.logger.info("📋 Generating export manifest")
        
        manifest = {
            'manifest_version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'export_info': self._create_export_info(context, output_directory),
            'workflow_info': self._create_workflow_info(context),
            'content_info': self._create_content_info(transformed_content),
            'files': self._create_file_info(saved_files),
            'provenance': self._create_provenance_info(context),
            'checksums': self._create_checksums(saved_files),
            'statistics': self._create_statistics(transformed_content, saved_files)
        }
        
        self.logger.info("✅ Manifest generated successfully")
        return manifest
    
    def _create_export_info(self, context: Dict[str, Any], output_directory: str) -> Dict[str, Any]:
        """Create export information section."""
        return {
            'export_id': context.get('workflow_id'),
            'output_directory': output_directory,
            'version': 'v1.0.0',
            'format_version': '1.0.0',
            'exporter': 'KBAExporter',
            'export_timestamp': datetime.now().isoformat()
        }
    
    def _create_workflow_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow information section."""
        return {
            'workflow_type': 'kba_ingestion',
            'workflow_mode': context.get('workflow_mode'),
            'workflow_id': context.get('workflow_id'),
            'client': context.get('client'),
            'custom_instructions': context.get('custom_instructions'),
            'output_format': context.get('output_format', 'default'),
            'sources_count': context.get('sources_count', 0),
            'execution_timestamp': context.get('timestamp')
        }
    
    def _create_content_info(self, transformed_content: 'TransformedContent') -> Dict[str, Any]:
        """Create content information section."""
        return {
            'summary': transformed_content.summary,
            'total_word_count': transformed_content.word_count,
            'file_count': len(transformed_content.files),
            'metadata': transformed_content.metadata,
            'transformer': transformed_content.metadata.get('transformer'),
            'key_themes': transformed_content.metadata.get('key_themes', [])
        }
    
    def _create_file_info(self, saved_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create file information section."""
        file_info = []
        
        for file_data in saved_files:
            file_info.append({
                'filename': file_data['filename'],
                'path': file_data['path'],
                'size_bytes': file_data['size_bytes'],
                'word_count': file_data['word_count'],
                'line_count': file_data['line_count'],
                'format': self._detect_file_format(file_data['filename']),
                'created_at': file_data['created_at'],
                'modified_at': file_data['modified_at']
            })
        
        return file_info
    
    def _create_provenance_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create provenance information section."""
        sources = context.get('sources', [])
        
        source_info = []
        for i, source in enumerate(sources):
            source_data = {
                'index': i,
                'type': source.get('type'),
                'origin': source.get('url') or source.get('filename') or f"source_{i}"
            }
            
            if 'filename' in source:
                source_data['filename'] = source['filename']
            if 'file_size' in source:
                source_data['file_size'] = source['file_size']
            
            source_info.append(source_data)
        
        return {
            'sources': source_info,
            'source_count': len(sources),
            'source_types': list(set(s.get('type') for s in sources if s.get('type'))),
            'processing_pipeline': [
                'extraction',
                'enrichment', 
                'transformation',
                'assembly',
                'export'
            ]
        }
    
    def _create_checksums(self, saved_files: List[Dict[str, Any]]) -> Dict[str, str]:
        """Create file checksums for integrity verification."""
        checksums = {}
        
        for file_data in saved_files:
            try:
                file_path = file_data['path']
                with open(file_path, 'rb') as f:
                    content = f.read()
                    checksum = hashlib.sha256(content).hexdigest()
                    checksums[file_data['filename']] = checksum
            except Exception as e:
                self.logger.warning(f"Failed to generate checksum for {file_data['filename']}: {e}")
                checksums[file_data['filename']] = 'error'
        
        return checksums
    
    def _create_statistics(self, 
                          transformed_content: 'TransformedContent',
                          saved_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create statistics section."""
        total_size = sum(f['size_bytes'] for f in saved_files)
        total_words = sum(f['word_count'] for f in saved_files)
        total_lines = sum(f['line_count'] for f in saved_files)
        
        file_types = {}
        for file_data in saved_files:
            file_format = self._detect_file_format(file_data['filename'])
            file_types[file_format] = file_types.get(file_format, 0) + 1
        
        return {
            'total_files': len(saved_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_word_count': total_words,
            'total_line_count': total_lines,
            'average_file_size': round(total_size / len(saved_files)) if saved_files else 0,
            'average_word_count': round(total_words / len(saved_files)) if saved_files else 0,
            'file_types': file_types,
            'largest_file': max(saved_files, key=lambda x: x['size_bytes'])['filename'] if saved_files else None,
            'smallest_file': min(saved_files, key=lambda x: x['size_bytes'])['filename'] if saved_files else None
        }
    
    def _detect_file_format(self, filename: str) -> str:
        """Detect file format from filename."""
        if filename.endswith('.md'):
            return 'markdown'
        elif filename.endswith('.json'):
            return 'json'
        elif filename.endswith('.html'):
            return 'html'
        elif filename.endswith('.txt'):
            return 'text'
        else:
            return 'unknown'
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> bool:
        """
        Validate manifest structure and content.
        
        Args:
            manifest: Manifest data to validate
            
        Returns:
            True if manifest is valid
        """
        required_sections = [
            'manifest_version',
            'created_at',
            'export_info',
            'workflow_info',
            'content_info',
            'files',
            'provenance',
            'checksums',
            'statistics'
        ]
        
        for section in required_sections:
            if section not in manifest:
                self.logger.error(f"Missing required manifest section: {section}")
                return False
        
        # Validate file count consistency
        files_count = len(manifest['files'])
        stats_count = manifest['statistics']['total_files']
        
        if files_count != stats_count:
            self.logger.error(f"File count mismatch: files={files_count}, stats={stats_count}")
            return False
        
        self.logger.info("✅ Manifest validation passed")
        return True
