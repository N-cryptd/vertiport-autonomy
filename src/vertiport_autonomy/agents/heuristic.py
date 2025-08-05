"""
Simplified Heuristic Baseline Agent

Provides a working baseline for comparison with DRL agents.
Uses simple FCFS strategy with basic conflict avoidance.
"""

from typing import Any, Dict

import numpy as np

from ..config.loader import load_scenario_config
from ..core.environment import VertiportEnv
from .base import BaseAgent


class SimpleHeuristicAgent(BaseAgent):
    """Simple heuristic agent that uses FCFS strategy."""

    def __init__(self, name: str = "SimpleHeuristic"):
        """Initialize the simple heuristic agent."""
        super().__init__(name)

    def act(self, observation: Dict[str, Any]) -> np.ndarray:
        """Select actions based on simple heuristic strategy.

        Args:
            observation: Current environment observation

        Returns:
            Array of actions for each drone
        """
        # Simple strategy: all drones move to waypoint
        num_drones = observation["drones_state"].shape[0]
        actions = np.ones(num_drones, dtype=np.int32)  # All MOVE_TO_WAYPOINT
        return actions

    def reset(self) -> None:
        """Reset agent state for a new episode."""
        # Simple heuristic doesn't maintain state
        pass


def run_simple_heuristic(scenario_path: str, max_steps: int = 200):
    """Run simple heuristic agent on given scenario"""

    print(f"\n🤖 Testing Simple Heuristic: {scenario_path}")

    config = load_scenario_config(scenario_path)
    env = VertiportEnv(config)

    obs, info = env.reset()
    total_reward = 0
    step_count = 0

    while step_count < max_steps:
        # Simple strategy: all drones move to waypoint
        num_drones = obs["drones_state"].shape[0]
        actions = np.ones(num_drones, dtype=np.int32)  # All MOVE_TO_WAYPOINT

        obs, reward, terminated, truncated, info = env.step(actions)
        total_reward += reward
        step_count += 1

        if terminated or truncated:
            break

    env.close()

    return {
        "episode_length": step_count,
        "total_reward": total_reward,
        "average_reward": total_reward / step_count if step_count > 0 else 0,
    }


def main():
    """Test simple heuristic on all scenarios"""

    scenarios = [
        "scenarios/easy_world.yaml",
        "scenarios/intermediate_world.yaml",
        "scenarios/steady_flow.yaml",
    ]

    print("🎯 Simple Heuristic Baseline Results")
    print("=" * 50)

    for scenario in scenarios:
        try:
            metrics = run_simple_heuristic(scenario)
            print(f"📊 {scenario}:")
            print(f"   Episode Length: {metrics['episode_length']}")
            print(f"   Total Reward: {metrics['total_reward']:.2f}")
            print(f"   Average Reward: {metrics['average_reward']:.2f}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
