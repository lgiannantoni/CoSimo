from abc import ABC, abstractmethod

from cosimo.utils import UniqueIdMap


class IModel(ABC):
    """
    The base class of each model

    ...

    Attributes
    ----------

    Methods
    -------
    """

    unique_id_map = UniqueIdMap()

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def unique_id(cls, obj):
        """Produce a unique integer id for the object.

        Object must be *hashable*. Id is a UUID and should be unique
        across Python invocations.

        """
        #return cls.unique_id_map[obj].int
        return cls.unique_id_map[obj]

    @abstractmethod
    def step(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def draw(self, name=None, path="."):
        raise NotImplementedError