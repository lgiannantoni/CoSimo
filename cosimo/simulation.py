import importlib
import logging
import re
from abc import ABC, abstractmethod

from cosimo.pipeline import Pipeline
from cosimo.simulator import Proxy
from cosimo.utils import AdvEnum


# class SimConfig(AdvEnum):
#     STEPS = 0
#     SHUTDOWN = 1
#     SIMS = 2


class SimType(AdvEnum):
    PYTHON = 3
    CMD = 4
    REMOTE = 5
    CONNECT = 6


class Simulation(ABC):
    _simulation_pipeline: Pipeline = None
    _meta_config = None
    _shutdown = False

    def __new__(cls, *args, **kwargs):
        cls.setup(*args, **kwargs)

    @classmethod
    def setup(cls, *args, **kwargs):
        if cls._simulation_pipeline:
            cls._simulation_pipeline.shutdown()
        cls._simulation_pipeline = Pipeline()
        if not cls._meta_config:
            assert kwargs, "pipppeeeee"
            if 'shutdown' in kwargs:
                cls._shutdown = kwargs['shutdown']
                del kwargs['shutdown']
            cls._meta_config = kwargs
        _sims = dict()
        for sim_name, sim_params in cls._meta_config.items():
            assert all([s.upper() in SimType.names() for s in sim_params.keys()]), "altre pippppeeeeeee"
            try:
                sim_mod, sim_class = sim_params['python'].split(':')
            except:
                raise Exception("blablabla")
            if not "remote" in sim_params.keys():
                # launch local
                mod = importlib.import_module(sim_mod)
                mcls = getattr(mod, sim_class)
                _sims[sim_class] = mcls()
            else:
                user, host, port = re.split(r'[@:]', sim_params['remote'])
                try:
                    p = Proxy(user=user, host=host, port=port, sim_name=sim_name, sim_class=sim_class,
                              sim_module=sim_mod)
                except Exception as e:
                    raise e
                _sims[sim_class] = p
        for sim_name, sim in _sims.items():
            cls._simulation_pipeline += sim
            logging.info(f"Simulator {sim_name} added")
        print("Simulation setup done.")

    @classmethod
    def start(cls, *args, **kwargs):
        print("Simulation starting up")
        try:
            cls._simulation_pipeline.do(**kwargs)
        except Exception as e:
            logging.error(e)
        #     cls.shutdown()
        # finally:
        #     if cls._shutdown:
        #         cls.shutdown()
        print("Simulation finished.")

    @classmethod
    def shutdown(cls):
        logging.info("Shutting down simulation.")
        cls._simulation_pipeline.shutdown()

    #TODO fatti furbo
    @classmethod
    def reset(cls):
        cls._simulation_pipeline.reset()

    @classmethod
    @abstractmethod
    def results(cls, *args, **kwargs):
        pass
