"""
Workflow registry for dynamic workflow management.
"""

import logging
from typing import Dict, Type, Any
from .base.workflow_base import WorkflowHandler

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    """
    Registry for managing workflow handlers dynamically.
    
    This allows adding new workflow types without modifying core code.
    """
    
    def __init__(self):
        self._handlers: Dict[str, Type[WorkflowHandler]] = {}
        self._instances: Dict[str, WorkflowHandler] = {}
        logger.info("🏗️ Workflow registry initialized")
    
    def register(self, workflow_type: str, handler_class: Type[WorkflowHandler]) -> None:
        """
        Register a workflow handler class.
        
        Args:
            workflow_type: Unique identifier for the workflow type
            handler_class: Handler class that inherits from WorkflowHandler
        """
        if not issubclass(handler_class, WorkflowHandler):
            raise ValueError(f"Handler must inherit from WorkflowHandler: {handler_class}")
        
        self._handlers[workflow_type] = handler_class
        logger.info(f"📝 Registered workflow handler: {workflow_type} -> {handler_class.__name__}")
    
    def get_handler(self, workflow_type: str) -> WorkflowHandler:
        """
        Get a workflow handler instance.
        
        Args:
            workflow_type: Type of workflow to get handler for
            
        Returns:
            WorkflowHandler instance
            
        Raises:
            ValueError: If workflow type is not registered
        """
        if workflow_type not in self._handlers:
            available_types = list(self._handlers.keys())
            raise ValueError(f"Unknown workflow type: {workflow_type}. Available: {available_types}")
        
        # Use cached instance if available
        if workflow_type not in self._instances:
            handler_class = self._handlers[workflow_type]
            self._instances[workflow_type] = handler_class(workflow_type)
            logger.debug(f"🔧 Created new handler instance: {workflow_type}")
        
        return self._instances[workflow_type]
    
    def list_workflows(self) -> Dict[str, str]:
        """
        List all registered workflow types.
        
        Returns:
            Dictionary mapping workflow_type to handler class name
        """
        return {
            workflow_type: handler_class.__name__ 
            for workflow_type, handler_class in self._handlers.items()
        }
    
    def is_registered(self, workflow_type: str) -> bool:
        """Check if a workflow type is registered."""
        return workflow_type in self._handlers
    
    async def execute_workflow(self, workflow_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow with dynamic context.
        
        Args:
            workflow_type: Type of workflow to execute
            context: Dynamic context from frontend
            
        Returns:
            Execution results
        """
        logger.info(f"🚀 Executing workflow: {workflow_type}")
        logger.debug(f"📊 Context keys: {list(context.keys())}")
        
        handler = self.get_handler(workflow_type)
        result = await handler.execute(context)
        
        logger.info(f"✅ Workflow execution completed: {workflow_type}")
        return result


# Global registry instance
workflow_registry = WorkflowRegistry()


def register_workflow(workflow_type: str):
    """
    Decorator for registering workflow handlers.
    
    Usage:
        @register_workflow('enhanced_article')
        class EnhancedArticleHandler(WorkflowHandler):
            pass
    """
    def decorator(handler_class: Type[WorkflowHandler]):
        workflow_registry.register(workflow_type, handler_class)
        return handler_class
    return decorator


def get_workflow_handler(workflow_type: str) -> WorkflowHandler:
    """Get a workflow handler instance."""
    return workflow_registry.get_handler(workflow_type)


async def execute_dynamic_workflow(workflow_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a workflow with dynamic context."""
    return await workflow_registry.execute_workflow(workflow_type, context)


def list_available_workflows() -> Dict[str, str]:
    """List all available workflow types."""
    return workflow_registry.list_workflows()
