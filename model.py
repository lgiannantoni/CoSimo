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

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def step(self, *args, **kwargs):
        pass

    @abstractmethod
    def draw(self, name=None, path="."):
        pass