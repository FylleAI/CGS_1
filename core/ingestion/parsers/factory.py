"""
Parser factory for creating appropriate parsers based on source type.
"""

import logging
from typing import Dict, Any, Optional, List, Type
from .base import BaseParser

logger = logging.getLogger(__name__)


class ParserFactory:
    """
    Factory class for creating and managing content parsers.
    
    This factory automatically selects the appropriate parser based on
    the source type and maintains a registry of available parsers.
    """
    
    _parsers: Dict[str, Type[BaseParser]] = {}
    _instances: Dict[str, BaseParser] = {}
    
    @classmethod
    def register_parser(cls, source_type: str, parser_class: Type[BaseParser]) -> None:
        """
        Register a parser class for a specific source type.
        
        Args:
            source_type: Type of source this parser handles (e.g., 'pdf', 'url')
            parser_class: Parser class that inherits from BaseParser
        """
        if not issubclass(parser_class, BaseParser):
            raise ValueError(f"Parser class must inherit from BaseParser: {parser_class}")
        
        cls._parsers[source_type.lower()] = parser_class
        logger.info(f"📝 Registered parser: {source_type} -> {parser_class.__name__}")
    
    @classmethod
    def get_parser(cls, source_type: str) -> BaseParser:
        """
        Get a parser instance for the specified source type.
        
        Args:
            source_type: Type of source to get parser for
            
        Returns:
            Parser instance
            
        Raises:
            ValueError: If no parser is registered for the source type
        """
        source_type = source_type.lower()
        
        # Return cached instance if available
        if source_type in cls._instances:
            return cls._instances[source_type]
        
        # Create new instance
        parser_class = cls._parsers.get(source_type)
        if not parser_class:
            raise ValueError(f"No parser registered for source type: {source_type}")
        
        parser_instance = parser_class()
        cls._instances[source_type] = parser_instance
        
        logger.debug(f"🔧 Created parser instance: {source_type} -> {parser_class.__name__}")
        return parser_instance
    
    @classmethod
    def get_parser_for_source(cls, source: Dict[str, Any]) -> BaseParser:
        """
        Get the appropriate parser for a source object.
        
        Args:
            source: Source dictionary with type information
            
        Returns:
            Parser instance that can handle the source
            
        Raises:
            ValueError: If no suitable parser is found
        """
        source_type = source.get('type', '').lower()
        if not source_type:
            raise ValueError("Source must have a 'type' field")
        
        parser = cls.get_parser(source_type)
        
        # Verify the parser can actually handle this source
        if not parser.can_parse(source):
            raise ValueError(f"Parser {parser.__class__.__name__} cannot handle source: {source}")
        
        return parser
    
    @classmethod
    def list_supported_types(cls) -> List[str]:
        """
        Get list of supported source types.
        
        Returns:
            List of supported source type strings
        """
        return list(cls._parsers.keys())
    
    @classmethod
    def is_supported(cls, source_type: str) -> bool:
        """
        Check if a source type is supported.
        
        Args:
            source_type: Source type to check
            
        Returns:
            True if source type is supported
        """
        return source_type.lower() in cls._parsers
    
    @classmethod
    async def parse_source(cls, source: Dict[str, Any]) -> 'ParsedContent':
        """
        Convenience method to parse a source using the appropriate parser.
        
        Args:
            source: Source dictionary to parse
            
        Returns:
            ParsedContent object
            
        Raises:
            ValueError: If no suitable parser is found or parsing fails
        """
        parser = cls.get_parser_for_source(source)
        return await parser.parse(source)
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the parser instance cache."""
        cls._instances.clear()
        logger.info("🧹 Parser instance cache cleared")
    
    @classmethod
    def get_registry_info(cls) -> Dict[str, str]:
        """
        Get information about registered parsers.
        
        Returns:
            Dictionary mapping source types to parser class names
        """
        return {
            source_type: parser_class.__name__ 
            for source_type, parser_class in cls._parsers.items()
        }


# Decorator for auto-registering parsers
def register_parser(source_type: str):
    """
    Decorator for automatically registering parser classes.
    
    Usage:
        @register_parser('pdf')
        class PDFParser(BaseParser):
            pass
    """
    def decorator(parser_class: Type[BaseParser]):
        ParserFactory.register_parser(source_type, parser_class)
        return parser_class
    return decorator
