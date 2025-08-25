"""
Base transformer interface for KBA content transformation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class TransformedContent:
    """
    Container for transformed content ready for export.
    
    This represents the final structured output that will be
    saved as files in the knowledge base.
    """
    files: Dict[str, str] = field(default_factory=dict)  # filename -> content
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    word_count: int = 0
    
    def __post_init__(self):
        """Calculate total word count if not provided."""
        if self.word_count == 0:
            self.word_count = sum(len(content.split()) for content in self.files.values())
    
    def is_valid(self) -> bool:
        """Check if the transformed content is valid."""
        return bool(self.files and all(content.strip() for content in self.files.values()))
    
    def get_file_list(self) -> List[str]:
        """Get list of generated file names."""
        return list(self.files.keys())
    
    def get_summary(self) -> str:
        """Get a brief summary of the transformed content."""
        return f"Files: {len(self.files)}, Total words: {self.word_count}"


class BaseTransformer(ABC):
    """
    Abstract base class for content transformers.
    
    Each transformer handles a specific workflow mode and converts
    parsed content into structured knowledge base files.
    """
    
    def __init__(self, workflow_mode: str):
        """
        Initialize the transformer.
        
        Args:
            workflow_mode: The workflow mode this transformer handles
        """
        self.workflow_mode = workflow_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def can_transform(self, workflow_mode: str) -> bool:
        """
        Check if this transformer can handle the given workflow mode.
        
        Args:
            workflow_mode: Workflow mode to check
            
        Returns:
            True if this transformer can handle the mode
        """
        pass
    
    @abstractmethod
    async def transform(self, 
                       parsed_contents: List['ParsedContent'], 
                       context: Dict[str, Any]) -> TransformedContent:
        """
        Transform parsed content into structured knowledge base files.
        
        Args:
            parsed_contents: List of ParsedContent objects from parsing stage
            context: Workflow context with additional information
            
        Returns:
            TransformedContent object with generated files
            
        Raises:
            ValueError: If transformation fails
        """
        pass
    
    def _merge_content(self, parsed_contents: List['ParsedContent']) -> str:
        """
        Merge multiple parsed contents into a single text.
        
        Args:
            parsed_contents: List of ParsedContent objects
            
        Returns:
            Merged content string
        """
        content_parts = []
        
        for i, parsed in enumerate(parsed_contents):
            if parsed.title:
                content_parts.append(f"# {parsed.title}")
            
            content_parts.append(parsed.content_md)
            
            # Add source information
            if parsed.origin:
                source_info = []
                if 'url' in parsed.origin:
                    source_info.append(f"Source: {parsed.origin['url']}")
                elif 'filename' in parsed.origin:
                    source_info.append(f"Source: {parsed.origin['filename']}")
                
                if source_info:
                    content_parts.append(f"\n*{', '.join(source_info)}*")
            
            # Add separator between sources
            if i < len(parsed_contents) - 1:
                content_parts.append("\n---\n")
        
        return '\n\n'.join(content_parts)
    
    def _extract_key_themes(self, content: str) -> List[str]:
        """
        Extract key themes from content (basic implementation).
        
        Args:
            content: Content to analyze
            
        Returns:
            List of key themes/topics
        """
        # Simple keyword extraction - could be enhanced with NLP
        words = content.lower().split()
        
        # Common business/technical terms that might indicate themes
        theme_indicators = {
            'brand', 'marketing', 'customer', 'product', 'service',
            'quality', 'process', 'workflow', 'team', 'strategy',
            'technology', 'development', 'design', 'user', 'experience',
            'data', 'analytics', 'security', 'compliance', 'training'
        }
        
        found_themes = []
        for word in theme_indicators:
            if word in words:
                found_themes.append(word.title())
        
        return found_themes[:10]  # Limit to top 10
    
    def _create_metadata(self, 
                        parsed_contents: List['ParsedContent'], 
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create metadata for transformed content.
        
        Args:
            parsed_contents: List of ParsedContent objects
            context: Workflow context
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'workflow_mode': self.workflow_mode,
            'source_count': len(parsed_contents),
            'total_word_count': sum(p.word_count for p in parsed_contents),
            'languages': list(set(p.language for p in parsed_contents if p.language)),
            'source_types': list(set(p.origin.get('source_type') for p in parsed_contents if p.origin)),
            'created_at': context.get('timestamp'),
            'client': context.get('client'),
            'workflow_id': context.get('workflow_id')
        }
        
        # Extract themes
        merged_content = self._merge_content(parsed_contents)
        metadata['key_themes'] = self._extract_key_themes(merged_content)
        
        return metadata
    
    def _format_content_section(self, title: str, content: str, level: int = 2) -> str:
        """
        Format a content section with proper markdown headers.
        
        Args:
            title: Section title
            content: Section content
            level: Header level (1-6)
            
        Returns:
            Formatted markdown section
        """
        header = '#' * level
        return f"{header} {title}\n\n{content.strip()}\n\n"
    
    def _clean_and_format(self, content: str) -> str:
        """
        Clean and format content for final output.
        
        Args:
            content: Raw content
            
        Returns:
            Cleaned and formatted content
        """
        if not content:
            return ""
        
        # Basic cleaning
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive whitespace
            cleaned_line = ' '.join(line.split())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        # Join with proper spacing
        return '\n\n'.join(cleaned_lines)
    
    def _generate_summary(self, files: Dict[str, str]) -> str:
        """
        Generate a summary of the transformed content.
        
        Args:
            files: Dictionary of filename -> content
            
        Returns:
            Summary string
        """
        file_summaries = []
        
        for filename, content in files.items():
            word_count = len(content.split())
            file_summaries.append(f"- {filename}: {word_count} words")
        
        return f"Generated {len(files)} files:\n" + '\n'.join(file_summaries)
