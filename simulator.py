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

    @abstractmethod
    def __init__(self):
        self.models = []
        self.data = []

    @abstractmethod
    def add_model(self, *args, **kwargs):
        pass

    @abstractmethod
    def step(self):
        pass

    def draw(self, name=None, path="."):
        for model in self.models:
            model.draw(name, path)
