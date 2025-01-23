
from typing import Callable, Optional, Union
import numpy as np
import inspect

from pybop import ParameterSet, Inputs
from pybop import BaseModel

# Extend this as needed to define acceptable model types
MODEL_TYPES = Union[BaseModel]


class BaseSim():
    """
    Base class for simulations (previously called models).
    This class is used to construct simulations from a parameter set and a
    model.
    This class defines the essential methods that all simulations should have
    to create a cost function.
    """

    def __init__(
            self,
            name: str = "BaseSim",
            parameter_set: Optional[Union[ParameterSet, dict]] = None,
            # Extend this to include other model types as needed
            model: Optional[MODEL_TYPES] = None
    ):
        self.name = name
        self.model = model
        self.model_arguments = set(inspect.signature(model))
        self.parameter_set = parameter_set

    def build(
            self,
    ):
        """
        If any build steps are required, they should be implemented here. 
        If this is called without being implemented, it should raise a
        NotImplementedError.
        """
        raise NotImplementedError

    def simulate(
            self,
            parameters: Union[ParameterSet, dict],
            t_eval: np.array
    ):
        """
        Simulate the model with the given parameters and t_eval.
        """
        if self.model is None:
            raise ValueError("Model has not been defined.")
        elif type(self.model) is BaseModel:
            output = self.model._simulate(
                parameters,  # The model parameters which are to be optimized
                self.parameter_set,  # Fixed parameters for the model
                t_eval,  # The time points at which the model is evaluated
            )
        else:
            # Extend this if statement to include other model types as needed
            raise NotImplementedError(f"Model is not in {MODEL_TYPES}.")
    
        return output  # TODO: Add type hinting on output
