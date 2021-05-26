import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from time import sleep

import Pyro4
from fabric import Connection

from cosimo.utils import Level, InputOutput


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
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
        self._models = defaultdict()
        self._input = list(set(_in))
        self._remove = list(set(_remove))
        self._add = list(set(_add))
        self._name = name

    @classmethod
    def serve(cls, host="127.0.0.1", port=9090, ns=False, verbose=False):
        cls.daemon = Pyro4.Daemon(host=host, port=port)  # custom daemon to control shutdown
        Pyro4.Daemon.serveSimple(
            {
                cls: cls.__name__
            },
            daemon=cls.daemon, ns=ns, verbose=verbose)
        print(f"{cls.__name__} execution terminated.")

    @Pyro4.expose
    def close(self):
        logging.info(f"Shutting down remote simulator {self.__class__.__name__}")
        Pyro4.Daemon.close(self.__class__.daemon)
        self.__class__.daemon = None
        print(f"{self.__class__.__name__} daemon shut down.")

        # https://pyro4.readthedocs.io/en/stable/clientcode.html#proxies-connections-threads-and-cleaning-up
        # self._pyroRelease()
        # self.close()

    @Pyro4.expose
    @abstractmethod
    def reset(self):
        raise NotImplementedError

    @property
    def models(self):
        return self._models

    @models.setter
    def models(self, value):
        self._models = value

    @property
    def input_list(self) -> list:
        return self._input

    @input_list.setter
    def input_list(self, value):
        self._input = list(set(value))

    @property
    def remove_list(self) -> list:
        return self._remove

    @remove_list.setter
    def remove_list(self, value):
        self._remove = list(set(value))

    @property
    def add_list(self) -> list:
        return self._add

    @add_list.setter
    def add_list(self, value):
        self._add = list(set(value))

    @property
    def name(self) -> str:
        return self._name

    def __add__(self, other):
        """To build the pipeline dynamically
        Create a pipeline by adding two simulators
        Parameters
        ----------
        other : ISimulator
        """
        if isinstance(other, ISimulator):
            from cosimo.pipeline import Pipeline
            return Pipeline(self, other)
        else:
            raise TypeError("The second arg is not a {} or {} object".format(ISimulator, Proxy))

    @abstractmethod
    def add_model(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def remove_model(self, *args, **kwargs):
        # TODO
        pass

    @abstractmethod
    @Pyro4.expose
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
        # raise NotImplementedError

    def draw_model(self, name=None, path=None):
        if len(self.models) > 0:
            self.models[0].draw(name=name, path=path)


class Proxy(Pyro4.Proxy):
    """

    """
    level = Level.NOTSET

    def __init__(self, *args, **kwargs):
        # try:
        #     self._pyroReconnect(tries=100)
        # except:
        user = kwargs['user']
        host = kwargs['host']
        port = kwargs['port']
        sim_class = kwargs['sim_class']
        sim_mod = kwargs['sim_module']
        sim_name = kwargs['sim_name'] if kwargs['sim_name'] else sim_class
        # launch remote
        # cmd = f"screen -dmS prova bash -c 'cd ~/coherence; source venv/bin/activate; python3 < {'/'.join(sim_path.split('.'))}.py - {host} {port} 2>/dev/null >/dev/null; exec bash' &"
        # TODO aggiungere il path dei simulatori ai path degli eseguibili python;
        # TODO o meglio: fare script per lanciare questa roba e aggiungerli al path
        # TODO salvare conn dentro la classe Proxy per usi futuri (es. terminare screen)?
        cmd = f"screen -admS {sim_name} bash -c 'cd ~/coherence; source venv3.9/bin/activate; python3 < {'/'.join(sim_mod.split('.'))}.py - {host} {port}; exec bash' &"
        conn = Connection(host, user=user)  # .run(cmd)
        result = conn.run(cmd)
        sleep(10)  # necessario per aspettare l'avvio del server. migliorare. n.b. il try su Proxy(...) non va: perché?
        super().__init__(uri=f"PYRO:{sim_class}@{host}:{port}")

    def __add__(self, other):
        """To build the pipeline dynamically
        Create a pipeline by adding two simulators
        Parameters
        ----------
        other : ISimulator or Proxy
        """
        if isinstance(other, ISimulator) or isinstance(other, Proxy):
            from cosimo.pipeline import Pipeline
            return Pipeline(self, other)
        else:
            raise TypeError("The second arg is not a {} or {} object".format(ISimulator, Proxy))

    # def shutdown(self):
    #     logging.info(f"Shutting down remote simulator {self}")
    #     # https://pyro4.readthedocs.io/en/stable/clientcode.html#proxies-connections-threads-and-cleaning-up
    #     self._pyroRelease()
    #     self.close()

    def __del__(self):
        logging.info(f"Shutting down remote simulator {self}")
        self._pyroRelease()
        self.close()
