"""
Creative Automation Pipeline utilities.

This package contains the core utility modules for the Creative Automation Pipeline:
- AssetManager: Handles asset discovery and file organization
- ImageGenerator: Manages GenAI image generation and placeholders
- CreativeGenerator: Creates multi-aspect ratio creatives with text overlays
- MetricsManager: Tracks campaign analytics and saves metrics to JSON files
- ContentModerator: Validates campaign content for compliance and legal requirements
"""

from .asset_manager import AssetManager
from .image_generator import ImageGenerator
from .creative_generator import CreativeGenerator
from .metrics_manager import MetricsManager
from .content_moderator import ContentModerator

__all__ = ['AssetManager', 'ImageGenerator', 'CreativeGenerator', 'MetricsManager', 'ContentModerator']