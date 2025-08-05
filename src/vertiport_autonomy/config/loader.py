import yaml

from .schema import ScenarioConfig


def load_scenario_config(path: str) -> ScenarioConfig:
    with open(path, "r") as f:
        config_data = yaml.safe_load(f)
    return ScenarioConfig(**config_data)
