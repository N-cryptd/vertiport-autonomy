#!/usr/bin/env python3
"""Training script entry point for vertiport autonomy."""

import argparse
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vertiport_autonomy.training.trainer import Trainer


def main():
    """Main training entry point."""
    parser = argparse.ArgumentParser(description="Train a vertiport autonomy agent")
    parser.add_argument(
        "--scenario",
        type=str,
        default="scenarios/steady_flow.yaml",
        help="Path to scenario configuration file",
    )
    parser.add_argument(
        "--timesteps", type=int, default=5000000, help="Total training timesteps"
    )
    parser.add_argument(
        "--n-envs", type=int, default=50, help="Number of parallel environments"
    )
    parser.add_argument(
        "--log-dir", type=str, default="logs", help="Directory for training logs"
    )
    parser.add_argument(
        "--model-dir", type=str, default="models", help="Directory for saving models"
    )
    parser.add_argument(
        "--learning-rate", type=float, default=1e-4, help="Learning rate for training"
    )
    parser.add_argument(
        "--batch-size", type=int, default=128, help="Batch size for training"
    )

    args = parser.parse_args()

    # Create trainer
    trainer = Trainer(
        log_dir=args.log_dir,
        model_dir=args.model_dir,
        n_envs=args.n_envs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
    )

    # Train the model
    model = trainer.train(scenario_path=args.scenario, total_timesteps=args.timesteps)

    print("Training complete!")


if __name__ == "__main__":
    main()
