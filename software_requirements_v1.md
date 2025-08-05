# Software Requirements Specification (SRS): Advanced Vertiport Autonomy

**Version:** 1.0 (Final)
**Date:** August 03, 2025
**Document Status:** Approved for Implementation

---

### 1. Introduction

#### 1.1 Project Purpose
This document specifies the definitive requirements for a benchmarkable research platform designed to develop and evaluate Deep Reinforcement Learning (DRL) agents for the tactical coordination of autonomous vertiport operations. The system will simulate a dynamic, resource-constrained airspace, compelling the agent to master proactive traffic flow and resource management. The ultimate goal is to produce a framework capable of generating scientifically valid, reproducible, and comparable results between DRL agents and established baseline methodologies.

#### 1.2 Scope
The project scope is the creation of a complete **benchmark suite** for vertiport DRL agents. This includes:
*   A highly configurable, scenario-driven, discrete-time simulator.
*   A modular environment wrapper designed to support multiple agent architectures (initially centralized, with a clear path to decentralized).
*   The implementation of two distinct agents for comparative analysis:
    1.  A **Heuristic Baseline Agent** based on logical, deterministic rules (First-Come-First-Served).
    2.  A **DRL Agent (PPO)** to be trained and evaluated against the baseline.
*   A rigorous evaluation framework for generating and comparing quantitative Key Performance Indicators (KPIs) across a defined set of operational scenarios.

#### 1.3 Definitions, Acronyms, and Abbreviations
*   **DRL:** Deep Reinforcement Learning
*   **PPO:** Proximal Policy Optimization
*   **SRS:** Software Requirements Specification
*   **UAV:** Unmanned Aerial Vehicle (Drone)
*   **FATO:** Final Approach and Take-off Area (Landing Pad)
*   **LoS:** Loss of Separation: A breach of the minimum required separation distance.
*   **Collision/NMAC:** Near Mid-Air Collision: A breach of the critical drone-radius distance.
*   **KPI:** Key Performance Indicator
*   **Centralized Controller:** A single agent/policy observing the entire system and commanding all UAVs.
*   **Heuristic Policy:** A non-learning policy based on predefined rules.

---

### 2. Overall Description

#### 2.1 Product Perspective
The system is a research framework designed to empirically answer the question: "Under which operational scenarios, and according to which specific KPIs, does a DRL-based coordinator outperform a traditional, rule-based system for vertiport traffic management?" It provides the tools to train, benchmark, and deeply analyze the emergent behaviors of intelligent agents in a complex, dynamic airspace.

#### 2.2 Product Functions
*   **Scenario-Based Simulation:** Deterministically model a resource-constrained vertiport environment under various pre-defined traffic scenarios loaded from configuration files.
*   **Policy Agnosticism:** Provide a standard environment that can interface with different policy types (DRL, Heuristic, etc.) for direct, apples-to-apples comparison.
*   **Agent Implementation:** Provide a complete implementation for a baseline Heuristic agent and the training framework for a DRL agent.
*   **Comparative Analysis:** Generate comprehensive, version-controlled logs and visualizations that directly compare the KPIs of different agents under identical scenarios and random seeds.

#### 2.3 User Characteristics
The intended users are DRL/aerospace researchers and students who require a robust platform for conducting reproducible experiments.

#### 2.4 Constraints
*   **C-1:** The project shall be developed in Python 3.9+ with strict dependency management (e.g., a version-pinned `requirements.txt` or `pyproject.toml`).
*   **C-2:** Core libraries: `gymnasium`, `stable-baselines3`, `numpy`, `pydantic` (for configuration validation), and `pytest` (for testing).
*   **C-3:** The simulation must be discrete-time and fully deterministic given a fixed random seed.
*   **C-4:** Physics and systems modeling are explicitly simplified to focus on the tactical decision-making problem.
*   **C-5:** The initial implementation shall focus on a **Centralized Controller** architecture, but the system design must not preclude future extension to Multi-Agent Reinforcement Learning (MARL).

---

### 3. Specific Requirements

#### 3.1 Functional Requirements

##### FR-1: Simulator (`VertiportSim`)
*   **FR-1.1: Scenario-Driven Configuration:** The simulator shall be initialized from a single, type-validated configuration object (Pydantic model) loaded from a YAML/JSON file. This object defines the entire experiment scenario, including:
    *   Vertiport layout (coordinates for FATOs, Holding Points, Entry/Exit Gates).
    *   Traffic profile (e.g., "Steady_Flow," "Sudden_Influx"), which dictates the parameters for a stochastic traffic generation process (e.g., Poisson distribution with a specific λ).
*   **FR-1.2: Formal Drone State Machine:** The simulator shall manage a formal state for each drone: `INACTIVE`, `EN_ROUTE_TO_ENTRY`, `AWAITING_CLEARANCE` (at a holding point), `CLEARED_TO_LAND`, `EN_ROUTE_TO_PAD`, `ON_PAD` (for a fixed `ground_time`), `EN_ROUTE_TO_EXIT`, `FINISHED`.
*   **FR-1.3: Clearance-Based Mission Protocol:** The simulation logic shall enforce a landing clearance protocol. A drone at a holding point (`AWAITING_CLEARANCE` state) must receive an explicit `GRANT_LANDING_CLEARANCE` command to transition to the `CLEARED_TO_LAND` state and proceed to its assigned FATO.
*   **FR-1.4: Ground-Truth Event Logging:** The simulator shall be the sole source of truth for performance metrics. It must detect and log all key events with timestamps to an internal, retrievable log. Events include: Mission Completion, LoS, Collision, Clearance Granted, and FATO Occupied/Vacated.

##### FR-2: DRL Environment (`VertiportEnv`)
*   **FR-2.1: Gymnasium Compliance:** The environment shall correctly implement the full `gymnasium.Env` API.
*   **FR-2.2: Contextual Action Space:** The `MultiDiscrete` action space shall be contextual. The environment will interpret the agent's intended action for each drone based on the drone's current state.
    1.  `CONTINUE`: Proceed at `max_speed`.
    2.  `REDUCE_SPEED`: Proceed at `reduced_speed`.
    3.  `HOLD_IN_PLACE`: Tactical hold (zero velocity).
    4.  `DIVERT_TO_HOLD`: Strategic hold (re-route to a holding point).
    5.  `GRANT_LANDING_CLEARANCE`: **Actionable only if drone is `AWAITING_CLEARANCE`**. Transitions drone to `CLEARED_TO_LAND`. No-op otherwise.
*   **FR-2.3: Agent-Centric Observation Space:** The `Dict` observation space shall be structured to provide a comprehensive view for a centralized agent, while being extensible for future decentralized agents. It will contain:
    *   `drones_kinematics`: NumPy array of shape `(N, K)` containing position, velocity, etc., for all `N` drones.
    *   `drones_mission`: NumPy array of shape `(N, L)` containing mission state, target waypoint, etc.
    *   `adjacency_matrix`: A binary matrix where `(i, j) = 1` if drone `j` is within a configurable "sensor range" of drone `i`.
    *   `infrastructure_state`: A binary vector indicating the occupancy status of all FATOs and holding points.
*   **FR-2.4: Principle-Driven Reward Function:** The reward function shall be designed to directly incentivize the desired high-level behaviors.
    *   **Principle 1: Safety is Paramount.**
        *   Large, sparse penalty for each `Collision` event.
        *   Small, dense penalty for each timestep a `LoS` condition exists.
    *   **Principle 2: Follow Procedure.**
        *   A catastrophic penalty for landing on a FATO without clearance (state is not `CLEARED_TO_LAND`). This penalty must be significantly larger than a collision penalty.
    *   **Principle 3: Maximize Throughput.**
        *   Large, sparse positive reward for each mission completion.
        *   A small, dense penalty for the total time each drone spends in the system (`time_in_system`). This holistically penalizes all forms of delay.

##### FR-3: Agent Implementation & Experiment Management
*   **FR-3.1: Heuristic Baseline Agent:** A non-learning, rule-based agent shall be implemented with FCFS clearance logic and rule-based conflict avoidance (e.g., the lower-priority drone holds).
*   **FR-3.2: Scenario-Based Evaluation Framework:** The evaluation script must be a command-line tool that accepts arguments for:
    *   `--scenario <path_to_scenario_config>`
    *   `--agent <path_to_drl_model | "heuristic">`
    *   `--num-episodes <integer>`
    *   `--seeds <list_of_seeds>`
    The script will run the specified agent on the scenario for each seed and output an aggregated CSV file with the final KPIs.
*   **FR-3.3: Interactive Visualization & Debugging:** The `render()` function shall support an interactive mode allowing the user to pause, step through the simulation, and click on any drone to print its full state dictionary to the console.

#### 3.2 Non-Functional Requirements

*   **NFR-1: Performance:** The simulation must be capable of running at a minimum of 500 steps-per-second on a modern consumer-grade CPU to facilitate rapid training.
*   **NFR-2: Modularity & Extensibility:** The system shall be designed with a strict separation of concerns. The simulator, environment, and agents must be in separate modules, allowing for independent modification and testing.
*   **NFR-3: Code Quality & Testing:** Code shall be fully type-hinted, documented, and linted. The `VertiportSim` module must have a comprehensive unit test suite (`pytest`) with at least 85% test coverage, verifying state transitions, conflict detection, and mission logic.
*   **NFR-4: Reproducibility & Versioning:** Every experiment run (training or evaluation) must generate a metadata file containing the full configuration used, the git hash of the code version, and a list of all library versions, ensuring 100% scientific reproducibility.