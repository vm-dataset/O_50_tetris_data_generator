"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           TETRIS TASK PROMPTS                                 ║
║                                                                               ║
║  Prompts for Tetris line-clearing reasoning tasks.                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  TETRIS PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Given a {n}x{n} Tetris map, determine whether any complete line(s) will be "
        "cleared after a new block locks. Difficulty: {difficulty}.\n\n"
        "If lines are cleared, simulate the elimination process and provide the final map. "
        "IMPORTANT (for visualization): when a line is cleared, animate that row by briefly "
        "flashing or highlighting the cleared cells and then removing them in-place — do NOT "
        "create new blocks or use an upward 'flip' animation. After removal, let blocks above "
        "fall straight down to fill the emptied cells. For simple cases, show a short local "
        "flash-and-disappear animation focused only on the cleared line(s). Also include a "
        "brief textual description of the animation steps (e.g., 'row flashes then disappears, "
        "blocks above fall down').",
    ],
    
    "easy": [
        "Given a 5x5 Tetris map with 2 bottom rows pre-filled, determine whether any complete "
        "line(s) will be cleared. Simulate line clearing only (no new block drop).\n\n"
        "If lines are cleared, animate the elimination: briefly flash the cleared row(s), then "
        "remove them, and show blocks above falling down to fill the gaps.",
    ],
    
    "medium": [
        "Given a 10x10 Tetris map with 3 bottom rows pre-filled, determine whether any complete "
        "line(s) will be cleared. Simulate line clearing only (no new block drop).\n\n"
        "If lines are cleared, animate the elimination: briefly flash the cleared row(s), then "
        "remove them, and show blocks above falling down to fill the gaps.",
    ],
    
    "hard": [
        "Given a 10x10 Tetris map with 3 bottom rows pre-filled and a new block falling from above, "
        "simulate both the block drop AND line clearing. The new block will hard-drop to the bottom.\n\n"
        "Show the complete sequence: (1) new block falls and locks, (2) check for complete lines, "
        "(3) if lines are cleared, animate the elimination: flash the cleared row(s), remove them, "
        "and show blocks above falling down.",
    ],
}


def get_prompt(task_type: str = "default", difficulty: str = "easy", map_size: int = 5) -> str:
    """
    Select a prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        difficulty: Difficulty level (easy/medium/hard)
        map_size: Map size (5 or 10)
        
    Returns:
        Formatted prompt string
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    prompt_template = prompts[0] if prompts else PROMPTS["default"][0]
    
    return prompt_template.format(n=map_size, difficulty=difficulty)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])
