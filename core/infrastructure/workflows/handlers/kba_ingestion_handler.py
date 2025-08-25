"""
KBA (Knowledge Base Assistant) Ingestion workflow handler.

This handler processes multiple sources (PDF, URL, MD, TXT, DOCX) and transforms them
into structured knowledge base files.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

# Import KBA components
from core.ingestion.parsers import ParserFactory
from core.ingestion.transformers import TransformerFactory
from core.ingestion.export import KBAExporter

# Import for processing simulation
import asyncio

logger = logging.getLogger(__name__)


@register_workflow('kba_ingestion')
class KBAIngestionHandler(WorkflowHandler):
    """
    Handler for KBA ingestion workflow.
    
    This workflow processes multiple input sources and creates structured
    knowledge base outputs through a 5-stage pipeline:
    1. Source Extraction & Normalization
    2. Content Enrichment & Cleaning  
    3. Content Transformation
    4. File Assembly & Formatting
    5. Export & Manifest Generation
    """
    
    def __init__(self, workflow_type: str = 'kba_ingestion'):
        """Initialize KBA ingestion handler."""
        super().__init__(workflow_type)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info("🔧 KBA Ingestion Handler initialized")
    
    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """
        Validate inputs specific to KBA ingestion workflow.
        
        Args:
            context: Input context to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Call parent validation first
        super().validate_inputs(context)
        
        # KBA specific validations
        client = context.get('client', '').strip()
        if not client or len(client) < 2:
            raise ValueError("Client name must be at least 2 characters")
        
        sources = context.get('sources', [])
        if not sources or not isinstance(sources, list):
            raise ValueError("Sources must be a non-empty list")
        
        if len(sources) > 15:  # Based on refactor plan max sources
            raise ValueError("Maximum 15 sources allowed per workflow")
        
        workflow_mode = context.get('workflow_mode', '').strip()
        if not workflow_mode:
            raise ValueError("Workflow mode is required")

        # Set default processing parameters if not provided
        if 'provider' not in context:
            context['provider'] = 'intelligent_analysis'
        if 'model' not in context:
            context['model'] = 'content_analyzer'
        if 'temperature' not in context:
            context['temperature'] = 0.7

        # Validate each source - ensure they are dictionaries
        for i, source in enumerate(sources):
            # Convert to dict if needed
            if hasattr(source, 'dict') and callable(getattr(source, 'dict')):
                source = source.dict()
                sources[i] = source
            elif hasattr(source, '__dict__'):
                # Convert object to dict using __dict__
                source = source.__dict__
                sources[i] = source
            elif not isinstance(source, dict):
                # Try to convert common object types
                try:
                    source = dict(source)
                    sources[i] = source
                except (TypeError, ValueError):
                    raise ValueError(f"Source {i+1} must be convertible to a dictionary. Got: {type(source)}")
            
            source_type = source.get('type', '').lower()
            if source_type not in ['pdf', 'url', 'md', 'txt', 'docx', 'html']:
                raise ValueError(f"Source {i+1}: Unsupported type '{source_type}'")
            
            if source_type == 'url':
                if not source.get('url'):
                    raise ValueError(f"Source {i+1}: URL is required for URL type")
            else:
                if not source.get('content') and not source.get('file_path'):
                    raise ValueError(f"Source {i+1}: Content or file_path is required")
        
        logger.info(f"✅ KBA validation passed: {len(sources)} sources for {client}")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare and enhance context for KBA processing.
        
        Args:
            context: Input context
            
        Returns:
            Enhanced context with KBA-specific metadata
        """
        # Call parent preparation
        context = super().prepare_context(context)
        
        # Add KBA-specific context
        context['sources_count'] = len(context.get('sources', []))
        context['workflow_id'] = context.get('workflow_id', f"kba_{int(time.time())}")
        context['timestamp'] = time.time()
        context['version'] = "1.0.0"
        
        # Set default output format if not specified
        if 'output_format' not in context:
            context['output_format'] = 'default'
        
        # Create output directory structure
        client = context['client']
        workflow_mode = context['workflow_mode']
        workflow_id = context['workflow_id']
        
        output_base_path = Path("data/outputs") / client / workflow_mode / workflow_id / "v1.0.0"
        context['output_base_path'] = str(output_base_path)
        
        # Ensure output directory exists
        output_base_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔧 KBA context prepared: {context['sources_count']} sources → {output_base_path}")
        return context
    
    def should_skip_task(self, task_id: str, context: Dict[str, Any]) -> bool:
        """
        Determine if a task should be skipped based on context.
        
        Args:
            task_id: ID of the task to check
            context: Current context
            
        Returns:
            True if task should be skipped
        """
        # For now, no tasks are skipped in KBA ingestion
        # Future: Could skip based on source types or workflow modes
        return False
    
    def post_process_task(self, task_id: str, task_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process individual task outputs.
        
        Args:
            task_id: ID of the completed task
            task_output: Output from the task
            context: Current context
            
        Returns:
            Updated context
        """
        logger.info(f"📝 Post-processing task: {task_id}")
        
        # Store task output in context for next tasks
        if 'task_outputs' not in context:
            context['task_outputs'] = {}
        context['task_outputs'][task_id] = task_output
        
        # Task-specific post-processing
        if task_id == 'task1_extract':
            # After extraction, we should have normalized content
            context['extracted_content'] = task_output
            logger.info("✅ Content extraction completed")
            
        elif task_id == 'task2_enrich':
            # After enrichment, we have cleaned and merged content
            context['enriched_content'] = task_output
            logger.info("✅ Content enrichment completed")
            
        elif task_id == 'task3_transform':
            # After transformation, we have structured content
            context['transformed_content'] = task_output
            logger.info("✅ Content transformation completed")
            
        elif task_id == 'task4_assemble':
            # After assembly, we have formatted files
            context['assembled_files'] = task_output
            logger.info("✅ File assembly completed")
            
        elif task_id == 'task5_export':
            # After export, we have saved files and manifest
            context['exported_files'] = task_output
            logger.info("✅ Export completed")
        
        return context
    
    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process the entire KBA workflow.

        Args:
            context: Final context after all tasks

        Returns:
            Final processed context with KBA results
        """
        logger.info("🔧 KBA workflow post-processing started")
        
        # Collect all outputs
        final_output = context.get('exported_files', '')
        task_outputs = context.get('task_outputs', {})
        
        # Create workflow summary
        workflow_summary = {
            'workflow_id': context.get('workflow_id'),
            'client': context.get('client'),
            'workflow_mode': context.get('workflow_mode'),
            'sources_processed': context.get('sources_count', 0),
            'output_path': context.get('output_base_path'),
            'success': bool(final_output),
            'timestamp': context.get('timestamp')
        }
        
        context['workflow_summary'] = workflow_summary
        context['final_content'] = final_output
        
        logger.info(f"🎉 KBA workflow completed: {workflow_summary}")
        return context

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete KBA ingestion pipeline.

        This method orchestrates the entire KBA workflow:
        1. Parse all sources
        2. Transform content based on workflow mode
        3. Export files to disk

        Args:
            context: Workflow context

        Returns:
            Updated context with results
        """
        self.logger.info("🚀 Starting KBA ingestion pipeline")

        try:
            # Validate and prepare context
            self.validate_inputs(context)
            context = self.prepare_context(context)

            # Step 1: Parse all sources
            self.logger.info("📄 Step 1: Parsing sources")
            parsed_contents = await self._parse_sources(context['sources'])
            context['parsed_contents'] = parsed_contents

            # Step 2: Transform content
            self.logger.info("🔄 Step 2: Transforming content")
            transformed_content = await self._transform_content(parsed_contents, context)
            context['transformed_content'] = transformed_content

            # Step 3: Export files
            self.logger.info("💾 Step 3: Exporting files")
            export_result = await self._export_files(transformed_content, context)
            context['export_result'] = export_result

            # Update context with final results
            context['final_content'] = f"KBA processing completed successfully. {len(transformed_content.files)} files exported."
            context['exported_files'] = list(transformed_content.files.keys())

            # Create workflow summary
            workflow_summary = {
                'workflow_id': context.get('workflow_id'),
                'client': context.get('client'),
                'workflow_mode': context.get('workflow_mode'),
                'sources_processed': len(parsed_contents),
                'files_generated': len(transformed_content.files),
                'output_path': export_result.get('output_directory'),
                'success': True,
                'timestamp': context.get('timestamp')
            }
            context['workflow_summary'] = workflow_summary

            self.logger.info(f"✅ KBA pipeline completed successfully: {workflow_summary}")
            return context

        except Exception as e:
            self.logger.error(f"❌ KBA pipeline failed: {str(e)}")
            context['error'] = str(e)
            context['success'] = False
            raise

    async def _parse_sources(self, sources: List[Dict[str, Any]]) -> List['ParsedContent']:
        """
        Parse all sources using appropriate parsers.

        Args:
            sources: List of source dictionaries

        Returns:
            List of ParsedContent objects
        """
        parsed_contents = []

        for i, source in enumerate(sources):
            try:
                self.logger.info(f"📄 Parsing source {i+1}/{len(sources)}: {source.get('type', 'unknown')}")

                # Get appropriate parser and parse
                parsed_content = await ParserFactory.parse_source(source)
                parsed_contents.append(parsed_content)

                self.logger.info(f"✅ Source {i+1} parsed: {parsed_content.get_summary()}")

            except Exception as e:
                self.logger.error(f"❌ Failed to parse source {i+1}: {str(e)}")
                # Continue with other sources instead of failing completely
                continue

        if not parsed_contents:
            raise ValueError("No sources could be parsed successfully")

        self.logger.info(f"📄 Parsing completed: {len(parsed_contents)}/{len(sources)} sources parsed")
        return parsed_contents

    async def _transform_content(self,
                                parsed_contents: List['ParsedContent'],
                                context: Dict[str, Any]) -> 'TransformedContent':
        """
        Transform parsed content using appropriate transformer.

        Args:
            parsed_contents: List of ParsedContent objects
            context: Workflow context

        Returns:
            TransformedContent object
        """
        workflow_mode = context['workflow_mode']

        self.logger.info(f"🔄 Transforming content for mode: {workflow_mode}")

        # Transform content using appropriate transformer
        transformed_content = await TransformerFactory.transform_content(
            workflow_mode=workflow_mode,
            parsed_contents=parsed_contents,
            context=context
        )

        self.logger.info(f"✅ Content transformed: {transformed_content.get_summary()}")
        return transformed_content

    async def _export_files(self,
                           transformed_content: 'TransformedContent',
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export transformed content to files.

        Args:
            transformed_content: TransformedContent object
            context: Workflow context

        Returns:
            Export result dictionary
        """
        self.logger.info("💾 Exporting files to disk")

        # Create exporter and export
        exporter = KBAExporter()
        export_result = await exporter.export(transformed_content, context)

        self.logger.info(f"✅ Files exported: {export_result.get('total_files', 0)} files")
        return export_result
