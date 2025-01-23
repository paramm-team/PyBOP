
from typing import Callable, Optional, Union
import numpy as np
import inspect

from pybop import ParameterSet


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
            parameter_set: Optional[ParameterSet] = None,
            model: Optional[Callable] = None,
    ):
        self.model = model
        self.model_arguments = set(inspect.signature(model))


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
        # Convert the parameters to a dictionary if it is a ParameterSet
        if isinstance(ParameterSet):
            parameters = parameters.to_dict()

        # Check that any function arguments that are not specified in
        # parameters have a default value
        for arg in self.model_arguments.parameters:
            if arg == "t_eval":
                continue
            if arg not in parameters.keys():
                assert arg.default is not inspect.Parameter.empty, f"Parameter\
                {arg} is not specified and does not have a default value."

        output = self.model(t_eval=t_eval, **parameters)
        return output
