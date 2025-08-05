import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.vertiport_autonomy.config.loader import load_scenario_config
from src.vertiport_autonomy.core.environment import VertiportEnv


# Test basic functionality
def test_basic_setup():
    print("Loading configuration...")
    config = load_scenario_config("scenarios/steady_flow.yaml")
    print(f"Config loaded successfully - {config.traffic.max_drones} drones")

    print("Creating environment...")
    env = VertiportEnv(config)
    print(f"Environment created - Action space: {env.action_space}")

    print("Testing reset...")
    obs, info = env.reset()
    print(f"Reset successful - Observation keys: {obs.keys()}")

    print("Testing step...")
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step successful - Reward: {reward}")

    env.close()
    print("Test completed successfully!")


if __name__ == "__main__":
    test_basic_setup()
