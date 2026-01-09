#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           TASK GENERATION SCRIPT                              ║
║                                                                               ║
║  Run this to generate your dataset.                                           ║
║  Customize TaskConfig and TaskGenerator in src/ for your task.                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 examples/generate.py --num-samples 100
    python3 examples/generate.py --num-samples 100 --output data/my_task --seed 42
    python3 examples/generate.py --num-samples 10 --difficulty easy
    python3 examples/generate.py --num-samples 10 --difficulty medium
    python3 examples/generate.py --num-samples 10 --difficulty hard
"""

import argparse
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import OutputWriter
from src import TaskGenerator, TaskConfig


def main():
    parser = argparse.ArgumentParser(
        description="Generate task dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python examples/generate.py --num-samples 10
    python examples/generate.py --num-samples 100 --output data/output --seed 42
        """
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        required=True,
        help="Number of task samples to generate"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/questions",
        help="Output directory (default: data/questions)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--no-videos",
        action="store_true",
        help="Disable video generation"
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard"],
        default="easy",
        help="Task difficulty level (default: easy)"
    )
    parser.add_argument(
        "--map-size",
        type=int,
        choices=[5, 10],
        default=None,
        help="Map size (5 for easy, 10 for medium/hard). Auto-set based on difficulty if not specified."
    )
    
    args = parser.parse_args()
    
    print(f"🎲 Generating {args.num_samples} {args.difficulty} difficulty tasks...")
    
    # ──────────────────────────────────────────────────────────────────────────
    #  Configure Tetris task
    # ──────────────────────────────────────────────────────────────────────────
    
    # Auto-set map size based on difficulty
    if args.map_size is None:
        if args.difficulty == "easy":
            map_size = 5
        else:
            map_size = 10
    else:
        map_size = args.map_size
    
    # Set number of initial rows
    if args.difficulty == "easy":
        num_init_rows = 2
    else:
        num_init_rows = 3
    
    config = TaskConfig(
        num_samples=args.num_samples,
        random_seed=args.seed,
        output_dir=Path(args.output),
        generate_videos=not args.no_videos,
        difficulty=args.difficulty,
        domain="tetris",
        map_width=map_size,
        map_height=map_size,
        num_init_rows=num_init_rows,
    )
    
    # Generate tasks
    generator = TaskGenerator(config)
    tasks = generator.generate_dataset()
    
    # Write to disk
    writer = OutputWriter(Path(args.output))
    writer.write_dataset(tasks)
    
    print(f"✅ Done! Generated {len(tasks)} tasks in {args.output}/{config.domain}_task/")


if __name__ == "__main__":
    main()
