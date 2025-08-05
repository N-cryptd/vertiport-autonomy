# vertiport_env.py
import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
from gymnasium import spaces

from ..config.schema import ScenarioConfig
from .event_logger import EventLogger, EventType
from .simulator import DroneState, VertiportSim


class VertiportEnv(gym.Env):
    """A Gymnasium environment for the VertiportSim."""

    metadata = {"render_modes": ["human"], "render_fps": 10}

    def __init__(self, config: ScenarioConfig, render_mode=None):
        super().__init__()

        self.config = config
        self.num_drones = config.traffic.max_drones
        self.sim = VertiportSim(config)

        # Define action and observation space
        # Action space: 5 actions per drone as per FR-2.2
        self.action_space = spaces.MultiDiscrete([5] * self.num_drones)

        # Observation space: Expanded to include adjacency matrix and infrastructure state
        # drone_state: position(3), velocity(3), acceleration(3), target_waypoint(3),
        #              hovering(1), hover_count(1), state(1), clearance_granted(1) = 16 features
        # infrastructure_state: FATO occupancy (1 per FATO) + holding point occupancy (1 per holding point)
        num_fatos = len(config.vertiport.fatos)
        num_holdings = len(config.vertiport.holding_points)

        self.observation_space = spaces.Dict(
            {
                "drones_state": spaces.Box(
                    low=-100.0,
                    high=100.0,
                    shape=(self.num_drones, 16),
                    dtype=np.float32,
                ),
                "distance_matrix": spaces.Box(
                    low=0,
                    high=1000.0,
                    shape=(self.num_drones, self.num_drones),
                    dtype=np.float32,
                ),
                "adjacency_matrix": spaces.Box(
                    low=0,
                    high=1,
                    shape=(self.num_drones, self.num_drones),
                    dtype=np.float32,
                ),
                "infrastructure_state": spaces.Box(
                    low=0, high=1, shape=(num_fatos + num_holdings,), dtype=np.float32
                ),
            }
        )

        self.max_steps = 1000
        self.current_step = 0
        self.prev_hover_count = np.zeros(self.num_drones)

        # For rendering
        self.render_mode = render_mode
        if self.render_mode == "human":
            self.fig, self.ax = plt.subplots(figsize=(8, 8))

    def _get_obs(self):
        """Formats the simulator state into the observation space shape."""
        state = self.sim._get_state()

        # Stack all state features per drone - now includes clearance_granted
        drones_state = np.hstack(
            [
                state["positions"],
                state["velocities"],
                state["accelerations"],
                state["target_waypoints"],
                state["hovering"].reshape(-1, 1),
                state["hover_count"].reshape(-1, 1),
                state["states"].reshape(-1, 1),
                state["clearance_granted"].reshape(-1, 1),
            ]
        ).astype(np.float32)

        # Calculate adjacency matrix based on sensor range
        sensor_range = self.config.simulation.get("sensor_range", 20.0)
        dist_matrix = state["distance_matrix"]
        adjacency_matrix = (dist_matrix > 0) & (dist_matrix < sensor_range)

        # Infrastructure state: FATO occupancy + holding point occupancy
        infrastructure_state = np.hstack(
            [
                state["fato_occupancy"],
                # Holding point occupancy not implemented yet - placeholder
                np.zeros(len(self.config.vertiport.holding_points), dtype=float),
            ]
        )

        # Check for NaN/inf values
        if np.any(np.isnan(drones_state)):
            print(f"WARNING: NaN found in drones_state!")

        distance_matrix = np.where(
            np.isinf(state["distance_matrix"]), 1000.0, state["distance_matrix"]
        )
        distance_matrix = np.where(np.isnan(distance_matrix), 1000.0, distance_matrix)

        return {
            "drones_state": drones_state,
            "distance_matrix": distance_matrix.astype(np.float32),
            "adjacency_matrix": adjacency_matrix.astype(np.float32),
            "infrastructure_state": infrastructure_state.astype(np.float32),
        }

    def reset(self, *, seed=None, options=None):
        # Call the parent reset method with seed and options
        super().reset(seed=seed, options=options)
        self.sim.reset()
        self.current_step = 0
        self.prev_hover_count = np.zeros(self.num_drones)
        return self._get_obs(), {}

    def step(self, action):
        self.current_step += 1

        # Get state before the step for reward calculation
        prev_state = self.sim._get_state()

        # Execute the action in the simulator
        current_state = self.sim.step(action)

        # Check for termination conditions first
        terminated = bool(
            current_state["collisions"] or np.all(current_state["states"] == 7)
        )  # 7 = DroneState.FINISHED
        truncated = self.current_step >= self.max_steps

        # Calculate reward (pass termination flags)
        reward = self._calculate_reward(
            prev_state, current_state, action, terminated, truncated
        )

        if self.render_mode == "human":
            self.render()

        return self._get_obs(), float(reward), bool(terminated), bool(truncated), {}

    def _calculate_reward(
        self, prev_state, current_state, action, terminated, truncated
    ):
        reward = 0
        min_separation = self.sim.min_separation
        drone_radius = self.sim.drone_radius
        logger = self.sim.logger

        # Get curriculum level for progressive penalty scaling
        curriculum_level = self.config.simulation.get("curriculum_level", 3)

        # Define penalty multipliers based on curriculum level
        if curriculum_level == 1:  # Easy World
            collision_penalty = 10.0  # Very low
            unauthorized_penalty = 0.0  # Disabled
            los_penalty_factor = 0.1  # Minimal
            progress_reward = 1.0  # Add progress rewards
        elif curriculum_level == 2:  # Intermediate World
            collision_penalty = 100.0  # Moderate
            unauthorized_penalty = 500.0  # Moderate
            los_penalty_factor = 0.3  # Moderate
            progress_reward = 0.5  # Reduced progress rewards
        else:  # Hard World (curriculum_level >= 3)
            collision_penalty = 1000.0  # Full penalty
            unauthorized_penalty = 5000.0  # Full penalty
            los_penalty_factor = 0.5  # Full penalty
            progress_reward = 0.0  # No progress rewards

        # 1. Safety Penalties (Scaled by curriculum)
        if current_state["collisions"]:
            reward -= collision_penalty
            logger.log_event(
                EventType.COLLISION_DETECTED,
                details=f"Collision detected at step {self.current_step}",
            )

        # Loss of Separation penalty (scaled)
        dist_matrix = current_state["distance_matrix"]
        for i in range(self.num_drones):
            for j in range(i + 1, self.num_drones):
                if dist_matrix[i, j] < min_separation:
                    violation_severity = min_separation - dist_matrix[i, j]
                    reward -= violation_severity * los_penalty_factor

        # 2. Procedure Violations (Scaled by curriculum)
        for i in range(self.num_drones):
            if (
                current_state["states"][i] == DroneState.ON_PAD
                and not prev_state["clearance_granted"][i]
            ):
                reward -= unauthorized_penalty
                if unauthorized_penalty > 0:  # Only log if penalty is active
                    logger.log_event(
                        EventType.UNAUTHORIZED_LANDING,
                        drone_id=i,
                        details="Landed without clearance",
                    )

        # 3. Throughput Rewards
        newly_finished = (current_state["states"] == DroneState.FINISHED) & (
            prev_state["states"] != DroneState.FINISHED
        )
        reward += np.sum(newly_finished) * 100.0

        # 4. Progress Rewards (Easy/Intermediate worlds only)
        if progress_reward > 0:
            for i in range(self.num_drones):
                if current_state["states"][i] != DroneState.FINISHED:
                    # Reward for getting closer to target
                    target_pos = current_state["target_waypoints"][i]
                    current_pos = current_state["positions"][i]
                    prev_pos = prev_state["positions"][i]

                    current_dist = np.linalg.norm(target_pos - current_pos)
                    prev_dist = np.linalg.norm(target_pos - prev_pos)

                    if current_dist < prev_dist:  # Getting closer
                        reward += progress_reward * (prev_dist - current_dist)

        # Time-in-system penalty (scaled)
        time_penalty = 0.1 if curriculum_level >= 2 else 0.05
        for i in range(self.num_drones):
            if current_state["states"][i] != DroneState.FINISHED:
                reward -= time_penalty

        # Save logs at end of episode
        if (terminated or truncated) and hasattr(self, "_is_main_env"):
            logger.save_to_csv()

        return reward

    def render(self):
        if self.render_mode != "human":
            return

        self.ax.clear()

        state = self.sim._get_state()
        positions = state["positions"]

        # Plot drones
        self.ax.scatter(positions[:, 0], positions[:, 1], c="blue", label="Drones")

        # Plot flight paths
        for i in range(self.num_drones):
            # Arrival path
            arr_path = self.sim.arrival_plans[i]
            self.ax.plot(arr_path[:, 0], arr_path[:, 1], "g--", alpha=0.5)
            # Departure path
            dep_path = self.sim.departure_plans[i]
            self.ax.plot(dep_path[:, 0], dep_path[:, 1], "r--", alpha=0.5)
            # Drone label
            self.ax.text(positions[i, 0], positions[i, 1], f"D{i}", fontsize=9)

        self.ax.set_xlim(-25, 25)
        self.ax.set_ylim(-25, 25)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_title(f"Step: {self.current_step}")
        self.ax.legend()
        plt.pause(0.01)

    def close(self):
        if self.render_mode == "human":
            plt.close(self.fig)
