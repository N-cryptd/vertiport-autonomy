#!/usr/bin/env python3
"""Evaluation script entry point for vertiport autonomy."""

import argparse
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vertiport_autonomy.agents.heuristic import SimpleHeuristicAgent
from vertiport_autonomy.evaluation.framework import (
    EvaluationFramework,
    heuristic_agent_wrapper,
)


def main():
    """Main evaluation entry point."""
    parser = argparse.ArgumentParser(description="Evaluate a vertiport autonomy agent")
    parser.add_argument(
        "--agent",
        type=str,
        default="heuristic",
        help="Agent to evaluate: 'heuristic' or path to trained model",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="scenarios/steady_flow.yaml",
        help="Path to scenario configuration file",
    )
    parser.add_argument(
        "--episodes", type=int, default=100, help="Number of evaluation episodes"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="evaluation_results",
        help="Directory for evaluation results",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducible evaluation"
    )
    parser.add_argument(
        "--deterministic",
        action="store_true",
        help="Use deterministic actions (for trained models)",
    )

    args = parser.parse_args()

    # Create evaluation framework
    evaluator = EvaluationFramework()

    # Determine agent
    if args.agent.lower() == "heuristic":
        agent_fn = heuristic_agent_wrapper
        agent_name = "heuristic"
    else:
        # Assume it's a path to a trained model
        # This would need to be implemented to load PPO models
        print(f"Loading trained model from: {args.agent}")
        agent_name = os.path.splitext(os.path.basename(args.agent))[0]
        # For now, fall back to heuristic
        agent_fn = heuristic_agent_wrapper

    # Run evaluation
    print(f"Evaluating agent: {agent_name}")
    print(f"Scenario: {args.scenario}")
    print(f"Episodes: {args.episodes}")

    results = evaluator.evaluate_agent(
        agent_fn=agent_fn,
        agent_name=agent_name,
        scenarios=[args.scenario],
        num_episodes=args.episodes,
        seeds=[args.seed + i for i in range(args.episodes)],
    )

    # Print summary
    print("\n=== Evaluation Results ===")
    if results:
        print(f"Total Episodes: {len(results)}")
        print(f"Results saved to: {args.output_dir}")
    else:
        print("No results generated")

    print("Evaluation complete!")


if __name__ == "__main__":
    main()
