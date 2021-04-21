import logging
import random
import sys
from collections import defaultdict
from enum import Enum
from weakref import WeakKeyDictionary
from uuid import uuid4

import Pyro4
from Pyro4.util import SerializerBase

Pyro4.config.SERIALIZER = "serpent"


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


class Objectless:
    def __new__(cls, *args, **kwargs):
        raise RuntimeError('%s should not be instantiated' % cls)


# python black magic FTW
class AdvEnum(Enum):
    # NEEDED, WTF
    SerializerBase.unregister_class_to_dict(Enum)

    def __init__(self, *args, **kwargs):
        #logging.debug(f"Registering serialization and deserialization hooks for class {self.__class__.__name__}")
        SerializerBase.register_class_to_dict(self.__class__, AdvEnum.__class_to_dict__)
        SerializerBase.register_dict_to_class(self.__class__.__name__, AdvEnum.__dict_to_class__)

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

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        else:
            return super.__eq__(self, other)

    def __hash__(self):
        return super().__hash__()

    def __repr__(self):
        return f"<'Enum' {self.__class__.__name__}.{self.name}: {self.value}>"

    # serialization hook
    @staticmethod
    def __class_to_dict__(obj):
        #print(f"----serializer hook, converting to dict: {obj.__repr__()}")
        d = {
            '__class__': obj.__class__.__name__,
            'name-attribute': obj.name,  # str(obj)
            'value-attribute': obj.value
        }
        return d

    # deserialization hook
    @staticmethod
    def __dict_to_class__(classname, d):
        #print(f"----deserializer hook, converting {d} to class: {classname}")
        value = d["value-attribute"]
        name = d["name-attribute"]
        clazz = d["__class__"]
        # if not clazz in custom_enums:
        #    raise Exception(f"{clazz} not in custom_enums {custom_enums}")
        # print(getattr(eval(clazz), name), type(getattr(eval(clazz), name)))
        return getattr(eval(clazz), name)  # return eval(name)


class Level(AdvEnum):
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class InputOutput(AdvEnum):
    DEBUG = -8
    NONE = -2
    ALL = -1
    PATH = 0
    DEBUG_PATH = 42
    CONFIG = 1
    DIGEST = 2
    PLACING = 3
    STIMULI = 4
    GRID_CONFIG = 6
    GRID_EVENTS = 7
    LIFECYCLE_CONFIG = 8
    LIFECYCLE_EVENTS = 9
    DEMIURGOS_EVENTS = -77
    PROTOCOL = 10
    META = -42
    SIM_STEPS = -666
