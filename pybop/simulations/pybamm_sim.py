
from typing import Optional, Union

import pybamm

from pybop import ParameterSet
from pybop import BaseSim
from pybop import PyBaMMBase


# Extend MODEL_TYPES to include the PyBaMM model class
MODEL_TYPES = Union[PyBaMMBase]


class PyBaMMSim(BaseSim):
    """
    Extension to the BaseSim class to include specifics for the PyBaMM model
    class.
    """

    def __init__(
            self,
            name: str = "BaseSim",
            parameter_set: Optional[Union[ParameterSet, dict]] = None,
            # Extend this to include other model types as needed
            model: Optional[MODEL_TYPES] = None,
    ):
        super().__init__(name, parameter_set, model)

    def __init_parameters__(self, parameter_set):
        """ Called by BaseSim.__init__ to set the parameter set. """
        if parameter_set is None:
            self._parameter_set = None
        elif isinstance(parameter_set, dict):
            self._parameter_set = pybamm.ParameterValues(parameter_set).copy()
        elif isinstance(parameter_set, pybamm.ParameterValues):
            self._parameter_set = parameter_set.copy()
        elif isinstance(parameter_set, ParameterSet):  # a pybop parameter set
            self._parameter_set = \
                pybamm.ParameterValues(parameter_set.params).copy()
        else:
            raise ValueError("Parameter set must be a dictionary, PyBop\
                             ParameterSet, pybamm.ParameterValues, or none.")
