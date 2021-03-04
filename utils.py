import logging
import random
from collections import defaultdict
from enum import Enum
from uuid import uuid4
from weakref import WeakKeyDictionary


class UniqueIdMap(WeakKeyDictionary):
    def __init__(self, dict=None):
        super().__init__(self)
        # replace data with a defaultdict to generate uuids
        self.data = defaultdict(uuid4)
        if dict is not None:
            self.update(dict)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AdvEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_name_value(cls):
        return list(map(lambda c: (c.name, c.value), cls))

    @classmethod
    def names(cls):
        return list(map(lambda c: c.name, cls))

    @classmethod
    def random(cls):
        return random.choice(list(cls))


class Level(AdvEnum):
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class InputOutput(AdvEnum):
    DEBUG = -8
    NONE = -2
    ALL = -1
    PATH = 0
    CONFIG = 1
    DIGEST = 2
    PLACING = 3
    STIMULI = 4
    GRID_CONFIG = 6
    GRID_EVENTS = 7
    LIFECYCLE_CONFIG = 8
    LIFECYCLE_EVENTS = 9
    PROTOCOL = 10


    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        else:
            return super.__eq__(self, other)

    def __hash__(self):
        return super().__hash__()
