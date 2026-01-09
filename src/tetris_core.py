"""
Tetris core game logic - Block shapes, map, and game rules.
Based on VMEvalKit's tetris_task implementation.
"""

import random
from typing import List, Tuple, Optional
from enum import Enum
from PIL import Image, ImageDraw


# Cell size for rendering (40px per cell, standard for 400x400 images)
CELL_SIZE = 40

# Color mapping for Tetris shapes
COLORS = {
    "I": (0, 255, 255),      # Cyan
    "O": (255, 255, 0),      # Yellow
    "T": (128, 0, 128),      # Purple
    "S": (0, 255, 0),        # Green
    "Z": (255, 0, 0),        # Red
    "J": (0, 0, 255),        # Blue
    "L": (255, 165, 0),      # Orange
    0: (30, 30, 30),         # Dark gray for empty
}


class TetrisShape(Enum):
    """Tetromino shapes."""
    I = "I"
    O = "O"
    T = "T"
    S = "S"
    Z = "Z"
    J = "J"
    L = "L"


class TetrisBlock:
    """Represents a Tetris block (Tetromino) with shape and position."""
    
    # Shape definitions: list of rotations, each rotation is list of (dx, dy) offsets
    SHAPES = {
        TetrisShape.I: [
            [(0, 0), (0, 1), (0, 2), (0, 3)],  # Horizontal
            [(0, 0), (1, 0), (2, 0), (3, 0)],  # Vertical
        ],
        TetrisShape.O: [
            [(0, 0), (0, 1), (1, 0), (1, 1)],  # Square (only 1 rotation)
        ],
        TetrisShape.T: [
            [(0, 1), (1, 0), (1, 1), (1, 2)],  # T pointing up
            [(0, 1), (1, 1), (1, 2), (2, 1)],  # T pointing right
            [(1, 0), (1, 1), (1, 2), (2, 1)],  # T pointing down
            [(0, 1), (1, 0), (1, 1), (2, 1)],  # T pointing left
        ],
        TetrisShape.S: [
            [(0, 1), (0, 2), (1, 0), (1, 1)],  # S horizontal
            [(0, 0), (1, 0), (1, 1), (2, 1)],  # S vertical
        ],
        TetrisShape.Z: [
            [(0, 0), (0, 1), (1, 1), (1, 2)],  # Z horizontal
            [(0, 1), (1, 0), (1, 1), (2, 0)],  # Z vertical
        ],
        TetrisShape.J: [
            [(0, 0), (1, 0), (1, 1), (1, 2)],  # J pointing up
            [(0, 1), (0, 2), (1, 1), (2, 1)],  # J pointing right
            [(1, 0), (1, 1), (1, 2), (2, 2)],  # J pointing down
            [(0, 1), (1, 1), (2, 0), (2, 1)],  # J pointing left
        ],
        TetrisShape.L: [
            [(0, 2), (1, 0), (1, 1), (1, 2)],  # L pointing up
            [(0, 1), (1, 1), (2, 1), (2, 2)],  # L pointing right
            [(1, 0), (1, 1), (1, 2), (2, 0)],  # L pointing down
            [(0, 0), (0, 1), (1, 1), (2, 1)],  # L pointing left
        ],
    }
    
    def __init__(self, shape: TetrisShape, x: int = 0, y: int = 0):
        self.shape = shape
        self.x = x  # Row position
        self.y = y  # Column position
        self.rotation = 0  # Current rotation index
    
    def get_coordinates(self) -> List[Tuple[int, int]]:
        """Get absolute coordinates of all blocks in this piece."""
        shape_coords = self.SHAPES[self.shape][self.rotation]
        return [(self.x + dx, self.y + dy) for dx, dy in shape_coords]
    
    def rotate_clockwise(self):
        """Rotate 90 degrees clockwise."""
        max_rotation = len(self.SHAPES[self.shape])
        self.rotation = (self.rotation + 1) % max_rotation
    
    def rotate_counterclockwise(self):
        """Rotate 90 degrees counterclockwise."""
        max_rotation = len(self.SHAPES[self.shape])
        self.rotation = (self.rotation - 1) % max_rotation
    
    def move(self, dx: int, dy: int):
        """Move block by offset."""
        self.x += dx
        self.y += dy
    
    def copy(self):
        """Create a copy of this block."""
        new_block = TetrisBlock(self.shape, self.x, self.y)
        new_block.rotation = self.rotation
        return new_block
    
    @staticmethod
    def get_random_shape() -> TetrisShape:
        """Get a random Tetris shape."""
        return random.choice(list(TetrisShape))


class TetrisMap:
    """Tetris game map with grid and game logic."""
    
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.current_block: Optional[TetrisBlock] = None
        self.score = 0
        self.lines_cleared = 0
    
    def is_valid_position(self, block: TetrisBlock) -> bool:
        """Check if block position is valid (no collisions, within bounds)."""
        for x, y in block.get_coordinates():
            if x < 0 or x >= self.height or y < 0 or y >= self.width:
                return False
            if self.grid[x][y] != 0:
                return False
        return True
    
    def place_block(self, block: TetrisBlock):
        """Place block on the grid (lock it in place)."""
        for x, y in block.get_coordinates():
            if 0 <= x < self.height and 0 <= y < self.width:
                self.grid[x][y] = block.shape.value
    
    def spawn_new_block(self) -> bool:
        """Spawn a new block at the top center."""
        shape = TetrisBlock.get_random_shape()
        self.current_block = TetrisBlock(shape, x=0, y=self.width // 2 - 1)
        
        if not self.is_valid_position(self.current_block):
            return False
        return True
    
    def move_block_down(self) -> bool:
        """Move current block down one row. Returns False if blocked."""
        if self.current_block is None:
            return False
        
        temp_block = self.current_block.copy()
        temp_block.move(1, 0)
        
        if self.is_valid_position(temp_block):
            self.current_block = temp_block
            return True
        else:
            # Block can't move down, lock it in place
            self.place_block(self.current_block)
            self.current_block = None
            self.clear_lines()
            return False
    
    def move_block_left(self) -> bool:
        """Move current block left."""
        if self.current_block is None:
            return False
        
        temp_block = self.current_block.copy()
        temp_block.move(0, -1)
        
        if self.is_valid_position(temp_block):
            self.current_block = temp_block
            return True
        return False
    
    def move_block_right(self) -> bool:
        """Move current block right."""
        if self.current_block is None:
            return False
        
        temp_block = self.current_block.copy()
        temp_block.move(0, 1)
        
        if self.is_valid_position(temp_block):
            self.current_block = temp_block
            return True
        return False
    
    def rotate_block(self) -> bool:
        """Rotate current block clockwise."""
        if self.current_block is None:
            return False
        
        temp_block = self.current_block.copy()
        temp_block.rotate_clockwise()
        
        if self.is_valid_position(temp_block):
            self.current_block = temp_block
            return True
        return False
    
    def clear_lines(self) -> int:
        """Clear all full lines and apply gravity. Returns number of lines cleared."""
        lines_to_clear = []
        for i in range(self.height):
            if all(self.grid[i][j] != 0 for j in range(self.width)):
                lines_to_clear.append(i)
        
        if lines_to_clear:
            # Remove full lines
            new_grid = []
            for i in range(self.height):
                if i not in lines_to_clear:
                    new_grid.append(self.grid[i])
            
            # Add empty lines at the top
            num_cleared = len(lines_to_clear)
            for _ in range(num_cleared):
                new_grid.insert(0, [0 for _ in range(self.width)])
            
            self.grid = new_grid
            self.lines_cleared += num_cleared
            self.score += num_cleared * num_cleared * 100
            
            return num_cleared
        
        return 0
    
    def hard_drop(self):
        """Drop current block to the lowest valid position."""
        if self.current_block is None:
            return
        
        while self.move_block_down():
            pass
    
    def get_display_grid(self) -> List[List]:
        """Get grid with current block overlaid."""
        display = [row[:] for row in self.grid]
        
        if self.current_block:
            for x, y in self.current_block.get_coordinates():
                if 0 <= x < self.height and 0 <= y < self.width:
                    display[x][y] = self.current_block.shape.value
        
        return display
    
    def render_to_image(self, image_size: Tuple[int, int] = None) -> Image.Image:
        """Render the Tetris map to a PIL Image."""
        display = self.get_display_grid()
        h = len(display)
        w = len(display[0])
        
        if image_size is None:
            img = Image.new("RGB", (w * CELL_SIZE, h * CELL_SIZE), (0, 0, 0))
            cell_size_w = CELL_SIZE
        else:
            img = Image.new("RGB", image_size, (0, 0, 0))
            # Calculate cell size to fit image
            cell_w = image_size[0] // w
            cell_h = image_size[1] // h
            cell_size_w = min(cell_w, cell_h)
        
        draw = ImageDraw.Draw(img)
        
        for x in range(h):
            for y in range(w):
                block = display[x][y]
                color = COLORS.get(block, (100, 100, 100))
                
                # Draw cell
                x0 = y * cell_size_w
                y0 = x * cell_size_w
                x1 = x0 + cell_size_w
                y1 = y0 + cell_size_w
                
                draw.rectangle(
                    [x0, y0, x1, y1],
                    fill=color,
                    outline=(50, 50, 50),
                    width=2
                )
        
        return img
    
    def initialize_with_random_blocks(
        self,
        max_blocks: int = 7,
        max_height: int = 3,
        strategy: str = "mixed"
    ):
        """
        Initialize the bottom of the map with blocks.
        
        Args:
            max_blocks: Maximum number of blocks to generate
            max_height: Max number of bottom rows to use
            strategy: "random", "flat", or "mixed"
        """
        if strategy == "mixed":
            use_flat = random.random() < 0.7
        elif strategy == "flat":
            use_flat = True
        else:
            use_flat = False
        
        if use_flat:
            self._initialize_flat_bottom(max_height)
        else:
            self._initialize_random_drop(max_blocks, max_height)
    
    def _initialize_flat_bottom(self, max_height: int = 3):
        """Flat-fill strategy: create bottom rows close to clearing."""
        num_rows_to_fill = random.randint(1, min(2, max_height))
        
        gap_positions_per_row = []
        
        for row_offset in range(num_rows_to_fill):
            row = self.height - 1 - row_offset
            
            if row_offset == 0:
                num_gaps = random.randint(1, 2)
                gap_positions = random.sample(range(self.width), num_gaps)
            else:
                previous_all_gaps = set()
                for prev_gaps in gap_positions_per_row:
                    previous_all_gaps.update(prev_gaps)
                
                gap_positions = list(previous_all_gaps)
                remaining_cols = [c for c in range(self.width) if c not in gap_positions]
                if remaining_cols and random.random() < 0.3:
                    extra_gaps = random.randint(1, min(1, len(remaining_cols)))
                    gap_positions.extend(random.sample(remaining_cols, extra_gaps))
            
            gap_positions_per_row.append(gap_positions)
            
            shapes = list(TetrisShape)
            for col in range(self.width):
                if col not in gap_positions:
                    self.grid[row][col] = random.choice(shapes).value
        
        # Place some blocks on third row if supported
        if max_height >= 3:
            third_row = self.height - 3
            supported_positions = []
            for col in range(self.width):
                is_fully_supported = True
                for check_row in range(third_row + 1, self.height):
                    if self.grid[check_row][col] == 0:
                        is_fully_supported = False
                        break
                if is_fully_supported:
                    supported_positions.append(col)
            
            if supported_positions:
                num_blocks_third_row = random.randint(0, min(len(supported_positions), self.width // 2))
                if num_blocks_third_row > 0:
                    positions = random.sample(supported_positions, num_blocks_third_row)
                    shapes = list(TetrisShape)
                    for col in positions:
                        self.grid[third_row][col] = random.choice(shapes).value
    
    def _initialize_random_drop(self, max_blocks: int, max_height: int):
        """Random-drop strategy: simulate natural falling."""
        num_blocks = random.randint(1, max_blocks)
        placed_blocks = 0
        attempts = 0
        max_attempts = max_blocks * 20
        
        while placed_blocks < num_blocks and attempts < max_attempts:
            attempts += 1
            
            shape = TetrisBlock.get_random_shape()
            block = TetrisBlock(shape, x=0, y=0)
            
            num_rotations = random.randint(0, len(TetrisBlock.SHAPES[shape]) - 1)
            for _ in range(num_rotations):
                block.rotate_clockwise()
            
            y_pos = random.randint(0, self.width - 1)
            block.x = 0
            block.y = y_pos
            
            coords = block.get_coordinates()
            min_y = min(dy for _, dy in coords)
            max_y = max(dy for _, dy in coords)
            if min_y < 0:
                block.y -= min_y
            if max_y >= self.width:
                block.y -= (max_y - self.width + 1)
            
            final_x = 0
            for x in range(self.height):
                block.x = x
                coords = block.get_coordinates()
                max_block_x = max(bx for bx, _ in coords)
                if max_block_x >= self.height:
                    continue
                
                collision = False
                for bx, by in coords:
                    if bx < 0 or bx >= self.height or by < 0 or by >= self.width:
                        collision = True
                        break
                    if self.grid[bx][by] != 0:
                        collision = True
                        break
                
                if not collision:
                    final_x = x
                else:
                    break
            
            block.x = final_x
            coords = block.get_coordinates()
            
            min_allowed_row = self.height - max_height
            if all(bx >= min_allowed_row for bx, _ in coords):
                valid = True
                for bx, by in coords:
                    if bx < 0 or bx >= self.height or by < 0 or by >= self.width:
                        valid = False
                        break
                    if self.grid[bx][by] != 0:
                        valid = False
                        break
                
                if valid:
                    self.place_block(block)
                    placed_blocks += 1
        
        return placed_blocks


def smart_fill_bottom_rows(
    tetris_map: TetrisMap,
    num_rows: int,
    fill_ratio: float,
    guarantee_clear: Optional[bool] = None
):
    """
    Smart fill bottom rows ensuring no floating blocks.
    
    Args:
        tetris_map: Tetris map object
        num_rows: Number of rows to fill
        fill_ratio: Fill ratio for each row (0.0-1.0)
        guarantee_clear: True=guarantee clear, False=guarantee no clear, None=random
    """
    n = tetris_map.width
    shapes = list(TetrisShape)
    
    # Decide which rows will be full
    if guarantee_clear is True:
        num_full_lines = random.randint(1, max(1, num_rows // 2))
        full_line_indices = random.sample(range(num_rows), num_full_lines)
    elif guarantee_clear is False:
        full_line_indices = []
    else:
        full_line_indices = []
        if fill_ratio >= 0.95 and random.random() < 0.5:
            num_full_lines = random.randint(1, max(1, num_rows // 3))
            full_line_indices = random.sample(range(num_rows), num_full_lines)
    
    # Fill from bottom up
    for i in range(num_rows):
        row_idx = tetris_map.height - 1 - i
        
        if i in full_line_indices:
            # Full line case
            if i == 0:
                for col in range(n):
                    tetris_map.grid[row_idx][col] = random.choice(shapes).value
            else:
                row_below = tetris_map.height - i
                supported_cols = [col for col in range(n) if tetris_map.grid[row_below][col] != 0]
                
                if len(supported_cols) == n:
                    for col in range(n):
                        tetris_map.grid[row_idx][col] = random.choice(shapes).value
                else:
                    if len(supported_cols) > 0:
                        for col in supported_cols:
                            tetris_map.grid[row_idx][col] = random.choice(shapes).value
        else:
            # Non-full line case
            if guarantee_clear is False:
                num_filled = random.randint(int(n * fill_ratio * 0.7), n - 1)
            else:
                num_filled = int(n * fill_ratio + random.uniform(-0.2, 0.2) * n)
                num_filled = max(0, min(n - 1, num_filled))
            
            if i == 0:
                positions = random.sample(range(n), num_filled)
                for col in positions:
                    tetris_map.grid[row_idx][col] = random.choice(shapes).value
            else:
                row_below = tetris_map.height - i
                supported_cols = [col for col in range(n) if tetris_map.grid[row_below][col] != 0]
                
                if not supported_cols:
                    continue
                
                actual_num_filled = min(num_filled, len(supported_cols))
                if actual_num_filled > 0:
                    positions = random.sample(supported_cols, actual_num_filled)
                    for col in positions:
                        tetris_map.grid[row_idx][col] = random.choice(shapes).value

