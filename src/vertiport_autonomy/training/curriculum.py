"""Curriculum learning trainer for progressive difficulty training."""

import os
from typing import Any, Dict, List, Optional

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize

from ..config.loader import load_scenario_config
from ..core.environment import VertiportEnv


class CurriculumTrainer:
    """Curriculum learning trainer for vertiport autonomy."""

    def __init__(self, log_dir: str = "logs", model_dir: str = "models"):
        """Initialize the curriculum trainer.

        Args:
            log_dir: Directory for training logs
            model_dir: Directory for saving models
        """
        self.log_dir = log_dir
        self.model_dir = model_dir
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)

        # Default curriculum phases
        self.phases = [
            {
                "name": "easy_world",
                "scenario": "scenarios/easy_world.yaml",
                "timesteps": 2000000,
                "success_threshold": -50,
                "n_envs": 16,
                "hyperparams": {
                    "learning_rate": 1e-4,
                    "ent_coef": 0.02,
                    "n_steps": 2048,
                    "batch_size": 64,
                },
            },
            {
                "name": "intermediate_world",
                "scenario": "scenarios/intermediate_world.yaml",
                "timesteps": 3000000,
                "success_threshold": -200,
                "n_envs": 16,
                "hyperparams": {
                    "learning_rate": 5e-5,
                    "ent_coef": 0.015,
                    "n_steps": 2048,
                    "batch_size": 128,
                },
            },
            {
                "name": "hard_world",
                "scenario": "scenarios/steady_flow.yaml",
                "timesteps": 5000000,
                "success_threshold": -100,
                "n_envs": 16,
                "hyperparams": {
                    "learning_rate": 3e-5,
                    "ent_coef": 0.01,
                    "n_steps": 2048,
                    "batch_size": 256,
                },
            },
        ]

    def set_custom_phases(self, phases: List[Dict[str, Any]]) -> None:
        """Set custom curriculum phases.

        Args:
            phases: List of phase configurations
        """
        self.phases = phases

    def train_phase(
        self, phase_config: Dict[str, Any], model: Optional[PPO] = None
    ) -> PPO:
        """Train a single curriculum phase.

        Args:
            phase_config: Configuration for this phase
            model: Previous model to continue from (None for first phase)

        Returns:
            Trained model for this phase
        """
        print(f"\n{'='*60}")
        print(f"Starting Phase: {phase_config['name'].upper()}")
        print(f"Scenario: {phase_config['scenario']}")
        print(f"Target Timesteps: {phase_config['timesteps']:,}")
        print(f"{'='*60}")

        # Load configuration for this phase
        config = load_scenario_config(phase_config["scenario"])

        # Create vectorized environment
        env = make_vec_env(
            VertiportEnv, n_envs=phase_config["n_envs"], env_kwargs={"config": config}
        )

        # Normalize environment
        env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.0)

        # Setup callbacks
        phase_log_dir = os.path.join(self.log_dir, f"curriculum_{phase_config['name']}")
        checkpoint_callback = CheckpointCallback(
            save_freq=100000,
            save_path=os.path.join(self.model_dir, phase_config["name"]),
            name_prefix=f"curriculum_{phase_config['name']}",
        )

        eval_callback = EvalCallback(
            eval_env=env,
            n_eval_episodes=10,
            eval_freq=50000,
            log_path=phase_log_dir,
            best_model_save_path=os.path.join(self.model_dir, phase_config["name"]),
            deterministic=True,
            render=False,
            verbose=1,
        )

        # Create or load model
        if model is None:
            # First phase - create new model
            print("Creating new PPO model...")
            model = PPO(
                "MultiInputPolicy",
                env,
                verbose=1,
                tensorboard_log=self.log_dir,
                gamma=0.99,
                **phase_config["hyperparams"],
            )
        else:
            # Subsequent phases - reload model with new environment
            print("Continuing from previous phase...")
            # Get the path to the previous phase model
            prev_phase_idx = [p["name"] for p in self.phases].index(
                phase_config["name"]
            ) - 1
            prev_phase_name = self.phases[prev_phase_idx]["name"]
            model_path = os.path.join(
                self.model_dir, f"curriculum_{prev_phase_name}_final"
            )

            # Load model with new environment
            model = PPO.load(model_path, env=env)
            print(f"Loaded model from: {model_path}")

            # Update learning rate if specified
            if "learning_rate" in phase_config["hyperparams"]:
                model.learning_rate = phase_config["hyperparams"]["learning_rate"]
                print(f"Updated learning rate to: {model.learning_rate}")

        # Train the model
        print(f"Training for {phase_config['timesteps']:,} timesteps...")
        model.learn(
            total_timesteps=phase_config["timesteps"],
            callback=[checkpoint_callback, eval_callback],
            tb_log_name=f"curriculum_{phase_config['name']}",
        )

        # Save final model for this phase
        final_model_path = os.path.join(
            self.model_dir, f"curriculum_{phase_config['name']}_final"
        )
        model.save(final_model_path)
        print(f"Phase completed! Model saved to: {final_model_path}")

        return model

    def run_full_curriculum(self) -> PPO:
        """Run the complete curriculum learning process.

        Returns:
            Final trained model
        """
        print("🎓 Starting Curriculum Learning for Vertiport Autonomy")
        print(f"Total phases: {len(self.phases)}")

        model = None
        for i, phase_config in enumerate(self.phases):
            print(f"\n📚 Phase {i+1}/{len(self.phases)}: {phase_config['name']}")
            model = self.train_phase(phase_config, model)

            print(f"✅ Phase {phase_config['name']} completed successfully!")

        print(f"\n🎉 Curriculum Learning Complete!")
        print(f"Final model saved in: {self.model_dir}")

        if model is None:
            raise RuntimeError("No model was trained - curriculum phases list is empty")
        return model

    def run_single_phase(self, phase_name: str, model: Optional[PPO] = None) -> PPO:
        """Run a single phase of the curriculum.

        Args:
            phase_name: Name of the phase to run
            model: Optional model to continue from

        Returns:
            Trained model for this phase

        Raises:
            ValueError: If phase_name is not found
        """
        phase_config = None
        for phase in self.phases:
            if phase["name"] == phase_name:
                phase_config = phase
                break

        if phase_config is None:
            available_phases = [p["name"] for p in self.phases]
            raise ValueError(
                f"Phase '{phase_name}' not found. Available phases: {available_phases}"
            )

        return self.train_phase(phase_config, model)

    def get_phase_names(self) -> List[str]:
        """Get list of available phase names.

        Returns:
            List of phase names
        """
        return [phase["name"] for phase in self.phases]


def main():
    """Curriculum training entry point."""
    trainer = CurriculumTrainer()

    # Run full curriculum
    final_model = trainer.run_full_curriculum()

    print("Curriculum training complete! 🚁")


if __name__ == "__main__":
    main()
