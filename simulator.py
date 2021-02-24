from abc import ABC, abstractmethod
from collections import defaultdict

from library.common.model import IModel
from library.utils import Level


class ISimulator(ABC):
    """
    The base class of each module

    ...

    Attributes
    ----------

    Methods
    -------
    """
    level = Level.NOTSET

    def __init__(self, _in: list, _remove: list, _add: list, name: str = ""):
        self.models = defaultdict()
        self._input = set(_in)
        self._remove = set(_remove)
        self._add = set(_add)
        self._name = name

    def input_list(self) -> set:
        return self._input

    def remove_list(self) -> set:
        return self._remove

    def add_list(self) -> set:
        return self._add

    def __add__(self, other):
        """To build the pipeline dynamically
        Create a pipeline by adding two modules
        Parameters
        ----------
        other : Module
        """
        if isinstance(other, ISimulator):
            from library.common.pipeline import Pipeline
            return Pipeline(self, other)
        else:
            raise TypeError("The second arg is not a {} object".format(ISimulator))


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
