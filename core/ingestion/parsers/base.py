"""
Base parser interface and data structures for KBA ingestion.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParsedContent:
    """
    Standardized container for parsed content from any source.
    
    This class ensures all parsers return content in a consistent format
    that can be processed by the downstream transformation pipeline.
    """
    content_md: str = ""
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    origin: Dict[str, Any] = field(default_factory=dict)
    word_count: int = 0
    language: Optional[str] = None
    
    def __post_init__(self):
        """Calculate word count if not provided."""
        if self.word_count == 0 and self.content_md:
            self.word_count = len(self.content_md.split())
    
    def is_valid(self) -> bool:
        """Check if the parsed content is valid."""
        return bool(self.content_md and self.content_md.strip())
    
    def get_summary(self) -> str:
        """Get a brief summary of the parsed content."""
        return f"Title: {self.title or 'N/A'}, Words: {self.word_count}, Language: {self.language or 'N/A'}"


class BaseParser(ABC):
    """
    Abstract base class for all content parsers.
    
    Each parser implementation must handle a specific source type
    and return standardized ParsedContent objects.
    """
    
    def __init__(self):
        """Initialize the parser."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def can_parse(self, source: Dict[str, Any]) -> bool:
        """
        Check if this parser can handle the given source.
        
        Args:
            source: Source dictionary with type and content/url information
            
        Returns:
            True if this parser can handle the source
        """
        pass
    
    @abstractmethod
    async def parse(self, source: Dict[str, Any]) -> ParsedContent:
        """
        Parse the source and return standardized content.
        
        Args:
            source: Source dictionary with type and content/url information
            
        Returns:
            ParsedContent object with extracted and normalized content
            
        Raises:
            ValueError: If source cannot be parsed
            Exception: For other parsing errors
        """
        pass
    
    def _extract_metadata(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from source.
        
        Args:
            source: Source dictionary
            
        Returns:
            Metadata dictionary
        """
        metadata = {}
        
        # Common metadata fields
        if 'filename' in source:
            metadata['filename'] = source['filename']
        if 'file_size' in source:
            metadata['file_size'] = source['file_size']
        if 'created_at' in source:
            metadata['created_at'] = source['created_at']
        if 'modified_at' in source:
            metadata['modified_at'] = source['modified_at']
        
        return metadata
    
    def _create_origin_info(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create origin information for traceability.
        
        Args:
            source: Source dictionary
            
        Returns:
            Origin information dictionary
        """
        origin = {
            'source_type': source.get('type', 'unknown'),
            'parser_class': self.__class__.__name__
        }
        
        if 'url' in source:
            origin['url'] = source['url']
        if 'file_path' in source:
            origin['file_path'] = source['file_path']
        if 'filename' in source:
            origin['filename'] = source['filename']
        
        return origin
    
    def _clean_content(self, content: str) -> str:
        """
        Clean and normalize content.
        
        Args:
            content: Raw content string
            
        Returns:
            Cleaned content string
        """
        if not content:
            return ""
        
        # Basic cleaning
        content = content.strip()
        
        # Remove excessive whitespace
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line:  # Skip empty lines
                cleaned_lines.append(cleaned_line)
        
        return '\n\n'.join(cleaned_lines)
    
    def _detect_language(self, content: str) -> Optional[str]:
        """
        Detect content language (basic implementation).
        
        Args:
            content: Content to analyze
            
        Returns:
            Detected language code or None
        """
        # Simple heuristic - could be enhanced with proper language detection
        if not content:
            return None
        
        # Check for common English words
        english_indicators = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        content_lower = content.lower()
        
        english_count = sum(1 for word in english_indicators if word in content_lower)
        
        if english_count >= 3:
            return 'en'
        
        return None  # Unknown language
