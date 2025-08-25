"""
Transformer factory for creating appropriate transformers based on workflow mode.
"""

import logging
from typing import Dict, Any, Type, List
from .base import BaseTransformer

logger = logging.getLogger(__name__)


class TransformerFactory:
    """
    Factory class for creating and managing content transformers.
    
    This factory automatically selects the appropriate transformer based on
    the workflow mode and maintains a registry of available transformers.
    """
    
    _transformers: Dict[str, Type[BaseTransformer]] = {}
    _instances: Dict[str, BaseTransformer] = {}
    
    @classmethod
    def register_transformer(cls, workflow_mode: str, transformer_class: Type[BaseTransformer]) -> None:
        """
        Register a transformer class for a specific workflow mode.
        
        Args:
            workflow_mode: Workflow mode this transformer handles
            transformer_class: Transformer class that inherits from BaseTransformer
        """
        if not issubclass(transformer_class, BaseTransformer):
            raise ValueError(f"Transformer class must inherit from BaseTransformer: {transformer_class}")
        
        cls._transformers[workflow_mode] = transformer_class
        logger.info(f"📝 Registered transformer: {workflow_mode} -> {transformer_class.__name__}")
    
    @classmethod
    def get_transformer(cls, workflow_mode: str) -> BaseTransformer:
        """
        Get a transformer instance for the specified workflow mode.
        
        Args:
            workflow_mode: Workflow mode to get transformer for
            
        Returns:
            Transformer instance
            
        Raises:
            ValueError: If no transformer is registered for the workflow mode
        """
        # Return cached instance if available
        if workflow_mode in cls._instances:
            return cls._instances[workflow_mode]
        
        # Create new instance
        transformer_class = cls._transformers.get(workflow_mode)
        if not transformer_class:
            raise ValueError(f"No transformer registered for workflow mode: {workflow_mode}")
        
        transformer_instance = transformer_class(workflow_mode)
        cls._instances[workflow_mode] = transformer_instance
        
        logger.debug(f"🔧 Created transformer instance: {workflow_mode} -> {transformer_class.__name__}")
        return transformer_instance
    
    @classmethod
    def list_supported_modes(cls) -> List[str]:
        """
        Get list of supported workflow modes.
        
        Returns:
            List of supported workflow mode strings
        """
        return list(cls._transformers.keys())
    
    @classmethod
    def is_supported(cls, workflow_mode: str) -> bool:
        """
        Check if a workflow mode is supported.
        
        Args:
            workflow_mode: Workflow mode to check
            
        Returns:
            True if workflow mode is supported
        """
        return workflow_mode in cls._transformers
    
    @classmethod
    async def transform_content(cls, 
                               workflow_mode: str,
                               parsed_contents: List['ParsedContent'], 
                               context: Dict[str, Any]) -> 'TransformedContent':
        """
        Convenience method to transform content using the appropriate transformer.
        
        Args:
            workflow_mode: Workflow mode to use
            parsed_contents: List of ParsedContent objects
            context: Workflow context
            
        Returns:
            TransformedContent object
            
        Raises:
            ValueError: If no suitable transformer is found or transformation fails
        """
        transformer = cls.get_transformer(workflow_mode)
        return await transformer.transform(parsed_contents, context)
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the transformer instance cache."""
        cls._instances.clear()
        logger.info("🧹 Transformer instance cache cleared")
    
    @classmethod
    def get_registry_info(cls) -> Dict[str, str]:
        """
        Get information about registered transformers.
        
        Returns:
            Dictionary mapping workflow modes to transformer class names
        """
        return {
            workflow_mode: transformer_class.__name__ 
            for workflow_mode, transformer_class in cls._transformers.items()
        }


# Decorator for auto-registering transformers
def register_transformer(workflow_mode: str):
    """
    Decorator for automatically registering transformer classes.
    
    Usage:
        @register_transformer('brand_kba_4docs')
        class BrandKBATransformer(BaseTransformer):
            pass
    """
    def decorator(transformer_class: Type[BaseTransformer]):
        TransformerFactory.register_transformer(workflow_mode, transformer_class)
        return transformer_class
    return decorator
