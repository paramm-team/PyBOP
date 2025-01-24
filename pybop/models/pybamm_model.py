import numpy as np
import pybamm
from typing import Optional

from pybop import Parameters
from pybop.models import BaseModel
from pybop.parameters.parameter import Inputs


class PyBaMMBase(BaseModel):
    """
    Class for defining a PyBaMM model, specific PyBaMM models should inherit 
    and extend.
    """
    def __init__(
            self,
            model: pybamm.BaseModel,
            name: str = "PyBaMMBase",
    ):
        super().__init__(model, name)
        self.geometric_parameters = self.set_geometric_parameters()

    def _simulate(
            self,
            parameters: pybamm.ParameterValues,
            parameter_set: pybamm.ParameterValues,
            t_eval: np.array
    ):
        """
        Simulate the model with the given parameters and t_eval.
        """
        return self.model.default_solver().solve(
            self.model,
            t_eval,
            inputs=parameters,
            parameter_values=parameter_set,
        )['solution']

    def _build(self, _sim,
               parameters: Optional[Parameters] = None,
               inputs: Optional[Inputs] = None):
        """
        Build the model.
        _sim is the Simulation class this model is passed to.
        _sim.model is this model.
        _sim.parameter_set is the parameter set for the model.
        _sim.inputs is the inputs for the model.
        """
        inputs = self.classify_parameters(_sim, parameters, inputs=inputs)

        if not self.model._built:
            self.model.build_model()

    def classify_parameters(self, _sim,
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
        _sim.parameters = parameters or _sim.parameters
        parameter_dictionary = _sim.parameters.as_dict()
        parameter_dictionary.update(inputs or {})

        rebuild_parameters = {
            param: parameter_dictionary[param]
            for param in parameter_dictionary
            if param in self.geometric_parameters
        }
        standard_parameters = {
            param: parameter_dictionary[param]
            for param in parameter_dictionary
            if param not in self.geometric_parameters
        }

        for key in standard_parameters.keys():
            _sim._parameter_set[key] = "[input]"

        if rebuild_parameters:
            requires_rebuild = False
            # A rebuild is required if any of the rebuild parameter values
            # have changed
            for key, value in rebuild_parameters.items():
                if value != _sim._unprocessed_parameter_set[key]:
                    requires_rebuild = True
            if requires_rebuild:
                self.clear()
                self._geometry = self.model.default_geometry
                # Update both the active and unprocessed parameter sets for
                # consistency
                _sim._parameter_set.update(rebuild_parameters)
                _sim._unprocessed_parameter_set.update(rebuild_parameters)

        return standard_parameters

    def set_geometric_parameters(self):
        """
        Set the geometric parameters for the model using the default geometry
        in the pybamm model.
        Overwrite this method in the child class to set the geometric
        parameters.
        The return values are the geometric parameters for the model with no
        values.
        """
        return dict.fromkeys(self.model.default_geometry.keys())
