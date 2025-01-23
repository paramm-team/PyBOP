from typing import Callable, Optional, Union
import inspect

from pybop import ParameterSet, Parameters
from pybop.models import BaseModel


def wrap_callable_model(model: Callable, time_variable_name: str) -> Callable:
    """
    Wrap a function that does not use t_eval for its time variable.

    Parameters
    ----------
    model : Callable
        The callable model function.

    Returns
    -------
    Callable
        A Callable object with the time variable changed to t_eval.
    """
    model_signature = inspect.signature(model)
    assert time_variable_name in model_signature.parameters, \
        f"Time variable {time_variable_name} not found in model's signature."
    new_signature = [
        param.replace(name='t_eval') if param.name == time_variable_name
        else param
        for param in model_signature.values()
    ]

    def new_model(*args, **kwargs):
        bound_args = new_signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        # Map the renamed argument back to the original argument name
        original_args = {
            (time_variable_name if k == 't_eval' else k): v
            for k, v in bound_args.arguments.items()
            }
        return model(**original_args)
    # Apply the new signature to the new model
    new_model.__signature__ = new_signature
    # Return the callable model with a signature that uses t_eval
    return new_model


class CallableModel(BaseModel):
    """
    Class for defining a basic callable model.
    The model must be a callable function with t_eval.
    """

    def __init__(
            self,
            model: Callable,
            name: str = "Callable",
    ):
        super().__init__(model, name)
        assert 't_eval' in inspect.signature(model).parameters, \
            "Model must have a time variable named 't_eval'.\
                Use wrap_callable_model to change the time variable name."

    def _simulate(self,
                  parameters: Union[Parameters, dict],
                  parameter_set: Union[ParameterSet, dict],
                  t_eval,
                  ):
        # Convert the parameters to a dictionary if it is a ParameterSet
        if isinstance(parameter_set, ParameterSet):
            _parameter_set = parameter_set.to_dict()
        if isinstance(parameters, Parameters):
            _parameters = parameters.to_dict()
        # Combine the parameters and parameter_set
        all_parameters = {**_parameter_set, **_parameters}

        # Check that any function arguments that are not specified in
        # parameters have a default value
        for arg in self.model_arguments.parameters:
            if arg == "t_eval":
                continue
            if arg not in all_parameters.keys():
                assert arg.default is not inspect.Parameter.empty, \
                    f"Parameter {arg} is not specified and does not have\
                        a default value."

        return self.model(t_eval=t_eval, **parameters)
