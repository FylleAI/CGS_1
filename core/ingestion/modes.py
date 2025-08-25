"""
Workflow mode configurations for KBA (Knowledge Base Assistant).

This module defines different workflow modes that determine how content
is transformed and what output files are generated.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class OutputFormat(Enum):
    """Supported output formats."""
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


@dataclass
class OutputFile:
    """Configuration for an output file."""
    name: str
    type: OutputFormat
    description: str
    required: bool = True


@dataclass
class WorkflowMode:
    """Configuration for a workflow mode."""
    name: str
    description: str
    transformer: str
    estimated_time: str
    required_sources: Dict[str, int]
    outputs: List[OutputFile]
    enabled: bool = True
    extensions: Dict[str, Any] = None


# Define all workflow modes
WORKFLOW_MODES = {
    "brand_kba_4docs": WorkflowMode(
        name="brand_kba_4docs",
        description="Brand Knowledge Base - 4 Documents",
        transformer="brand_kba",
        estimated_time="3-7 minutes",
        required_sources={"min": 2, "max": 15},
        outputs=[
            OutputFile(
                name="company_profile_brand_voice.md",
                type=OutputFormat.MARKDOWN,
                description="Company profile and brand voice guidelines"
            ),
            OutputFile(
                name="production_guide.md",
                type=OutputFormat.MARKDOWN,
                description="Content production guidelines and processes"
            ),
            OutputFile(
                name="quality_standards.md",
                type=OutputFormat.MARKDOWN,
                description="Quality standards and compliance requirements"
            ),
            OutputFile(
                name="voice_examples.md",
                type=OutputFormat.MARKDOWN,
                description="Voice examples and cultural context"
            )
        ]
    ),

    "faq_kba": WorkflowMode(
        name="faq_kba",
        description="FAQ Knowledge Base Generation",
        transformer="faq_kba",
        estimated_time="2-5 minutes",
        required_sources={"min": 1, "max": 10},
        outputs=[
            OutputFile(
                name="faq.md",
                type=OutputFormat.MARKDOWN,
                description="Formatted FAQ in markdown"
            ),
            OutputFile(
                name="faq.json",
                type=OutputFormat.JSON,
                description="Structured FAQ data"
            )
        ]
    ),

    "documentation_kba": WorkflowMode(
        name="documentation_kba",
        description="Technical Documentation Knowledge Base",
        transformer="documentation_kba",
        estimated_time="4-8 minutes",
        required_sources={"min": 2, "max": 20},
        outputs=[
            OutputFile(
                name="overview.md",
                type=OutputFormat.MARKDOWN,
                description="System overview and introduction"
            ),
            OutputFile(
                name="user_guide.md",
                type=OutputFormat.MARKDOWN,
                description="User guide and tutorials"
            ),
            OutputFile(
                name="api_reference.md",
                type=OutputFormat.MARKDOWN,
                description="API reference documentation"
            ),
            OutputFile(
                name="troubleshooting.md",
                type=OutputFormat.MARKDOWN,
                description="Troubleshooting guide and FAQ"
            )
        ]
    ),

    "training_kba": WorkflowMode(
        name="training_kba",
        description="Training Material Knowledge Base",
        transformer="training_kba",
        estimated_time="5-10 minutes",
        required_sources={"min": 3, "max": 25},
        outputs=[
            OutputFile(
                name="training_overview.md",
                type=OutputFormat.MARKDOWN,
                description="Training program overview"
            ),
            OutputFile(
                name="modules.md",
                type=OutputFormat.MARKDOWN,
                description="Training modules and curriculum"
            ),
            OutputFile(
                name="exercises.md",
                type=OutputFormat.MARKDOWN,
                description="Practical exercises and examples"
            ),
            OutputFile(
                name="assessment.md",
                type=OutputFormat.MARKDOWN,
                description="Assessment criteria and tests"
            )
        ]
    ),

    # Future workflow modes (disabled by default)
    "visualization_kba": WorkflowMode(
        name="visualization_kba",
        description="Knowledge Base with Interactive Visualizations",
        transformer="visualization_kba",
        estimated_time="5-15 minutes",
        required_sources={"min": 2, "max": 20},
        enabled=False,  # Feature flag
        outputs=[
            OutputFile(
                name="dashboard.html",
                type=OutputFormat.HTML,
                description="Interactive dashboard"
            ),
            OutputFile(
                name="knowledge_graph.json",
                type=OutputFormat.JSON,
                description="Knowledge graph data"
            ),
            OutputFile(
                name="interactive_cards.json",
                type=OutputFormat.JSON,
                description="Interactive card data"
            )
        ],
        extensions={
            "visualizations": True,
            "interactivity": True,
            "export_formats": ["html", "pdf", "json"]
        }
    ),

    "listening_kba": WorkflowMode(
        name="listening_kba",
        description="Self-Updating Knowledge Base with Monitoring",
        transformer="listening_kba",
        estimated_time="3-8 minutes",
        required_sources={"min": 1, "max": 15},
        enabled=False,  # Feature flag
        outputs=[
            OutputFile(
                name="knowledge_base.md",
                type=OutputFormat.MARKDOWN,
                description="Main knowledge base content"
            ),
            OutputFile(
                name="monitors.json",
                type=OutputFormat.JSON,
                description="Monitoring configuration"
            ),
            OutputFile(
                name="update_schedule.json",
                type=OutputFormat.JSON,
                description="Update schedule configuration"
            )
        ],
        extensions={
            "monitoring": True,
            "auto_update": True,
            "notification": True
        }
    ),

    "segmented_kba": WorkflowMode(
        name="segmented_kba",
        description="Segmented Knowledge Base with Interactive Cards",
        transformer="segmented_kba",
        estimated_time="7-20 minutes",
        required_sources={"min": 3, "max": 30},
        enabled=False,  # Feature flag
        outputs=[
            OutputFile(
                name="topic_segments.json",
                type=OutputFormat.JSON,
                description="Content segmented by topic"
            ),
            OutputFile(
                name="audience_segments.json",
                type=OutputFormat.JSON,
                description="Content segmented by audience"
            ),
            OutputFile(
                name="interactive_cards.json",
                type=OutputFormat.JSON,
                description="Interactive card definitions"
            ),
            OutputFile(
                name="card_dashboard.html",
                type=OutputFormat.HTML,
                description="Card-based dashboard"
            )
        ],
        extensions={
            "segmentation": True,
            "cards": True,
            "search": True,
            "recommendations": True
        }
    )
}


def get_workflow_mode(mode_name: str) -> WorkflowMode:
    """
    Get workflow mode configuration by name.
    
    Args:
        mode_name: Name of the workflow mode
        
    Returns:
        WorkflowMode configuration
        
    Raises:
        ValueError: If mode is not found or disabled
    """
    mode = WORKFLOW_MODES.get(mode_name)
    if not mode:
        raise ValueError(f"Unknown workflow mode: {mode_name}")
    
    if not mode.enabled:
        raise ValueError(f"Workflow mode is disabled: {mode_name}")
    
    return mode


def list_available_modes() -> List[str]:
    """
    Get list of available (enabled) workflow modes.
    
    Returns:
        List of workflow mode names
    """
    return [name for name, mode in WORKFLOW_MODES.items() if mode.enabled]


def validate_sources_for_mode(mode_name: str, source_count: int) -> bool:
    """
    Validate if source count is appropriate for workflow mode.
    
    Args:
        mode_name: Name of the workflow mode
        source_count: Number of sources
        
    Returns:
        True if source count is valid
    """
    mode = get_workflow_mode(mode_name)
    min_sources = mode.required_sources.get("min", 1)
    max_sources = mode.required_sources.get("max", 100)
    
    return min_sources <= source_count <= max_sources


def get_mode_info() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all workflow modes.
    
    Returns:
        Dictionary with mode information
    """
    return {
        name: {
            "description": mode.description,
            "estimated_time": mode.estimated_time,
            "required_sources": mode.required_sources,
            "output_count": len(mode.outputs),
            "enabled": mode.enabled
        }
        for name, mode in WORKFLOW_MODES.items()
    }
