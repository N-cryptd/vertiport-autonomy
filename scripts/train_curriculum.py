#!/usr/bin/env python3
"""Curriculum training script entry point for vertiport autonomy."""

import argparse
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vertiport_autonomy.training.curriculum import CurriculumTrainer


def main():
    """Curriculum training entry point."""
    parser = argparse.ArgumentParser(
        description="Train a vertiport autonomy agent using curriculum learning"
    )
    parser.add_argument(
        "--log-dir", type=str, default="logs", help="Directory for training logs"
    )
    parser.add_argument(
        "--model-dir", type=str, default="models", help="Directory for saving models"
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=["easy_world", "intermediate_world", "hard_world", "all"],
        default="all",
        help="Which curriculum phase to run ('all' for full curriculum)",
    )
    parser.add_argument(
        "--easy-steps", type=int, default=2000000, help="Training steps for easy phase"
    )
    parser.add_argument(
        "--intermediate-steps",
        type=int,
        default=3000000,
        help="Training steps for intermediate phase",
    )
    parser.add_argument(
        "--hard-steps", type=int, default=5000000, help="Training steps for hard phase"
    )

    args = parser.parse_args()

    # Create trainer
    trainer = CurriculumTrainer(log_dir=args.log_dir, model_dir=args.model_dir)

    # Customize phases if step counts provided
    if any(
        [
            args.easy_steps != 2000000,
            args.intermediate_steps != 3000000,
            args.hard_steps != 5000000,
        ]
    ):
        custom_phases = trainer.phases.copy()
        custom_phases[0]["timesteps"] = args.easy_steps
        custom_phases[1]["timesteps"] = args.intermediate_steps
        custom_phases[2]["timesteps"] = args.hard_steps
        trainer.set_custom_phases(custom_phases)

    # Run training
    if args.phase == "all":
        print("🎓 Running full curriculum...")
        final_model = trainer.run_full_curriculum()
    else:
        print(f"🎓 Running single phase: {args.phase}")
        final_model = trainer.run_single_phase(args.phase)

    print("Curriculum training complete! 🚁")


if __name__ == "__main__":
    main()
