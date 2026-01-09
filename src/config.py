"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK CONFIGURATION                             ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define your task-specific settings.                   ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import Optional
from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Your task-specific configuration.
    
    CUSTOMIZE THIS CLASS to add your task's hyperparameters.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    
    domain: str = Field(default="tetris")
    image_size: tuple[int, int] = Field(default=(400, 400))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TETRIS-SPECIFIC SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    map_width: int = Field(
        default=5,
        description="Tetris map width (5 for easy, 10 for medium/hard)"
    )
    
    map_height: int = Field(
        default=5,
        description="Tetris map height (5 for easy, 10 for medium/hard)"
    )
    
    num_init_rows: int = Field(
        default=2,
        description="Number of bottom rows to initialize (2 for easy, 3 for medium/hard)"
    )
    
    fill_ratio: float = Field(
        default=0.8,
        description="Fill ratio for initial rows (0.0-1.0)"
    )
    
    guarantee_clear: Optional[bool] = Field(
        default=None,
        description="Guarantee line clear: True=always clear, False=never clear, None=random"
    )
