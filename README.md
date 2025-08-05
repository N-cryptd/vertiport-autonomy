# Vertiport Autonomy: DRL-Based UAM Traffic Management

A comprehensive Deep Reinforcement Learning (DRL) framework for autonomous vertiport traffic management in Urban Air Mobility (UAM) scenarios. This project implements intelligent agents that learn to manage drone traffic at vertiports through simulation and curriculum learning.

## 🚁 Overview

This project addresses the challenge of autonomous traffic management at vertiports—specialized airports for electric Vertical Take-Off and Landing (eVTOL) aircraft. Using Deep Reinforcement Learning, we train intelligent agents to coordinate drone arrivals, departures, and ground operations while optimizing safety, efficiency, and throughput.

### Key Features

- **Scenario-driven simulation** with YAML-based configuration
- **Curriculum learning** for progressive training difficulty
- **Multi-agent support** with heuristic and DRL-based agents
- **Comprehensive evaluation framework** with detailed metrics
- **Event logging** for detailed analysis and debugging
- **Modular architecture** for extensibility and maintenance

## 🏗️ Project Structure

```
vertiport-autonomy/
├── src/vertiport_autonomy/          # Main package
│   ├── core/                        # Core simulation components
│   │   ├── simulator.py            # Vertiport simulation engine
│   │   ├── environment.py          # Gymnasium DRL environment
│   │   └── event_logger.py         # Event tracking system
│   ├── config/                     # Configuration management
│   │   ├── schema.py               # Pydantic configuration models
│   │   └── loader.py               # Configuration loading utilities
│   ├── agents/                     # Agent implementations
│   │   ├── base.py                 # Abstract agent interface
│   │   ├── heuristic.py            # Rule-based baseline agent
│   │   └── drl/                    # Deep RL agents (future)
│   ├── training/                   # Training components
│   │   ├── trainer.py              # Basic training logic
│   │   └── curriculum.py           # Curriculum learning implementation
│   └── evaluation/                 # Evaluation framework
│       ├── framework.py            # Main evaluation system
│       └── metrics.py              # Performance metrics calculation
├── scripts/                        # Entry point scripts
│   ├── train.py                    # Standard training
│   ├── train_curriculum.py         # Curriculum-based training
│   └── evaluate.py                 # Agent evaluation
├── scenarios/                      # Simulation scenarios
│   ├── easy_world.yaml            # Beginner training scenario
│   ├── intermediate_world.yaml    # Intermediate scenario
│   └── steady_flow.yaml           # Evaluation scenario
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   └── integration/                # Integration tests
├── docs/                           # Documentation
├── .github/workflows/              # CI/CD pipelines
└── models/                         # Trained model storage
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda for package management

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/vertiport-autonomy.git
   cd vertiport-autonomy
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

### Basic Usage

#### Training a DRL Agent

```bash
# Standard training
python scripts/train.py --scenario scenarios/easy_world.yaml --steps 1000000

# Curriculum learning (recommended)
python scripts/train_curriculum.py
```

#### Evaluating an Agent

```bash
# Evaluate heuristic baseline
python scripts/evaluate.py --agent heuristic --scenario scenarios/steady_flow.yaml

# Evaluate trained DRL model
python scripts/evaluate.py --agent drl --model models/ppo_vertiport_final.zip --scenario scenarios/steady_flow.yaml
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/vertiport_autonomy --cov-report=html
```

## 📊 Simulation Environment

### State Space

The environment provides comprehensive observations including:
- **Infrastructure state**: FATO occupancy, queue status, weather conditions
- **Drone information**: Positions, states, fuel levels, destinations
- **Adjacency matrix**: Spatial relationships between vertiport elements
- **Traffic metrics**: Current throughput, safety indicators

### Action Space

Agents can perform contextual actions based on drone states:
- **APPROACHING**: Grant/deny landing clearance, assign FATO
- **LANDED**: Authorize takeoff, hold for safety
- **DEPARTING**: Manage departure sequencing
- **EMERGENCY**: Coordinate emergency procedures

### Reward Function

Multi-objective reward system optimizing:
- **Safety**: Collision avoidance, separation maintenance
- **Efficiency**: Throughput maximization, delay minimization
- **Fuel economy**: Resource conservation
- **Infrastructure utilization**: Optimal FATO usage

## 🎯 Curriculum Learning

The training follows a three-phase curriculum:

1. **Easy World**: Basic scenarios with low traffic, simple weather
2. **Intermediate World**: Moderate complexity with varied conditions
3. **Hard World**: Realistic scenarios with high traffic and challenging weather

Each phase builds upon previous learning, ensuring robust agent behavior across diverse conditions.

## 📈 Performance Metrics

The evaluation framework tracks comprehensive KPIs:

- **Safety**: Collision rate, near-miss incidents, separation violations
- **Efficiency**: Average throughput, delay times, queue lengths
- **Resource usage**: Fuel consumption, FATO utilization
- **Operational**: Success rate, completion times, emergency handling

## 🔧 Configuration

Scenarios are configured using YAML files with Pydantic validation:

```yaml
scenario_name: "easy_world"
vertiport:
  fatos: 2
  max_queue_size: 5
  weather_variation: 0.1
traffic:
  arrival_rate: 0.3
  departure_rate: 0.25
  emergency_probability: 0.01
curriculum:
  level: 1
  difficulty_factors:
    traffic_density: 0.5
    weather_severity: 0.3
```

## 🧪 Testing

Comprehensive test suite includes:
- **Unit tests**: Individual component functionality
- **Integration tests**: End-to-end training and evaluation workflows
- **Scenario tests**: Validation across different configurations
- **Performance tests**: Benchmarking and regression detection

## 📚 Documentation

- **API Reference**: Auto-generated from docstrings
- **Tutorials**: Step-by-step guides for common tasks
- **Technical specs**: Detailed system architecture and algorithms
- **Contributing guide**: Development workflow and standards

## 🤝 Contributing

We welcome contributions! Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for:
- Development setup and workflow
- Code style and testing requirements
- Pull request guidelines
- Issue reporting procedures

## 📄 License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

## 🔗 Related Work

This project builds upon research in:
- Urban Air Mobility (UAM) traffic management
- Deep Reinforcement Learning for transportation
- Multi-agent systems in aviation
- Autonomous air traffic control

## 📞 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join technical discussions in GitHub Discussions
- **Documentation**: Visit our [documentation site](https://n-cryptd.github.io/vertiport-autonomy)

## 🏆 Acknowledgments

Special thanks to:
- The stable-baselines3 team for the DRL framework
- The Gymnasium project for the environment API
- The broader UAM research community

---

**Note**: This project is under active development. APIs may change between versions. Please check the [CHANGELOG](CHANGELOG.md) for updates.