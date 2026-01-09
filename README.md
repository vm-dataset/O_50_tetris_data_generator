# Tetris Task Data Generator 🎮

A data generator for creating Tetris line-clearing reasoning tasks. Generates initial and final board states with prompts for video model evaluation, following the VMEvalKit framework.

Repository: [O_50_tetris_data_generator](https://github.com/vm-dataset/O_50_tetris_data_generator)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/O_50_tetris_data_generator.git
cd O_50_tetris_data_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python3 examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
tetris-task-data-generator/
├── core/                    # ✅ KEEP: Standard utilities
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # ⚠️ CUSTOMIZE: Tetris task logic
│   ├── generator.py        # Tetris task generator
│   ├── prompts.py          # Tetris prompt templates
│   ├── config.py           # Tetris configuration
│   └── tetris_core.py      # Tetris game logic
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Every generator produces:

```
data/questions/tetris_task/{task_id}/
├── first_frame.png          # Initial state (REQUIRED)
├── final_frame.png          # Goal state after line clearing (REQUIRED)
├── prompt.txt               # Instructions (REQUIRED)
└── ground_truth.mp4         # Solution video (OPTIONAL)
```

---

## 🎨 Customization

This generator implements a **Tetris line-clearing task** based on the [VMEvalKit template](https://github.com/vm-dataset/template-data-generator).

### Task Overview

- **Input**: Tetris board with pre-filled bottom rows and a falling block
- **Output**: Board state after line clearing and gravity application
- **Goal**: Evaluate video models' discrete grid dynamics reasoning

### Difficulty Levels

| Difficulty | Map Size | Features |
|------------|----------|----------|
| **Easy** | 5×5 | 2 bottom rows pre-filled, static |
| **Medium** | 10×10 | 3 bottom rows pre-filled, static |
| **Hard** | 10×10 | 3 bottom rows + new block drop, dynamic |

### Key Components

1. **`src/generator.py`** - Implements the Tetris task generator
2. **`src/prompts.py`** - Tetris-specific prompt templates
3. **`src/config.py`** - Tetris task configuration (map size, difficulty, etc.)
4. **`src/tetris_core.py`** - Core Tetris game logic (blocks, map, line clearing)

---

## 🔧 Usage

### Basic Generation

```bash
# Generate 10 easy tasks (5×5 map)
python3 examples/generate.py --num-samples 10 --difficulty easy

# Generate 50 medium tasks (10×10 map)
python3 examples/generate.py --num-samples 50 --difficulty medium

# Generate 100 hard tasks (10×10 map with dynamic blocks)
python3 examples/generate.py --num-samples 100 --difficulty hard
```

### Advanced Options

```bash
# Custom output directory
python3 examples/generate.py --num-samples 20 --output data/my_tasks

# Disable video generation (faster)
python3 examples/generate.py --num-samples 50 --no-videos

# Use random seed for reproducibility
python3 examples/generate.py --num-samples 100 --seed 42

# Custom map size
python3 examples/generate.py --num-samples 10 --map-size 10
```

---

## 🎯 VMEvalKit Integration

This generator produces data compatible with the VMEvalKit framework:

- **Image Format**: 400×400px PNG (40px per cell)
- **Color Scheme**: Standard Tetris colors (I/O/T/S/Z/J/L blocks)
- **Video Format**: MP4, 10fps, 60 frames
- **Prompt Template**: Aligned with VMEvalKit PROMPTS specification

---

## 🔧 Requirements

- Python 3.8+
- Pillow (PIL)
- NumPy
- OpenCV (cv2)
- Pydantic

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

This project is based on the [template-data-generator](https://github.com/vm-dataset/template-data-generator) template. For contributing guidelines and framework details, please refer to the template repository.
