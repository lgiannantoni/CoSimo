import importlib
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from time import sleep

from fabric import Connection

from library.common.pipeline import Pipeline
from library.common.simulator import Proxy
from library.common.utils import InputOutput
from library.space.simple_grid import GridObjectType, SimpleGridOpt


class ProtocolMaker(ABC):
    _simulation_pipeline = Pipeline()
    sims = None

    @classmethod
    def simulation_setup(cls, kwargs):
        meta_config = kwargs
        cls.sims = dict()
        for sim_name, sim_params in meta_config.items():
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
                cmd = f"screen -dmS {sim_name} bash -c 'cd ~/coherence; source venv3.9/bin/activate; python3 < {'/'.join(sim_mod.split('.'))}.py - {host} {port}; exec bash' &"
                print(f"cmd {cmd}")
                try:
                    # result = Connection(host, user=user).run(f"cd ~/coherence; source venv/bin/activate; python3 < {'/'.join(sim_path.split('.'))}.py 2> /dev/null > /dev/null &")
                    conn = Connection(host, user=user)  # .run(cmd)
                    result = conn.run(cmd)
                    # print("{}: {}".format(host, result.stdout.strip()))
                    sleep(10)  # necessario per aspettare l'avvio del server. migliorare. n.b. il try su Proxy(...) non va: perché?
                except Exception as e:
                    raise e
                p = Proxy(f"PYRO:{sim_class}@{host}:{port}")

                cls.sims[sim_class] = p
        for sim_name, sim in cls.sims.items():
            print(type(sim))
            cls._simulation_pipeline += sim
            print(f"{sim_name} added")
        print("Simulation setup done.")

    @classmethod
    def simulation_start(cls, kwargs):
        print("Simulation starting up")
        #try:
        cls._simulation_pipeline.do(**kwargs)
        #except Exception as e:
        #    print(e)
        #    cls.simulation_shutdown()
        print("Simulation finished")

    @classmethod
    def simulation_shutdown(cls):
        #TODO spostare nella Pipeline (accesso a _pipe...)
        for sim in cls._simulation_pipeline._pipe:
            if type(sim) == Proxy:
                print(f"Shutting down remote simulator {sim}")
                # https://pyro4.readthedocs.io/en/stable/clientcode.html#proxies-connections-threads-and-cleaning-up
                sim._pyroRelease()
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
    # def make_protocol(cls, *args, **kwargs):
    #     super().make_protocol(args, kwargs)
    #     pass
    #
    # def simulate_protocol(cls, *args, **kwargs):
    #     super().simulate_protocol(args, kwargs)
    #     #cls.simulate_protocol(Prova)
    #     print("class " + cls.__name__)

    @staticmethod
    def eval_protocol(protocol: str):
        print(protocol)


def prova():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)

    path = Path("./experiments/test")

    kwargs = dict()
    kwargs["PATH"] = str(path)
    kwargs["CONFIG"] = dict()
    kwargs["CONFIG"]["GRID_CONFIG"] = simple_grid_config()
    kwargs["CONFIG"]["LIFECYCLE_CONFIG"] = lifecycle_config()
    kwargs["CONFIG"]["SIM_STEPS"] = 10
    kwargs["META"] = {
            'Tester1': {
                'python': 'pyro_test.tester1:Tester1',
                'remote': 'leonardo@actarus.polito.it:9091'
                #'remote': 'lg@0.0.0.0:9091'
            },
            'Tester2': {
                'python': 'pyro_test.pyro_test:Tester2'
            },
        }

    # ipAddressServer = "0.0.0.0"
    # tester1 = Proxy('PYRO:Tester1@' + ipAddressServer + ':9090')

    # Prova.eval_protocol("aaaaaaaaaa")
    return kwargs


def lifecycle_config():
    from library.lifecycle.data.regan_exp_data import REGAN_EXP
    from library.lifecycle.data.regan_exp_data import EXP
    config = {"LIFECYCLE_INIT_STATE": REGAN_EXP['Regan_2_proliferation2anoikis'][EXP.init_state],
            "LIFECYCLE_TIMESCALE": 1,
            "LIFECYCLE_DRAW_INTERVAL": 1,

        }
    return config


def simple_grid_config():
    config = { SimpleGridOpt.GRID_DIM.name: (50, 50, 20),
               SimpleGridOpt.GRID_TIMESCALE.name: 1,
               SimpleGridOpt.GRID_SIGNALS.name: ['GF', 'Trail'],
               SimpleGridOpt.GRID_ADD.name: [
                   [GridObjectType.CELL.name, [20, 20, 6]],
                   [GridObjectType.CELL.name, [5, 6, 7], {'RADIUS': 1}],
                   [GridObjectType.CELL.name, [15, 15, 15]],
                   [GridObjectType.CELL.name, [18, 18, 5]]
               ],
               SimpleGridOpt.GRID_ADD_WHERE.name: [
                   [{"CUBOID": {"WIDTH": 40, "DEPTH": 40, "HEIGHT": 3, "ORIGIN": [0, 0, 0]}}, "ECM"],
                   [{"TORUS": {"CENTER": [10, 10, 10], "MAJOR_RADIUS": 8, "MINOR_RADIUS": 2}}, "ECM"]
               ],
               # "GRID_ADD_WHERE": [
               #     ['x<50, y<50, z<3', "ECM", {'STIFF': True}],
               #     ['x<10, y<10, z>17', "CELL"]
               # ],
               SimpleGridOpt.GRID_DRAW_INTERVAL.name: 0
           }
    return config


def prova_seria():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)

    path = Path("./experiments/test")

    kwargs = dict()
    kwargs[InputOutput.PATH.name] = str(path)
    kwargs[InputOutput.CONFIG.name] = dict()
    kwargs[InputOutput.CONFIG.name][InputOutput.GRID_CONFIG.name] = simple_grid_config()
    kwargs[InputOutput.CONFIG.name][InputOutput.LIFECYCLE_CONFIG.name] = lifecycle_config()
    kwargs[InputOutput.CONFIG.name][InputOutput.SIM_STEPS.name] = 10
    kwargs[InputOutput.META.name] = {
        'SimpleGrid': {
            'python': 'library.space.simple_grid:GridSimulator',
            #'remote': 'leonardo@actarus.polito.it:9999'
            #'remote': 'lg@127.0.0.1:9999'
        },
        'LifecycleSimulator': {
            'python': 'library.lifecycle.models.bool_lifecycle:LifecycleSimulator',
            'remote': 'leonardo@actarus.polito.it:9666'
        },
    }

    return kwargs



if __name__ == "__main__":
    #SIM_CONFIG = prova()
    SIM_CONFIG = prova_seria()
    print(SIM_CONFIG)
    Prova.simulation_setup(SIM_CONFIG["META"])
    try:
        Prova.simulation_start(SIM_CONFIG)
    except:
        Prova.simulation_shutdown()
    finally:
        Prova.simulation_shutdown()
