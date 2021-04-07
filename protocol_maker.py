import importlib
import re
import signal
from abc import ABC, abstractmethod
from time import sleep

from fabric import Connection

from library.common.pipeline import Pipeline
from library.common.simulator import Proxy
from pyro_test.pyro_test import Tester2


class ProtocolMaker(ABC):
    _simulation_pipeline = Pipeline()

    @classmethod
    def simulation_setup(cls, sim_config):
        cls.sim_config = sim_config
        cls.sims = dict()
        for sim_name, sim_params in sim_config.items():
            print(sim_name)
            try:
                sim_mod, sim_class = sim_params['python'].split(':')
            except:
                raise Exception("blablabla")
            if not "remote" in sim_params.keys():
                # launch local
                mod = importlib.import_module(sim_mod)
                mcls = getattr(mod, sim_class)
                cls.sims[sim_class] = mcls()
            else:
                #user, host = sim_params['remote'].split('@')
                user, host, port = re.split(r'[@:]', sim_params['remote'])
                # try:
                #     p = Proxy(f"PYRO:{sim_class}@{host}:{port}")
                # except:
                print("qua")
                # launch remote
                #cmd = f"screen -dmS prova bash -c 'cd ~/coherence; source venv/bin/activate; python3 < {'/'.join(sim_path.split('.'))}.py - {host} {port} 2>/dev/null >/dev/null; exec bash' &"
                #TODO aggiungere il path dei simulatori ai path degli eseguibili python;
                #TODO o meglio: fare script per lanciare questa roba e aggiungerli al path
                #TODO salvare conn dentro la classe Proxy per usi futuri (es. terminare screen)?
                cmd = f"screen -dmS {sim_name} bash -c 'cd ~/coherence; source venv/bin/activate; python3 < {'/'.join(sim_mod.split('.'))}.py - {host} {port}; exec bash' &"
                print(f"cmd {cmd}")
                try:
                    #result = Connection(host, user=user).run(f"cd ~/coherence; source venv/bin/activate; python3 < {'/'.join(sim_path.split('.'))}.py 2> /dev/null > /dev/null &")
                    conn = Connection(host, user=user) #.run(cmd)
                    result = conn.run(cmd)
                    #print("{}: {}".format(host, result.stdout.strip()))
                    sleep(3) # necessario per aspettare l'avvio del server. migliorare. n.b. il try su Proxy(...) non va: perché?
                except Exception as e:
                    raise e
                p = Proxy(f"PYRO:{sim_class}@{host}:{port}")

                cls.sims[sim_class] = p
        for sim_name, sim in cls.sims.items():
            print(type(sim))
            cls._simulation_pipeline += sim
            print(f"{sim_name} added")
        kwargs = {"CONFIG": {"SIM_STEPS": 10}, "PATH": '.'}
        cls._simulation_pipeline.do(**kwargs)
        for sim in cls._simulation_pipeline._pipe:
            if type(sim) == Proxy:
                sim.close()
        #cls.sims["Tester1"].close()

    @classmethod
    @abstractmethod
    def make_protocol(cls, *args, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def simulate_protocol(cls, *args, **kwargs):
        print("class " + cls.__name__)
        print("simulate")

    @staticmethod
    @abstractmethod
    def eval_protocol(protocol: str):
        raise NotImplementedError

#    @classmethod
#    def make(cls):
#        cls.make_protocol()
#        cls.eval_protocol("abstract")


class Prova(ProtocolMaker):
    def make_protocol(cls, *args, **kwargs):
        super().make_protocol(args, kwargs)
        pass

    def simulate_protocol(cls, *args, **kwargs):
        super().simulate_protocol(args, kwargs)
        print(cls.__name__)
        cls.simulate_protocol(Prova)
        print("class " + cls.__name__)

    @staticmethod
    def eval_protocol(protocol: str):
        print(protocol)


if __name__ == "__main__":
    SIM_CONFIG = {
        # 'SimpleGrid': {
        #     'python': 'library.space.simple_grid:GridSimulator'
        # },
        'Tester1': {
            'python': 'pyro_test.tester1:Tester1',
            'remote': 'leonardo@actarus.polito.it:9091'
        },
        'Tester2': {
            'python': 'pyro_test.pyro_test:Tester2'
        },


        #'LifecycleSimulator': {
        #    'python': 'library.lifecycle.models.bool_lifecycle:LifecycleSimulator',
        #    'remote': 'leonardo@actarus.polito.it'
        #},
    }

    #ipAddressServer = "0.0.0.0"
    #tester1 = Proxy('PYRO:Tester1@' + ipAddressServer + ':9090')

    #Prova.eval_protocol("aaaaaaaaaa")
    Prova.simulation_setup(SIM_CONFIG)
