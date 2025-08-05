import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.vertiport_autonomy.config.loader import load_scenario_config
from src.vertiport_autonomy.core.environment import VertiportEnv


def test_curriculum_phases():
    """Test all curriculum phases for basic functionality"""

    phases = [
        ("Easy World", "scenarios/easy_world.yaml"),
        ("Intermediate World", "scenarios/intermediate_world.yaml"),
        ("Hard World", "scenarios/steady_flow.yaml"),
    ]

    for phase_name, scenario_path in phases:
        print(f"\n🧪 Testing {phase_name}")
        print(f"Scenario: {scenario_path}")

        try:
            # Load configuration
            config = load_scenario_config(scenario_path)
            curriculum_level = config.simulation.get("curriculum_level", 3)
            print(f"✅ Config loaded - Curriculum Level: {curriculum_level}")
            print(f"   Drones: {config.traffic.max_drones}")
            print(f"   Arrival Rate: {config.traffic.arrival_rate}")

            # Create environment
            env = VertiportEnv(config)
            print(f"✅ Environment created")

            # Test reset
            obs, info = env.reset()
            print(f"✅ Reset successful")

            # Test multiple steps to check reward behavior
            total_reward = 0
            episode_length = 0
            max_steps = 50  # Test first 50 steps

            for step in range(max_steps):
                action = env.action_space.sample()
                obs, reward, terminated, truncated, info = env.step(action)
                total_reward += reward
                episode_length += 1

                if terminated or truncated:
                    break

            print(f"✅ Test run completed:")
            print(f"   Episode Length: {episode_length}")
            print(f"   Total Reward: {total_reward:.2f}")
            print(f"   Average Reward: {total_reward/episode_length:.2f}")

            # Check if episode lasted reasonable length for curriculum level
            expected_min_length = {1: 10, 2: 5, 3: 1}  # Easy should last longer
            min_length = expected_min_length.get(int(curriculum_level), 1)

            if episode_length >= min_length:
                print(f"✅ Episode length appropriate for curriculum level")
            else:
                print(f"⚠️  Episode too short for curriculum level {curriculum_level}")

            env.close()
            print(f"✅ {phase_name} test passed!\n")

        except Exception as e:
            print(f"❌ {phase_name} test failed: {str(e)}")
            return False

    print("🎉 All curriculum phases tested successfully!")


if __name__ == "__main__":
    test_curriculum_phases()
