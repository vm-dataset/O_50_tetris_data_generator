"""
Tetris task implementation.

This module provides:
    - TaskConfig: Tetris-specific configuration (map size, difficulty, etc.)
    - TaskGenerator: Tetris task generation logic (easy/medium/hard)
    - get_prompt: Tetris task prompts/instructions
    - tetris_core: Core Tetris game logic (blocks, map, line clearing)
"""

from .config import TaskConfig
from .generator import TaskGenerator
from .prompts import get_prompt

__all__ = ["TaskConfig", "TaskGenerator", "get_prompt"]
