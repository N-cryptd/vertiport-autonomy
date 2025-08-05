"""Performance metrics calculation utilities."""

from typing import Any, Dict, List

import numpy as np


def calculate_performance_metrics(
    episode_data: List[Dict[str, Any]],
) -> Dict[str, float]:
    """Calculate aggregated performance metrics from episode data.

    Args:
        episode_data: List of episode results containing metrics

    Returns:
        Dictionary of aggregated performance metrics
    """
    if not episode_data:
        return {}

    # Extract metrics from episodes
    episode_lengths = [ep.get("episode_length", 0) for ep in episode_data]
    total_rewards = [ep.get("total_reward", 0.0) for ep in episode_data]
    collisions = [ep.get("collisions", 0) for ep in episode_data]
    missions_completed = [ep.get("missions_completed", 0) for ep in episode_data]

    # Calculate aggregated metrics
    metrics = {
        "mean_episode_length": float(np.mean(episode_lengths)),
        "std_episode_length": float(np.std(episode_lengths)),
        "mean_total_reward": float(np.mean(total_rewards)),
        "std_total_reward": float(np.std(total_rewards)),
        "total_collisions": int(np.sum(collisions)),
        "collision_rate": float(np.mean(collisions)),
        "total_missions_completed": int(np.sum(missions_completed)),
        "completion_rate": float(np.mean(missions_completed)),
        "success_rate": float(
            np.mean(
                [
                    1.0 if ep.get("missions_completed", 0) > 0 else 0.0
                    for ep in episode_data
                ]
            )
        ),
    }

    return metrics


def calculate_safety_metrics(episode_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate safety-specific metrics.

    Args:
        episode_data: List of episode results containing safety metrics

    Returns:
        Dictionary of safety metrics
    """
    if not episode_data:
        return {}

    unauthorized_landings = [ep.get("unauthorized_landings", 0) for ep in episode_data]
    loss_of_separation = [ep.get("loss_of_separation", 0) for ep in episode_data]

    safety_metrics = {
        "total_unauthorized_landings": int(np.sum(unauthorized_landings)),
        "unauthorized_landing_rate": float(np.mean(unauthorized_landings)),
        "total_loss_of_separation": int(np.sum(loss_of_separation)),
        "loss_of_separation_rate": float(np.mean(loss_of_separation)),
    }

    return safety_metrics


def calculate_efficiency_metrics(
    episode_data: List[Dict[str, Any]],
) -> Dict[str, float]:
    """Calculate efficiency-specific metrics.

    Args:
        episode_data: List of episode results containing efficiency metrics

    Returns:
        Dictionary of efficiency metrics
    """
    if not episode_data:
        return {}

    time_in_system = [ep.get("mean_time_in_system", 0.0) for ep in episode_data]
    throughput = [ep.get("throughput", 0.0) for ep in episode_data]

    efficiency_metrics = {
        "mean_time_in_system": float(np.mean(time_in_system)),
        "std_time_in_system": float(np.std(time_in_system)),
        "mean_throughput": float(np.mean(throughput)),
        "std_throughput": float(np.std(throughput)),
    }

    return efficiency_metrics
