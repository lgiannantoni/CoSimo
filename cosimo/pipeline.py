import datetime
import logging
import os
import time
from pathlib import Path
from typing import List, Union

from cosimo.simulator import ISimulator, Proxy
from cosimo.utils import Level, IO

from Pyro4.util import getPyroTraceback


class Pipeline:
    """
    A class used manage a pipeline
    ...
    Attributes
    ----------
    arg : list
        list of Modules
    Methods
    -------
    __add__(other)
        To build the pipeline dynamically
    do(*args,**kwargs)
        Executes the pipeline
    set_level(Level)
            Sets the level of log
    """

    debug_path = None

    def __init__(self, *args):
        """
        Parameters
        ----------
         arg : list
            list of Modules
        """
        Pipeline.debug_path = Path("./_debug_output")
        self._pipe: List[Union[ISimulator, Proxy]] = []
        self._output = list()
        self._stop = False
        self.level = Level.DEBUG
        for module in args:
            self.__add__(module)

    def __add__(self, other):
        """To build the pipeline dynamically
        Add new modules to the pipeline ( It checks if the pipeline is consistent)
        Parameters
        ----------
        other : Pipeline, Module
            Module to add to the pipeline or a Pipeline to marge
        """

        if isinstance(other, ISimulator) or isinstance(other, Proxy):
            other = [other]
        elif isinstance(other, Pipeline):
            other = other._pipe
        else:
            raise TypeError("The pipeline can accept only {} and {} objects".format(ISimulator, Proxy))

        for module in other:
            l_pipe = len(self._pipe)
            if isinstance(module, ISimulator) or isinstance(module, Proxy):
                if l_pipe == 0:
                    self._pipe.append(module)
                    self._output = list(set(self._output) | set(module.input_list))
                else:
                    tmp = list(set(module.input_list) - set(self._output))
                    if len(tmp) != 0:
                        raise TypeError(
                            "The output of module {} is not compatible with the input of module {}".format(l_pipe - 1,
                                                                                                           l_pipe))
                    else:
                        self._pipe.append(module)

                for el in module.remove_list:
                    self._output.remove(el)

                self._output = list(set(self._output) | set(module.add_list))

            else:
                raise TypeError("The pipeline can accept only {} or {} objects".format(ISimulator, Proxy))
        return self

    def __iadd__(self, other):
        self.__add__(other)
        return self

    def do(self, *args, **kwargs):
        """Executes the pipeline
        Parameters
        ----------
        args :list
            list of params that will passed to the first Module
        kwargs: dict
            dict of params that will passed to the first Module
        """
        logging.info(f"Start pipeline.")
        start_pipeline = time.time()
        if self.level == Level.DEBUG and IO.PATH.name in kwargs.keys():
            Pipeline.debug_path = Path(kwargs[IO.PATH.name]) / "_debug_output"
            if not Pipeline.debug_path.exists():
                logging.debug("Debug folder not found. Creating folder.")
                try:
                    os.mkdir(Pipeline.debug_path)
                except OSError:
                    logging.debug("Creation of the directory %s failed." % Pipeline.debug_path)
                else:
                    logging.debug("Directory %s successfully created." % Pipeline.debug_path)
            else:
                logging.debug("Debug folder found.")

        logging.info(f"Starting simulation pipeline.")
        #start_time = time.time()
        for _ in range(int(kwargs[IO.CONFIG.name]["SIM_STEPS"])):
            if IO.STOP_SIMULATION.name in kwargs or self.stop:
                logging.debug(f"In pipeline: stopping simulation (STOP_SIMULATION: {kwargs[IO.STOP_SIMULATION.name]}, self.stop: {self.stop})")

            else:
                for module in self._pipe:
                    #logging.debug(f"Start: {str(module)}")
                    #start_time = time.time()
                    if args is None:
                        args = ()
                    if kwargs is None:
                        kwargs = {}
                    kwargs[IO.DEBUG.name] = self.level
                    kwargs[IO.DEBUG_PATH.name] = str(Pipeline.debug_path)
                    try:
                        args, kwargs = module.step(*args, **kwargs)
                    except Exception as e:
                        logging.error(f"In pipeline: module {module}: {e}.")
                        logging.error("".join(getPyroTraceback()))
                        self.shutdown()
                        return
                    #logging.debug(f"End in: {(time.time() - start_time):.2f} sec")

        logging.info(f"End pipeline in: {str(datetime.timedelta(seconds=(time.time() - start_pipeline)))}")

        return args, kwargs

    def reset(self):
        for sim in self._pipe:
            sim.reset()

    def set_level(self, level: Level):
        """Sets the level of log
        Parameters
        ----------
        level: Level
            The level selected for logging ( Default= NOTSET )
        """
        self.level = level

    @property
    def stop(self) -> bool:
        return self._stop

    @stop.setter
    def stop(self, val: bool = True):
        self._stop = True

    def shutdown(self):
        logging.info("Shutting down pipeline.")
        for module in self._pipe:
            if type(module) == Proxy:
                #module.shutdown()
                module.close()

    def __str__(self):
        return "Pipeline(%s)" % ",".join([str(i) for i in self._pipe])
