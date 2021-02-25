from abc import ABC, abstractmethod

from PyBoolNet import InteractionGraphs


class IModel(ABC):
    """
    The base class of each model

    ...

    Attributes
    ----------

    Methods
    -------
    """

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def step(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def draw(self, name=None, path="."):
        raise NotImplementedError