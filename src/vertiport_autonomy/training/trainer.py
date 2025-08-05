"""Basic training utilities for vertiport autonomy agents."""

import os
from typing import Any, Dict, Optional

import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize

from ..config.loader import load_scenario_config
from ..core.environment import VertiportEnv


class Trainer:
    """Basic trainer for PPO agents in vertiport environments."""

    def __init__(
        self,
        log_dir: str = "logs",
        model_dir: str = "models",
        n_envs: int = 50,
        **ppo_kwargs,
    ):
        """Initialize the trainer.

        Args:
            log_dir: Directory for training logs
            model_dir: Directory for saving models
            n_envs: Number of parallel environments
            **ppo_kwargs: Additional arguments for PPO
        """
        self.log_dir = log_dir
        self.model_dir = model_dir
        self.n_envs = n_envs
        self.ppo_kwargs = ppo_kwargs

        # Create directories
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)

        # Default PPO parameters
        self.default_ppo_params = {
            "gamma": 0.99,
            "n_steps": 1024,
            "batch_size": 128,
            "learning_rate": 1e-4,
            "gae_lambda": 0.95,
            "clip_range": 0.2,
            "ent_coef": 0.01,
            "vf_coef": 0.5,
            "max_grad_norm": 0.5,
            "policy_kwargs": {"net_arch": [64, 64], "activation_fn": torch.nn.Tanh},
        }

    def create_environment(self, scenario_path: str) -> VecNormalize:
        """Create a vectorized and normalized environment.

        Args:
            scenario_path: Path to scenario configuration file

        Returns:
            Normalized vectorized environment
        """
        config = load_scenario_config(scenario_path)

        # Create vectorized environment
        env = make_vec_env(
            VertiportEnv, n_envs=self.n_envs, env_kwargs={"config": config}
        )

        # Normalize environment
        env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.0)

        return env

    def create_model(self, env: VecNormalize, **override_params) -> PPO:
        """Create a PPO model.

        Args:
            env: Environment for training
            **override_params: Parameters to override defaults

        Returns:
            PPO model instance
        """
        # Merge parameters
        params = {**self.default_ppo_params, **self.ppo_kwargs, **override_params}

        model = PPO(
            "MultiInputPolicy", env, verbose=1, tensorboard_log=self.log_dir, **params
        )

        return model

    def create_callbacks(
        self,
        save_freq: int = 50000,
        eval_freq: int = 10000,
        n_eval_episodes: int = 5,
        name_prefix: str = "ppo_vertiport",
    ) -> list:
        """Create training callbacks.

        Args:
            save_freq: Frequency for saving checkpoints
            eval_freq: Frequency for evaluation
            n_eval_episodes: Number of episodes for evaluation
            name_prefix: Prefix for saved model names

        Returns:
            List of callbacks
        """
        checkpoint_callback = CheckpointCallback(
            save_freq=save_freq, save_path=self.model_dir, name_prefix=name_prefix
        )

        # Note: EvalCallback needs a separate environment
        # This is a simplified version - in practice you'd want a separate eval env
        callbacks = [checkpoint_callback]

        return callbacks

    def train(
        self,
        scenario_path: str,
        total_timesteps: int,
        tb_log_name: str = "PPO_Vertiport",
        save_final: bool = True,
        final_model_name: str = "ppo_vertiport_final",
        **model_params,
    ) -> PPO:
        """Train a PPO agent.

        Args:
            scenario_path: Path to scenario configuration
            total_timesteps: Total training timesteps
            tb_log_name: TensorBoard log name
            save_final: Whether to save final model
            final_model_name: Name for final model
            **model_params: Additional model parameters

        Returns:
            Trained PPO model
        """
        print("--- Starting Training ---")
        print(f"Scenario: {scenario_path}")
        print(f"Total timesteps: {total_timesteps:,}")
        print(f"Parallel environments: {self.n_envs}")

        # Create environment and model
        env = self.create_environment(scenario_path)
        model = self.create_model(env, **model_params)

        # Create callbacks
        callbacks = self.create_callbacks()

        # Train the model
        model.learn(
            total_timesteps=total_timesteps, callback=callbacks, tb_log_name=tb_log_name
        )

        print("--- Training Finished ---")

        # Save final model
        if save_final:
            final_path = os.path.join(self.model_dir, final_model_name)
            model.save(final_path)
            print(f"Final model saved to {final_path}")

        return model


def main():
    """Basic training entry point."""
    trainer = Trainer()

    # Train with default parameters
    model = trainer.train(
        scenario_path="scenarios/steady_flow.yaml", total_timesteps=5000000
    )

    print("Training complete!")


if __name__ == "__main__":
    main()
