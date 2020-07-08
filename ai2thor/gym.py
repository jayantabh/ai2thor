from ai2thor.controller import Controller
from ai2thor.server import Event
import gym
from gym.spaces import Discrete, Box
from collections import defaultdict
from typing import List, Tuple, Dict, Union, Iterable
import numpy as np
import random

class GymTHOR:
    def __init__(self,
            controller_initialization: dict=dict(),
            horizon: int=200,
            seed: int=42):
        self.controller = Controller(**controller_initialization)
        self.frame_height, self.frame_width, _ = \
            self.controller.last_event.frame.shape
        self._seed(seed)

    @property
    def observation_space(self) -> gym.spaces:
        """Returns a gym.spaces observation space. Default is the
           RGB Frame of size Box(height, width, 3) with values
           from [0:1].
        
        TODO: Link to common alternatives, like using RGB-D
        normalized frames."""
        return Box(low=0, high=1, shape=(self.frame_height,
            self.frame_width, 3), dtype=np.float64)

    @property
    def action_space(self) -> gym.spaces:
        """Returns the gym.spaces action space.
        
        Common Examples:
        * Discrete(4): 4 discrete actions, e.g.,
            0 could be RotateLeft
            1 could be MoveAhead
            2 could be RotateRight
            3 could be Done
        * Box(low=0, high=1, shape=(2, 1), dtype=np.float64):
            For 4 continuous valued actions, which could
            indicate the magnitude and direction to rotate."""
        raise NotImplementedError()

    def scene_names(self) -> Iterable[str]:
        """Returns an iterable of scene names."""
        raise NotImplementedError()

    def observation(self, event) -> np.array:
        """Returns the agent's observation at each time step. The
           default observation is the normalized RGB frame."""
        rgb_image = event.frame
        return rgb_image / 255

    def episode_done(self, event):
        raise NotImplementedError()

    def reward(self, episode_done: bool, event) -> float:
        raise NotImplementedError()

    def __enter__(self):
        """Enables entering context manager support."""
        return self

    def __exit__(self, *args) -> None:
        """Enables exiting context manager support."""
        self.controller.stop()

    def close(self):
        """Ends the controller's session."""
        self.controller.stop()

    def _seed(self, seed_num: int=42) -> None:
        """Sets the random module and numpy random seeds."""
        random.seed(seed_num)
        np.random.seed(seed_num)

    def render(self, mode=None) -> None:
        """Provides a warning that render doesn't need to be called for AI2-THOR.

        We have provided it in case somebody copies and pastes code over
        from OpenAI Gym."""
        import warnings
        warnings.warn('The render function call is unnecessary for AI2-THOR.')