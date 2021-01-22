from abc import ABC, abstractmethod
from collections import defaultdict

from library.common.model import IModel


class ISimulator(ABC):
    """
    The base class of each module

    ...

    Attributes
    ----------

    Methods
    -------
    """

    def __init__(self):
        self.models = defaultdict()

    @abstractmethod
    def add_model(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def step(self):
        raise NotImplementedError

    @abstractmethod
    def data(self):
        raise NotImplementedError

    def draw(self, name=None, path="."):
        pass
        #raise NotImplementedError

    def draw_model(self, name=None, path=None):
        if len(self.models) > 0:
            self.models[0].draw(name=name, path=path)
