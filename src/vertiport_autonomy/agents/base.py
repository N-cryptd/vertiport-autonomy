"""Abstract base class for all agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict

import numpy as np


class BaseAgent(ABC):
    """Abstract base class for vertiport autonomy agents."""

    def __init__(self, name: str):
        """Initialize the agent.

        Args:
            name: Human-readable name for the agent
        """
        self.name = name

    @abstractmethod
    def act(self, observation: Dict[str, Any]) -> np.ndarray:
        """Select actions based on the current observation.

        Args:
            observation: Current environment observation

        Returns:
            Array of actions for each drone
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset agent state for a new episode."""
        pass

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"
