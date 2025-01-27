
from typing import Optional, Union

import pybamm
from pybamm import Simulation

from pybop import Parameters, ParameterSet, Inputs
from pybop import BaseSim
from pybop import PyBaMMBase


# Extend MODEL_TYPES to include the PyBaMM model class
MODEL_TYPES = Union[PyBaMMBase]


class PyBaMMSim(BaseSim, Simulation):
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
        BaseSim().__init__(name, parameter_set, model)
        if False:
            # TODO: Enable this if all Simulation requirements are met
            Simulation().__init__(self, *args, **kwargs)  # noqa: F821
        else:
            # Define the Simulation attributes via some getters

            @property
            def _model(self):
                """ Return the PyBaMM model. """
                return self.model.model

            @property
            def _unprocessed_parameter_values(self):
                """ Return the unprocessed parameter set. """
                assert self._unprocessed_parameter_set is not None, \
                    "unprocessed_parameter_set is not set."
                return self._unprocessed_parameter_set

            # TODO: Implement setters if needed to either nullify or set


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
        self._unprocessed_parameter_set = self._parameter_set.copy()

    def build(
            self,
            parameters: Optional[ParameterSet] = None,
            inputs: Optional[Union[dict, Inputs]] = None,
            initial_state: Optional[dict] = None
    ):
        inputs = self.classify_parameters(parameters=parameters, inputs=inputs)
        if initial_state is not None:
            self.set_initial_state(initial_state, inputs=inputs)

        # Call the build method of BaseSim to build the model from its own
        # methods, this works like super().__init__ or BaseSim.__init__ as here
        BaseSim().build(parameters=parameters, inputs=inputs)

    def set_initial_state(self, initial_state: dict, inputs: Optional[dict] = None):
        """
        Set the initial state of the model.
        """
        self.model.clear() #  TODO: Determine if this is a sim (self) or model (self.model) method

        self.model._set_initial_state(initial_state=initial_state, inputs=inputs)

        self._parameter_set = self._unprocessed_parameter_set.copy()

    def _set_initial_state(self, initial_state: dict, inputs: Optional[Inputs] = None):
        """
        Set the initial state of charge or concentrations for the battery model.

        Parameters
        ----------
        initial_state : dict
            A valid initial state, e.g. the initial state of charge or open-circuit voltage.
        inputs : Inputs
            The input parameters to be used when building the model.
        """
        initial_state = self.convert_to_pybamm_initial_state(initial_state)

        if not self.pybamm_model._built:  # noqa: SLF001
            self.pybamm_model.build_model()

        # Temporary construction of attributes for PyBaMM
        self._model = self.pybamm_model
        self._unprocessed_parameter_values = self._unprocessed_parameter_set

        # Set initial state via PyBaMM's Simulation class
        Simulation.set_initial_soc(self, initial_state, inputs=inputs)

        # Update the default parameter set for consistency
        self._unprocessed_parameter_set = self._parameter_values

        # Clear the pybamm objects
        del self._model
        del self._unprocessed_parameter_values
        del self._parameter_values

    def classify_parameters(self,
                            parameters: Optional[Parameters] = None,
                            inputs: Optional[Inputs] = None):
        """
        Check for any 'rebuild_parameters' which require a model rebuild and
        update the unprocessed_parameter_set if a rebuild is required.

        Parameters
        ----------
        parameters : Parameters, optional
            The optimisation parameters. Defaults to None, resulting in the 
            internal `pybop.Parameters` object to be used.
        inputs : Inputs, optional
            The input parameters for the simulation (default: None).
        """
        self.parameters = parameters or self.parameters
        parameter_dictionary = self.parameters.as_dict()
        parameter_dictionary.update(inputs or {})

        rebuild_parameters = {
            param: parameter_dictionary[param]
            for param in parameter_dictionary
            if param in self.model.geometric_parameters
        }
        standard_parameters = {
            param: parameter_dictionary[param]
            for param in parameter_dictionary
            if param not in self.model.geometric_parameters
        }

        for key in standard_parameters.keys():
            self._parameter_set[key] = "[input]"

        if rebuild_parameters:
            requires_rebuild = False
            # A rebuild is required if any of the rebuild parameter values
            # have changed
            for key, value in rebuild_parameters.items():
                if value != self._unprocessed_parameter_set[key]:
                    requires_rebuild = True
            if requires_rebuild:
                self.clear()
                self._geometry = self.model.default_geometry
                # Update both the active and unprocessed parameter sets for
                # consistency
                self._parameter_set.update(rebuild_parameters)
                self._unprocessed_parameter_set.update(rebuild_parameters)

        return standard_parameters