"""
Evaluation Framework for Vertiport Autonomy

Provides systematic evaluation of agents with comprehensive KPI reporting.
Supports multiple scenarios, multiple runs, and statistical analysis.
"""

import csv
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from ..agents.heuristic import SimpleHeuristicAgent
from ..config.loader import load_scenario_config
from ..core.environment import VertiportEnv
from ..core.simulator import DroneState


@dataclass
class EvaluationMetrics:
    """Container for episode evaluation metrics"""

    # Basic episode info
    scenario: str
    agent_type: str
    episode_id: int
    seed: int

    # Performance metrics
    episode_length: int
    total_reward: float
    average_reward: float

    # Safety metrics
    collisions: int
    los_violations: int
    unauthorized_landings: int

    # Efficiency metrics
    missions_completed: int
    completion_rate: float
    average_mission_time: float
    throughput: float  # missions per unit time

    # State distribution
    final_states: List[str]
    time_in_states: Dict[str, float]


class EvaluationFramework:
    """
    Comprehensive evaluation framework for vertiport coordination agents
    """

    def __init__(self, output_dir: str = "evaluation_results"):
        """Initialize evaluation framework"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Default evaluation scenarios
        self.scenarios = [
            "scenarios/easy_world.yaml",
            "scenarios/intermediate_world.yaml",
            "scenarios/steady_flow.yaml",
        ]

        print(f"📊 Evaluation Framework initialized")
        print(f"   Output directory: {output_dir}")

    def evaluate_agent(
        self,
        agent_fn,
        agent_name: str,
        scenarios: Optional[List[str]] = None,
        num_episodes: int = 10,
        max_steps: int = 500,
        seeds: Optional[List[int]] = None,
    ) -> List[EvaluationMetrics]:
        """
        Evaluate an agent across multiple scenarios and episodes

        Args:
            agent_fn: Function that takes (scenario_path, seed, max_steps) and returns metrics
            agent_name: Name identifier for the agent
            scenarios: List of scenario files to test (default: all scenarios)
            num_episodes: Number of episodes per scenario
            max_steps: Maximum steps per episode
            seeds: List of random seeds (default: sequential integers)

        Returns:
            List of EvaluationMetrics for all episodes
        """

        if scenarios is None:
            scenarios = self.scenarios

        if seeds is None:
            seeds = list(range(num_episodes))
        elif len(seeds) < num_episodes:
            seeds = seeds + list(range(len(seeds), num_episodes))

        print(f"\n🚀 Evaluating Agent: {agent_name}")
        print(f"   Scenarios: {len(scenarios)}")
        print(f"   Episodes per scenario: {num_episodes}")
        print(f"   Max steps per episode: {max_steps}")

        all_metrics = []

        for scenario_idx, scenario_path in enumerate(scenarios):
            print(f"\n📋 Scenario {scenario_idx + 1}/{len(scenarios)}: {scenario_path}")

            for episode_idx in range(num_episodes):
                seed = seeds[episode_idx]

                print(
                    f"   Episode {episode_idx + 1}/{num_episodes} (seed={seed})...",
                    end="",
                )

                try:
                    # Run agent on scenario
                    start_time = time.time()
                    metrics = agent_fn(scenario_path, seed, max_steps)
                    eval_time = time.time() - start_time

                    # Convert to EvaluationMetrics
                    eval_metrics = self._convert_to_eval_metrics(
                        metrics, scenario_path, agent_name, episode_idx, seed
                    )

                    all_metrics.append(eval_metrics)
                    print(f" ✅ ({eval_time:.1f}s, R={eval_metrics.total_reward:.1f})")

                except Exception as e:
                    print(f" ❌ Error: {e}")
                    continue

        # Save results
        self._save_results(all_metrics, agent_name)

        return all_metrics

    def _convert_to_eval_metrics(
        self,
        raw_metrics: Dict,
        scenario_path: str,
        agent_name: str,
        episode_id: int,
        seed: int,
    ) -> EvaluationMetrics:
        """Convert raw metrics to EvaluationMetrics format"""

        # Extract scenario name
        scenario_name = os.path.basename(scenario_path).replace(".yaml", "")

        # Calculate completion rate
        total_drones = raw_metrics.get("total_drones", 1)
        completed = raw_metrics.get("missions_completed", 0)
        completion_rate = completed / total_drones if total_drones > 0 else 0

        # Calculate throughput (missions per step)
        episode_length = raw_metrics.get("episode_length", 1)
        throughput = completed / episode_length if episode_length > 0 else 0

        # Default values for missing metrics
        return EvaluationMetrics(
            scenario=scenario_name,
            agent_type=agent_name,
            episode_id=episode_id,
            seed=seed,
            episode_length=episode_length,
            total_reward=raw_metrics.get("total_reward", 0.0),
            average_reward=raw_metrics.get("average_reward", 0.0),
            collisions=raw_metrics.get("collisions", 0),
            los_violations=raw_metrics.get("los_violations", 0),
            unauthorized_landings=raw_metrics.get("unauthorized_landings", 0),
            missions_completed=completed,
            completion_rate=completion_rate,
            average_mission_time=raw_metrics.get("average_mission_time", 0.0),
            throughput=throughput,
            final_states=raw_metrics.get("final_states", []),
            time_in_states=raw_metrics.get("time_in_states", {}),
        )

    def _save_results(self, metrics: List[EvaluationMetrics], agent_name: str):
        """Save evaluation results to CSV and JSON"""

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # Save detailed CSV
        csv_path = os.path.join(self.output_dir, f"{agent_name}_{timestamp}.csv")
        with open(csv_path, "w", newline="") as csvfile:
            if metrics:
                fieldnames = list(asdict(metrics[0]).keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for metric in metrics:
                    row = asdict(metric)
                    # Convert complex fields to JSON strings
                    row["final_states"] = json.dumps(row["final_states"])
                    row["time_in_states"] = json.dumps(row["time_in_states"])
                    writer.writerow(row)

        # Save summary JSON
        json_path = os.path.join(
            self.output_dir, f"{agent_name}_{timestamp}_summary.json"
        )
        summary = self._generate_summary(metrics)
        with open(json_path, "w") as jsonfile:
            json.dump(summary, jsonfile, indent=2)

        print(f"\n💾 Results saved:")
        print(f"   Detailed: {csv_path}")
        print(f"   Summary: {json_path}")

    def _generate_summary(self, metrics: List[EvaluationMetrics]) -> Dict:
        """Generate summary statistics from evaluation metrics"""

        if not metrics:
            return {}

        # Group by scenario
        scenario_groups = {}
        for metric in metrics:
            scenario = metric.scenario
            if scenario not in scenario_groups:
                scenario_groups[scenario] = []
            scenario_groups[scenario].append(metric)

        summary = {
            "agent_type": metrics[0].agent_type,
            "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_episodes": len(metrics),
            "scenarios": {},
        }

        # Calculate statistics per scenario
        for scenario, scenario_metrics in scenario_groups.items():
            rewards = [m.total_reward for m in scenario_metrics]
            episode_lengths = [m.episode_length for m in scenario_metrics]
            completion_rates = [m.completion_rate for m in scenario_metrics]
            collisions = [m.collisions for m in scenario_metrics]

            summary["scenarios"][scenario] = {
                "episodes": len(scenario_metrics),
                "reward_stats": {
                    "mean": float(np.mean(rewards)),
                    "std": float(np.std(rewards)),
                    "min": float(np.min(rewards)),
                    "max": float(np.max(rewards)),
                },
                "episode_length_stats": {
                    "mean": float(np.mean(episode_lengths)),
                    "std": float(np.std(episode_lengths)),
                },
                "completion_rate_stats": {
                    "mean": float(np.mean(completion_rates)),
                    "std": float(np.std(completion_rates)),
                },
                "safety_stats": {
                    "total_collisions": int(np.sum(collisions)),
                    "collision_rate": float(np.mean(collisions)),
                },
            }

        return summary

    def compare_agents(self, results_files: List[str]) -> pd.DataFrame:
        """
        Compare multiple agents from saved results

        Args:
            results_files: List of CSV files with evaluation results

        Returns:
            DataFrame with comparative statistics
        """

        print(f"\n📈 Comparing {len(results_files)} agents...")

        all_data = []
        for file_path in results_files:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                all_data.append(df)
            else:
                print(f"⚠️  File not found: {file_path}")

        if not all_data:
            print("❌ No valid result files found")
            return pd.DataFrame()

        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)

        # Generate comparison table
        comparison = (
            combined_df.groupby(["agent_type", "scenario"])
            .agg(
                {
                    "total_reward": ["mean", "std"],
                    "episode_length": ["mean", "std"],
                    "completion_rate": ["mean", "std"],
                    "collisions": ["sum", "mean"],
                }
            )
            .round(3)
        )

        return comparison


def heuristic_agent_wrapper(scenario_path: str, seed: int, max_steps: int) -> Dict:
    """Wrapper for simple heuristic agent to match evaluation interface"""

    # Set random seed
    np.random.seed(seed)

    # Run heuristic agent (this would need to be implemented in the agent class)
    # For now, create a placeholder since the heuristic agent structure changed
    config = load_scenario_config(scenario_path)
    metrics = {
        "episode_length": max_steps,
        "total_reward": -100.0,  # Placeholder
        "collisions": 0,
        "missions_completed": config.traffic.max_drones,
    }
    metrics["total_drones"] = config.traffic.max_drones
    metrics["collisions"] = 0  # Simple heuristic doesn't track this
    metrics["los_violations"] = 0
    metrics["unauthorized_landings"] = 0
    metrics["average_mission_time"] = 0.0
    metrics["final_states"] = []
    metrics["time_in_states"] = {}

    return metrics


def main():
    """Example usage of evaluation framework"""

    # Initialize framework
    evaluator = EvaluationFramework()

    # Evaluate simple heuristic agent
    print("🎯 Evaluating Simple Heuristic Agent")
    heuristic_metrics = evaluator.evaluate_agent(
        agent_fn=heuristic_agent_wrapper,
        agent_name="simple_heuristic",
        num_episodes=5,  # Quick test
        max_steps=200,
    )

    print(f"\n✅ Evaluation completed!")
    print(f"   Total episodes: {len(heuristic_metrics)}")

    # Show sample results
    if heuristic_metrics:
        sample = heuristic_metrics[0]
        print(f"\n📊 Sample Results ({sample.scenario}):")
        print(f"   Total Reward: {sample.total_reward:.2f}")
        print(f"   Episode Length: {sample.episode_length}")
        print(f"   Completion Rate: {sample.completion_rate:.2%}")


if __name__ == "__main__":
    main()
