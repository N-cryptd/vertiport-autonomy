# vertiport_simulator.py
from enum import Enum

import numpy as np

from ..config.schema import (
    FATO,
    Gate,
    HoldingPoint,
    Point3D,
    ScenarioConfig,
    TrafficProfile,
)
from .event_logger import EventLogger, EventType


class DroneState(Enum):
    INACTIVE = 0
    EN_ROUTE_TO_ENTRY = 1
    AWAITING_CLEARANCE = 2
    CLEARED_TO_LAND = 3
    EN_ROUTE_TO_PAD = 4
    ON_PAD = 5
    EN_ROUTE_TO_EXIT = 6
    FINISHED = 7


class VertiportSim:
    """
    A lightweight, discrete-time simulator for multi-drone vertiport operations.
    Manages drone states, flight plans, and collision detection.
    """

    def __init__(self, config: ScenarioConfig):
        self.config = config
        self.num_drones = config.traffic.max_drones
        self.dt = config.simulation.get("time_step", 0.1)

        # Simulation constants
        self.drone_radius = config.simulation.get("drone_radius", 0.5)
        self.arrival_radius = config.simulation.get("arrival_radius", 1.0)
        self.drone_speed = config.simulation.get("drone_speed", 5.0)
        self.min_separation = config.simulation.get("min_separation", 6.0)

        # Initialize event logger
        self.logger = EventLogger()

        # Define flight plans (arrival and departure) from config
        self.arrival_plans = self._generate_arrival_plans()
        self.departure_plans = self._generate_departure_plans()

        # Initialize drone state arrays with proper types
        self.positions: np.ndarray = np.zeros((self.num_drones, 3))
        self.velocities: np.ndarray = np.zeros((self.num_drones, 3))
        self.accelerations: np.ndarray = np.zeros((self.num_drones, 3))
        self.waypoint_indices: np.ndarray = np.ones(self.num_drones, dtype=int)
        self.states: np.ndarray = np.array([DroneState.INACTIVE] * self.num_drones)
        self.hovering: np.ndarray = np.zeros(self.num_drones, dtype=bool)
        self.hover_count: np.ndarray = np.zeros(self.num_drones, dtype=int)
        self.clearance_granted: np.ndarray = np.zeros(self.num_drones, dtype=bool)
        self.fato_occupancy: np.ndarray = np.zeros(
            len(config.vertiport.fatos), dtype=bool
        )
        self.ground_times: np.ndarray = np.zeros(self.num_drones, dtype=float)

        self.reset()

    def _generate_arrival_plans(self):
        """Generates arrival flight plans from configuration."""
        plans = []
        entry_gates = [gate for gate in self.config.vertiport.gates if gate.is_entry]

        for i in range(self.num_drones):
            # Assign FATO in round-robin fashion
            fato = self.config.vertiport.fatos[i % len(self.config.vertiport.fatos)]
            gate = entry_gates[i % len(entry_gates)]

            # Create waypoints: [gate] + approach_path + [FATO]
            waypoints = [np.array([gate.position.x, gate.position.y, gate.position.z])]
            for point in fato.approach_path:
                waypoints.append(np.array([point.x, point.y, point.z]))
            waypoints.append(
                np.array([fato.position.x, fato.position.y, fato.position.z])
            )

            plans.append(np.array(waypoints))
        return plans

    def _generate_departure_plans(self):
        """Generates departure plans from configuration."""
        plans = []
        exit_gates = [gate for gate in self.config.vertiport.gates if gate.is_exit]

        for i in range(self.num_drones):
            # Assign FATO in round-robin fashion
            fato = self.config.vertiport.fatos[i % len(self.config.vertiport.fatos)]
            gate = exit_gates[i % len(exit_gates)]

            # Create waypoints: [FATO] + reversed approach_path + [gate]
            waypoints = [np.array([fato.position.x, fato.position.y, fato.position.z])]
            for point in reversed(fato.approach_path):
                waypoints.append(np.array([point.x, point.y, point.z]))
            waypoints.append(
                np.array([gate.position.x, gate.position.y, gate.position.z])
            )

            plans.append(np.array(waypoints))
        return plans

    def reset(self):
        """Resets the simulation to its initial state."""
        self.positions = np.array([plan[0] for plan in self.arrival_plans])
        self.velocities = np.zeros((self.num_drones, 3))
        self.accelerations = np.zeros((self.num_drones, 3))
        self.waypoint_indices = np.ones(self.num_drones, dtype=int)
        self.states = np.array([DroneState.INACTIVE] * self.num_drones)
        self.hovering = np.zeros(self.num_drones, dtype=bool)
        self.hover_count = np.zeros(self.num_drones, dtype=int)
        self.clearance_granted = np.zeros(self.num_drones, dtype=bool)

        # Activate drones
        for i in range(self.num_drones):
            self.states[i] = DroneState.EN_ROUTE_TO_ENTRY
            self.logger.log_event(EventType.MISSION_STARTED, drone_id=i)

        return self._get_state()

    def step(self, actions: np.ndarray):
        """
        Advances the simulation by one time step based on agent actions.
        Action 0: Hover, Action 1: Continue, Action 4: Grant Clearance.
        """
        # Store previous velocities for acceleration calculation
        prev_velocities = self.velocities.copy()

        # 1. Process clearance grants first (Action 4)
        for i in range(self.num_drones):
            if actions[i] == 4:  # Grant Clearance
                if self.states[i] == DroneState.AWAITING_CLEARANCE:
                    self.clearance_granted[i] = True

        # 2. Update velocities based on actions
        for i in range(self.num_drones):
            if self.states[i] in [
                DroneState.FINISHED,
                DroneState.INACTIVE,
                DroneState.AWAITING_CLEARANCE,
                DroneState.ON_PAD,
            ]:
                self.velocities[i] = 0
                self.hovering[i] = True
                continue

            if actions[i] == 0:  # Hover
                self.velocities[i] = 0
                # Increment hover count if not already hovering
                if not self.hovering[i]:
                    self.hover_count[i] += 1
                self.hovering[i] = True
            elif actions[i] == 1:  # Continue
                target_waypoint = self._get_target_waypoint(i)
                direction = target_waypoint - self.positions[i]
                distance = np.linalg.norm(direction)

                # Add epsilon to prevent division by zero
                if distance > self.arrival_radius and distance > 1e-8:
                    self.velocities[i] = (direction / distance) * self.drone_speed
                else:
                    self.velocities[i] = (
                        0  # Reached waypoint, hover for next logic step
                    )
                self.hovering[i] = False

        # 3. Calculate acceleration
        self.accelerations = (self.velocities - prev_velocities) / self.dt

        # 4. Update positions
        self.positions += self.velocities * self.dt

        # 5. Update ground times for drones on pads
        for i in range(self.num_drones):
            if self.states[i] == DroneState.ON_PAD:
                self.ground_times[i] += self.dt

        # 6. Check for waypoint arrival and update mission status
        for i in range(self.num_drones):
            if self.states[i] == DroneState.FINISHED:
                continue

            target_waypoint = self._get_target_waypoint(i)
            distance_to_target = np.linalg.norm(target_waypoint - self.positions[i])

            if distance_to_target < self.arrival_radius:
                self._advance_mission(i)

        return self._get_state()

    def _get_target_waypoint(self, drone_index: int):
        """Gets the current target waypoint for a specific drone."""
        state = self.states[drone_index]
        wp_idx = self.waypoint_indices[drone_index]

        if state in [
            DroneState.EN_ROUTE_TO_ENTRY,
            DroneState.AWAITING_CLEARANCE,
            DroneState.CLEARED_TO_LAND,
        ]:
            return self.arrival_plans[drone_index][wp_idx]
        elif state in [DroneState.ON_PAD, DroneState.EN_ROUTE_TO_EXIT]:
            return self.departure_plans[drone_index][wp_idx]
        else:  # FINISHED or INACTIVE
            return self.positions[drone_index]  # Target is its own position

    def _advance_mission(self, drone_index: int):
        """Advances a drone's mission to the next waypoint or next phase."""
        state = self.states[drone_index]
        wp_idx = self.waypoint_indices[drone_index]

        if state == DroneState.EN_ROUTE_TO_ENTRY:
            # Check if we've reached the holding point
            if (
                wp_idx == len(self.arrival_plans[drone_index]) - 2
            ):  # Second last point is holding
                self.states[drone_index] = DroneState.AWAITING_CLEARANCE
                self.logger.log_event(
                    EventType.HOLDING_POINT_REACHED, drone_id=drone_index
                )
            else:
                self.waypoint_indices[drone_index] += 1

        elif state == DroneState.AWAITING_CLEARANCE:
            # Only advance if clearance has been granted
            if self.clearance_granted[drone_index]:
                self.states[drone_index] = DroneState.CLEARED_TO_LAND
                self.clearance_granted[drone_index] = False
                self.waypoint_indices[drone_index] += 1
                self.logger.log_event(EventType.CLEARANCE_GRANTED, drone_id=drone_index)

        elif state == DroneState.CLEARED_TO_LAND:
            # Check if we've reached the FATO
            if wp_idx == len(self.arrival_plans[drone_index]) - 1:
                # Find FATO index for this drone
                fato_id = self._get_assigned_fato(drone_index)
                if fato_id >= 0 and not self.fato_occupancy[fato_id]:
                    self.states[drone_index] = DroneState.ON_PAD
                    self.fato_occupancy[fato_id] = True
                    self.logger.log_event(
                        EventType.FATO_OCCUPIED,
                        drone_id=drone_index,
                        details=f"FATO_{fato_id}",
                    )
                else:
                    # FATO occupied, remain at current position
                    pass
            else:
                self.waypoint_indices[drone_index] += 1

        elif state == DroneState.ON_PAD:
            # After ground time, switch to departure
            if self.ground_times[drone_index] >= self.config.simulation.get(
                "ground_time", 5.0
            ):
                # Find FATO index for this drone
                fato_id = self._get_assigned_fato(drone_index)
                if fato_id >= 0:
                    self.fato_occupancy[fato_id] = False
                    self.states[drone_index] = DroneState.EN_ROUTE_TO_EXIT
                    self.waypoint_indices[drone_index] = 1
                    self.ground_times[drone_index] = 0
                    self.logger.log_event(
                        EventType.FATO_VACATED,
                        drone_id=drone_index,
                        details=f"FATO_{fato_id}",
                    )

        elif state == DroneState.EN_ROUTE_TO_EXIT:
            # Check if we've reached the exit
            if wp_idx >= len(self.departure_plans[drone_index]) - 1:
                self.states[drone_index] = DroneState.FINISHED
                self.logger.log_event(EventType.MISSION_COMPLETED, drone_id=drone_index)
            else:
                self.waypoint_indices[drone_index] += 1

    def _get_assigned_fato(self, drone_index: int) -> int:
        """Returns the index of the FATO assigned to this drone."""
        # Simplified: drone index modulo number of FATOs
        return drone_index % len(self.config.vertiport.fatos)

    def _get_state(self):
        """Returns the full current state of the simulation."""
        # Pairwise distance matrix
        pos_matrix = self.positions[:, np.newaxis, :] - self.positions[np.newaxis, :, :]
        dist_matrix = np.linalg.norm(pos_matrix, axis=2)

        # Collision detection
        # Drones can't collide with themselves, so set diagonal to a large value
        np.fill_diagonal(dist_matrix, 1000.0)
        collisions = dist_matrix < (2 * self.drone_radius)

        target_waypoints = np.array(
            [self._get_target_waypoint(i) for i in range(self.num_drones)]
        )

        return {
            "positions": self.positions.copy(),
            "velocities": self.velocities.copy(),
            "accelerations": self.accelerations.copy(),
            "target_waypoints": target_waypoints,
            "states": np.array([state.value for state in self.states]),
            "fato_occupancy": self.fato_occupancy.copy(),
            "distance_matrix": dist_matrix,
            "collisions": collisions.any(),
            "hovering": self.hovering.copy(),
            "hover_count": self.hover_count.copy(),
            "clearance_granted": self.clearance_granted.copy(),
            "logger": self.logger,
        }
