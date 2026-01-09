"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           TETRIS TASK GENERATOR                               ║
║                                                                               ║
║  Generates Tetris line-clearing reasoning tasks with initial and final states.║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
import copy
from pathlib import Path
from typing import Optional
from PIL import Image

from core import BaseGenerator, TaskPair
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt
from .tetris_core import (
    TetrisMap,
    TetrisBlock,
    TetrisShape,
    smart_fill_bottom_rows
)


class TaskGenerator(BaseGenerator):
    """
    Tetris task generator.
    
    Generates task pairs with:
    - Initial state: Tetris board with pre-filled bottom rows (and optionally a falling block)
    - Final state: Board after line clearing and gravity
    - Prompt: Instructions for the video model
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.tetris_map = TetrisMap(width=config.map_width, height=config.map_height)
        
        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one Tetris task pair."""
        
        # Reset map for each task
        self.tetris_map = TetrisMap(
            width=self.config.map_width,
            height=self.config.map_height
        )
        
        # Determine difficulty-based settings
        difficulty = self.config.difficulty or "easy"
        
        # For random mode (guarantee_clear=None), ensure at least some tasks have line clears
        # Use task_id to determine: roughly 70% will have line clears
        effective_guarantee_clear = self.config.guarantee_clear
        if effective_guarantee_clear is None:
            # Extract number from task_id (e.g., "tetris_0042" -> 42)
            try:
                task_num = int(task_id.split('_')[-1])
                # 70% chance to guarantee clear
                effective_guarantee_clear = (task_num % 10) < 7
            except (ValueError, IndexError):
                # Fallback: random choice
                effective_guarantee_clear = random.random() < 0.7
        
        # Temporarily override guarantee_clear for this task
        original_guarantee_clear = self.config.guarantee_clear
        self.config.guarantee_clear = effective_guarantee_clear
        
        # Generate task, retry if first and final are identical
        max_retries = 10
        task_data = None
        
        for retry in range(max_retries):
            try:
                if difficulty == "easy":
                    task_data = self._generate_easy_task()
                elif difficulty == "medium":
                    task_data = self._generate_medium_task()
                elif difficulty == "hard":
                    task_data = self._generate_hard_task()
                else:
                    # Default to easy
                    task_data = self._generate_easy_task()
            finally:
                # Restore original guarantee_clear
                self.config.guarantee_clear = original_guarantee_clear
            
            # Check if images are different
            first_image = task_data["first_image"]
            final_image = task_data["final_image"]
            
            import numpy as np
            img1_array = np.array(first_image)
            img2_array = np.array(final_image)
            images_different = np.any(img1_array != img2_array)
            
            if images_different:
                # Success! Images are different
                break
            else:
                # Images are same, retry with guarantee_clear=True
                if retry < max_retries - 1:
                    print(f"  ⚠️  {task_id}: first and final are identical, regenerating... (attempt {retry + 1}/{max_retries})")
                    self.config.guarantee_clear = True
                    # Reset map for retry
                    self.tetris_map = TetrisMap(
                        width=self.config.map_width,
                        height=self.config.map_height
                    )
                else:
                    print(f"  ⚠️  {task_id}: reached max retries, using current result")
        
        # Restore original guarantee_clear
        self.config.guarantee_clear = original_guarantee_clear
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(
                first_image, final_image, task_id, task_data
            )
        
        # Get prompt
        prompt = get_prompt(
            task_type="default",
            difficulty=difficulty,
            map_size=self.config.map_width
        )
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK GENERATION METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_easy_task(self) -> dict:
        """Generate easy task: 5x5 map, 2 rows, static line clearing."""
        # Fill bottom rows
        smart_fill_bottom_rows(
            self.tetris_map,
            num_rows=self.config.num_init_rows,
            fill_ratio=self.config.fill_ratio,
            guarantee_clear=self.config.guarantee_clear
        )
        
        # Save initial grid state before clearing
        initial_grid = copy.deepcopy(self.tetris_map.grid)
        
        # Render initial state
        first_image = self.tetris_map.render_to_image(self.config.image_size)
        
        # Clear lines
        lines_cleared = self.tetris_map.clear_lines()
        
        # If guarantee_clear is True but no lines cleared, retry
        if lines_cleared == 0 and self.config.guarantee_clear is True:
            # Retry once to ensure we have a line clear
            self.tetris_map = TetrisMap(
                width=self.config.map_width,
                height=self.config.map_height
            )
            smart_fill_bottom_rows(
                self.tetris_map,
                num_rows=self.config.num_init_rows,
                fill_ratio=self.config.fill_ratio,
                guarantee_clear=True  # Force at least one line to clear
            )
            initial_grid = copy.deepcopy(self.tetris_map.grid)
            first_image = self.tetris_map.render_to_image(self.config.image_size)
            lines_cleared = self.tetris_map.clear_lines()
        
        # Render final state
        final_image = self.tetris_map.render_to_image(self.config.image_size)
        
        return {
            "first_image": first_image,
            "final_image": final_image,
            "lines_cleared": lines_cleared,
            "difficulty": "easy",
            "initial_grid": initial_grid,
            "final_grid": copy.deepcopy(self.tetris_map.grid)
        }
    
    def _generate_medium_task(self) -> dict:
        """Generate medium task: 10x10 map, 3 rows, static line clearing."""
        # Ensure map size is 10x10
        if self.config.map_width != 10 or self.config.map_height != 10:
            self.tetris_map = TetrisMap(width=10, height=10)
        
        # Fill bottom rows
        smart_fill_bottom_rows(
            self.tetris_map,
            num_rows=3,
            fill_ratio=self.config.fill_ratio,
            guarantee_clear=self.config.guarantee_clear
        )
        
        # Save initial grid state
        initial_grid = copy.deepcopy(self.tetris_map.grid)
        
        # Render initial state
        first_image = self.tetris_map.render_to_image(self.config.image_size)
        
        # Clear lines
        lines_cleared = self.tetris_map.clear_lines()
        
        # If guarantee_clear is True but no lines cleared, retry
        if lines_cleared == 0 and self.config.guarantee_clear is True:
            self.tetris_map = TetrisMap(width=10, height=10)
            smart_fill_bottom_rows(
                self.tetris_map,
                num_rows=3,
                fill_ratio=self.config.fill_ratio,
                guarantee_clear=True
            )
            initial_grid = copy.deepcopy(self.tetris_map.grid)
            first_image = self.tetris_map.render_to_image(self.config.image_size)
            lines_cleared = self.tetris_map.clear_lines()
        
        # Render final state
        final_image = self.tetris_map.render_to_image(self.config.image_size)
        
        return {
            "first_image": first_image,
            "final_image": final_image,
            "lines_cleared": lines_cleared,
            "difficulty": "medium",
            "initial_grid": initial_grid,
            "final_grid": copy.deepcopy(self.tetris_map.grid)
        }
    
    def _generate_hard_task(self) -> dict:
        """Generate hard task: 10x10 map, 3 rows, new block drop + line clearing."""
        # Ensure map size is 10x10
        if self.config.map_width != 10 or self.config.map_height != 10:
            self.tetris_map = TetrisMap(width=10, height=10)
        
        # Fill bottom rows (guarantee no complete lines initially)
        smart_fill_bottom_rows(
            self.tetris_map,
            num_rows=3,
            fill_ratio=0.85,
            guarantee_clear=False  # Hard tasks: no initial clears
        )
        
        # Clear any complete lines that might have been created
        self.tetris_map.clear_lines()
        
        # Save initial grid state (before block drop)
        initial_grid = copy.deepcopy(self.tetris_map.grid)
        
        # Render initial state (before block drop)
        first_image = self.tetris_map.render_to_image(self.config.image_size)
        
        # Spawn and drop new block
        lines_before = self.tetris_map.lines_cleared
        
        # Try to spawn a block
        spawn_success = False
        new_block_shape = None
        all_shapes = list(TetrisShape)
        
        for _ in range(len(all_shapes) * 3):
            shape = random.choice(all_shapes)
            col = random.randint(0, self.tetris_map.width - 1)
            
            test_block = TetrisBlock(shape, x=0, y=col)
            if self.tetris_map.is_valid_position(test_block):
                self.tetris_map.current_block = test_block
                new_block_shape = shape.value
                spawn_success = True
                break
        
        if not spawn_success:
            # Fallback: use I block at center
            fallback_col = self.tetris_map.width // 2 - 1
            self.tetris_map.current_block = TetrisBlock(TetrisShape.I, x=0, y=fallback_col)
            new_block_shape = TetrisShape.I.value
        
        # Hard drop the block (this will set current_block to None after placement)
        self.tetris_map.hard_drop()
        
        # Calculate lines cleared by the new block
        lines_after = self.tetris_map.lines_cleared
        lines_cleared_by_block = lines_after - lines_before
        
        # Render final state
        final_image = self.tetris_map.render_to_image(self.config.image_size)
        
        return {
            "first_image": first_image,
            "final_image": final_image,
            "lines_cleared": lines_cleared_by_block,
            "difficulty": "hard",
            "new_block_shape": new_block_shape,
            "initial_grid": initial_grid,
            "final_grid": copy.deepcopy(self.tetris_map.grid)
        }
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        task_data: dict
    ) -> Optional[str]:
        """Generate ground truth video showing line clearing animation."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_tetris_animation_frames(
            first_image, final_image, task_data
        )
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_tetris_animation_frames(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_data: dict,
        hold_frames: int = 15,
        flash_frames: int = 10,
        clear_frames: int = 20,
        transition_frames: int = 50
    ) -> list:
        """
        Create animation frames for Tetris line clearing.
        
        Shows: initial state -> line flash -> clearing -> gravity -> final state
        Always ensures smooth transition from first to final frame.
        """
        from PIL import ImageEnhance
        frames = []
        
        lines_cleared = task_data.get("lines_cleared", 0)
        initial_grid = task_data.get("initial_grid")
        final_grid = task_data.get("final_grid")
        
        # Check if images are actually different
        import numpy as np
        img1_array = np.array(first_image)
        img2_array = np.array(final_image)
        images_different = np.any(img1_array != img2_array)
        
        # Hold initial position
        for _ in range(hold_frames):
            frames.append(first_image.copy())
        
        # If lines are cleared, show detailed animation
        if lines_cleared > 0 and initial_grid and final_grid and images_different:
            # Step 1: Flash the lines that will be cleared
            for i in range(flash_frames):
                flash_img = first_image.copy()
                # Make it brighter to show flash effect
                enhancer = ImageEnhance.Brightness(flash_img)
                flash_factor = 1.0 + 0.3 * (1.0 if i % 2 == 0 else 0.0)  # Alternating flash
                flash_img = enhancer.enhance(flash_factor)
                frames.append(flash_img)
            
            # Step 2: Show clearing (fade out the cleared lines)
            for i in range(clear_frames):
                progress = i / (clear_frames - 1) if clear_frames > 1 else 1.0
                # Blend from first to final, showing the clearing
                alpha = progress
                frame = Image.blend(first_image, final_image, alpha)
                frames.append(frame)
        else:
            # Even if no lines cleared or images are same, show smooth transition
            # This ensures video always has movement from first to final
            if not images_different:
                # If images are identical, create animation effect
                # This should rarely happen, but ensures video is never static
                
                # Hold at start
                for i in range(hold_frames):
                    frames.append(first_image.copy())
                
                # Create animation with brightness variation
                # This simulates "processing" or "thinking" effect
                # Use many frames to ensure visible animation (at least 30+ frames total)
                for i in range(transition_frames):
                    progress = i / (transition_frames - 1) if transition_frames > 1 else 1.0
                    frame = first_image.copy()
                    enhancer = ImageEnhance.Brightness(frame)
                    # Brightness animation: 1.0 -> 1.2 -> 1.0 (visible pulse)
                    brightness = 1.0 + 0.2 * (1.0 - abs(progress - 0.5) * 2)
                    frame = enhancer.enhance(brightness)
                    frames.append(frame)
                
                # Hold before final
                for i in range(hold_frames):
                    frames.append(first_image.copy())
            else:
                # Images are different but no lines cleared (shouldn't happen often)
                # Show smooth transition from first to final
                for i in range(transition_frames):
                    progress = i / (transition_frames - 1) if transition_frames > 1 else 1.0
                    # Smooth blend from first to final
                    frame = Image.blend(first_image, final_image, progress)
                    frames.append(frame)
        
        # Hold final position
        for _ in range(hold_frames):
            frames.append(final_image.copy())
        
        # Ensure minimum frame count for smooth animation (at least 30 frames)
        min_frames = 30
        if len(frames) < min_frames:
            # If we have too few frames, add more transition frames
            additional_frames = min_frames - len(frames)
            if images_different:
                # Add more blend frames
                for i in range(additional_frames):
                    progress = (i + 1) / (additional_frames + 1)
                    frame = Image.blend(first_image, final_image, progress)
                    # Insert before final hold
                    frames.insert(-hold_frames, frame)
            else:
                # Add more brightness variation frames
                for i in range(additional_frames):
                    progress = (i + 1) / (additional_frames + 1)
                    frame = first_image.copy()
                    enhancer = ImageEnhance.Brightness(frame)
                    brightness = 1.0 + 0.15 * (1.0 - abs(progress - 0.5) * 2)
                    frame = enhancer.enhance(brightness)
                    # Insert before final hold
                    frames.insert(-hold_frames, frame)
        
        return frames
