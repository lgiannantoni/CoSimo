from abc import ABC, abstractmethod
from collections import defaultdict

from library.common.utils import Level, InputOutput


class ISimulator(ABC):
    """
    The base class of each simulator
    ...
    Attributes
    ----------
    _in : list
        list of params required as input
    _remove : list
        list of params that will removed from input
    _add : list
        list of params that will added from input
    name : list
        Simulator's name
    Methods
    -------
    __add__(other)
        To build the pipeline dynamically
    do(*args,**kwargs)
        Abstract method that will be called by the pipeline
    ...
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
        Create a pipeline by adding two simulators
        Parameters
        ----------
        other : ISimulator
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
    def remove_model(self, *args, **kwargs):
        # TODO
        pass

    @abstractmethod
    def step(self, *args, **kwargs) -> (tuple, dict):
        """Abstract method that will be called by the pipeline
                Parameters
                ----------
                args :list
                    list of params that will used by the simulator
                kwargs: dict
                    dict of params that will passed by the simulator
                """
        if InputOutput.DEBUG.name in kwargs.keys():
            self.level = kwargs[InputOutput.DEBUG.name]
        pass

    def __repr__(self):
        return self._name

    def __str__(self):
        return self._name

    @abstractmethod
    def data(self):
        raise NotImplementedError

    def draw(self, name=None, path="."):
        pass
        #raise NotImplementedError

    def draw_model(self, name=None, path=None):
        if len(self.models) > 0:
            self.models[0].draw(name=name, path=path)
