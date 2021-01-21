from abc import ABC, abstractmethod


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
        self.models = []

    @abstractmethod
    def add_model(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def step(self):
        raise NotImplementedError

    def data(self) -> list:
        return [m.data for m in self.models]

    def draw(self, name=None, path="."):
        pass
        #raise NotImplementedError

    def draw_model(self, name=None, path=None):
        if len(self.models) > 0:
            self.models[0].draw(name=name, path=path)
