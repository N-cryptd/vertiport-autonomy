import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.vertiport_autonomy.config.loader import load_scenario_config
from src.vertiport_autonomy.training.curriculum import CurriculumTrainer


def test_phase_transition():
    """Test curriculum phase transitions without full training"""

    print("🧪 Testing Curriculum Phase Transitions")

    trainer = CurriculumTrainer()

    # Test first phase setup
    phase1 = trainer.phases[0]  # easy_world
    print(f"\n📚 Testing Phase 1: {phase1['name']}")
    config1 = load_scenario_config(phase1["scenario"])
    print(f"✅ Config loaded - {phase1['n_envs']} environments")

    # Test second phase setup
    phase2 = trainer.phases[1]  # intermediate_world
    print(f"\n📚 Testing Phase 2: {phase2['name']}")
    config2 = load_scenario_config(phase2["scenario"])
    print(f"✅ Config loaded - {phase2['n_envs']} environments")

    # Verify consistent environment counts
    assert (
        phase1["n_envs"] == phase2["n_envs"]
    ), f"Environment count mismatch: {phase1['n_envs']} != {phase2['n_envs']}"
    print(f"✅ Environment counts consistent: {phase1['n_envs']}")

    # Test model path construction
    prev_phase_idx = [p["name"] for p in trainer.phases].index(phase2["name"]) - 1
    prev_phase_name = trainer.phases[prev_phase_idx]["name"]
    model_path = os.path.join(trainer.model_dir, f"curriculum_{prev_phase_name}_final")
    print(f"✅ Model transition path: {model_path}")

    print(f"\n🎉 Phase transition logic validated!")


if __name__ == "__main__":
    test_phase_transition()
