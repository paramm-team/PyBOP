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
               inputs: Optional[Inputs] = None,
               initial_state: Optional[dict] = None
               ):
        """
        Construct the PyBaMM model, if not already built or if there are changes to any
        `rebuild_parameters` or the initial state.

        This method initializes the model components, applies the given parameters,
        sets up the mesh and discretization if needed, and prepares the model
        for simulations.
        _sim is the Simulation class this model is passed to.
        _sim.model is this model.
        _sim.parameter_set is the parameter set for the model.
        _sim.inputs is the inputs for the model.
        """
        
        if not self.model._built:
            self.model.build_model()

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
