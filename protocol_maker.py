import importlib
import logging
import re
import signal
from abc import ABC, abstractmethod
from pathlib import Path
from time import sleep

import yaml
from fabric import Connection

from library.common.pipeline import Pipeline
from library.common.simulator import Proxy
from library.common.utils import InputOutput
from pyro_test.pyro_test import Tester2


class ProtocolMaker(ABC):
    _simulation_pipeline = Pipeline()

    @classmethod
    def simulation_setup(cls, **kwargs):
        cls.sim_config = kwargs["META"]
        cls.sims = dict()
        for sim_name, sim_params in cls.sim_config.items():
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
                user, host, port = re.split(r'[@:]', sim_params['remote'])
                # launch remote
                # cmd = f"screen -dmS prova bash -c 'cd ~/coherence; source venv/bin/activate; python3 < {'/'.join(sim_path.split('.'))}.py - {host} {port} 2>/dev/null >/dev/null; exec bash' &"
                # TODO aggiungere il path dei simulatori ai path degli eseguibili python;
                # TODO o meglio: fare script per lanciare questa roba e aggiungerli al path
                # TODO salvare conn dentro la classe Proxy per usi futuri (es. terminare screen)?
                cmd = f"screen -dmS {sim_name} bash -c 'cd ~/coherence; source venv/bin/activate; python3 < {'/'.join(sim_mod.split('.'))}.py - {host} {port}; exec bash' &"
                print(f"cmd {cmd}")
                try:
                    # result = Connection(host, user=user).run(f"cd ~/coherence; source venv/bin/activate; python3 < {'/'.join(sim_path.split('.'))}.py 2> /dev/null > /dev/null &")
                    conn = Connection(host, user=user)  # .run(cmd)
                    result = conn.run(cmd)
                    # print("{}: {}".format(host, result.stdout.strip()))
                    sleep(
                        3)  # necessario per aspettare l'avvio del server. migliorare. n.b. il try su Proxy(...) non va: perché?
                except Exception as e:
                    raise e
                p = Proxy(f"PYRO:{sim_class}@{host}:{port}")

                cls.sims[sim_class] = p
        for sim_name, sim in cls.sims.items():
            print(type(sim))
            cls._simulation_pipeline += sim
            print(f"{sim_name} added")
        #kwargs = {"CONFIG": {"SIM_STEPS": 10}, "PATH": '.'}
        kw = dict()
        cls._simulation_pipeline.do(**kwargs)
        for sim in cls._simulation_pipeline._pipe:
            if type(sim) == Proxy:
                sim.close()

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


def test():
    SIM_CONFIG = {"META": {
            'Tester1': {
                'python': 'pyro_test.tester1:Tester1',
                'remote': 'leonardo@actarus.polito.it:9091'
            },
            'Tester2': {
                'python': 'pyro_test.pyro_test:Tester2'
            },
        }
    }

    # ipAddressServer = "0.0.0.0"
    # tester1 = Proxy('PYRO:Tester1@' + ipAddressServer + ':9090')

    # Prova.eval_protocol("aaaaaaaaaa")
    return SIM_CONFIG


def lifecycle_config():
    from library.lifecycle.data.regan_exp_data import REGAN_EXP
    from library.lifecycle.data.regan_exp_data import EXP
    config = {"LIFECYCLE_INIT_STATE": REGAN_EXP['Regan_2_proliferation2anoikis'][EXP.init_state],
            "LIFECYCLE_TIMESCALE": 1,
            "LIFECYCLE_DRAW_INTERVAL": 1,

        }
        # InputOutput.GRID_EVENTS.name: {'SPAWNED':
        #                                    {226342273803344125728680122314229309424: None,
        #                                     251400722381318013486144802793001007937: None,
        #                                     206814744286531949838648585207961370790: None,
        #                                     327463866859093737560666092480710577366: None,
        #                                     300058428272089005060538137567039257209: None,
        #                                     104105104108353130623393740016594252228: None,
        #                                     203791298355420147201781396204199291413: None,
        #                                     35466258178066977688270175797123321629: None,
        #                                     80110063412880363238205193708478292736: None,
        #                                     61450793094859548438329929150037727390: None
        #                                     }
        #                                }


    return config


def simple_grid_config():
    config = { "GRID_DIM": (50, 50, 20),
               "GRID_TIMESCALE": 1,
               "GRID_SIGNALS": ['GF', 'Trail'],
               "GRID_ADD": [
                   ["CELL", [20, 20, 6]],
                   ["CELL", [5, 6, 7], {'RADIUS': 1}],
                   ["CELL", [15, 15, 15]],
                   ["CELL", [18, 18, 5]]
               ],
               "GRID_ADD_WHERE": [
                   [{"CUBOID": {"WIDTH": 40, "DEPTH": 40, "HEIGHT": 3, "ORIGIN": [0, 0, 0]}}, "ECM"],
                   [{"TORUS": {"CENTER": [10, 10, 10], "MAJOR_RADIUS": 8, "MINOR_RADIUS": 2}}, "ECM"]
               ],
               # "GRID_ADD_WHERE": [
               #     ['x<50, y<50, z<3', "ECM", {'STIFF': True}],
               #     ['x<10, y<10, z>17', "CELL"]
               # ],
               "GRID_DRAW_INTERVAL": 0
           }
    return config


def test_serio():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)

    path = Path("./experiments/test")

    kwargs = dict()
    kwargs["CONFIG"] = dict()
    kwargs["CONFIG"]["PATH"] = path
    kwargs["CONFIG"]["GRID_CONFIG"] = simple_grid_config()
    kwargs["CONFIG"]["LIFECYCLE_CONFIG"] = lifecycle_config()
    kwargs["CONFIG"]["SIM_STEPS"] = 10
    kwargs["META"] = {
        'SimpleGrid': {
            'python': 'library.space.simple_grid:GridSimulator'
        },
        'LifecycleSimulator': {
            'python': 'library.lifecycle.models.bool_lifecycle:LifecycleSimulator',
            'remote': 'leonardo@actarus.polito.it:9666'
        },
    }

    return kwargs



if __name__ == "__main__":
    #SIM_CONFIG = test()
    SIM_CONFIG = test_serio()
    print(SIM_CONFIG)
    Prova.simulation_setup(**SIM_CONFIG)
