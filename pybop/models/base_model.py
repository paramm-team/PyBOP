from typing import Callable, Optional


class BaseModel():
    """
    Base class for defining the model (often a PDE) that will be used in
    the simulation in conjunction a solver.
    """

    def __init__(
            self,
            model: Optional[Callable] = None,
            name: str = "BaseModel",
    ):
        self.name = name
        self.model = model

    def _simulate(*args, **kwargs):
        """
        This method should be implemented in the child class.
        _simulate should take the parameters, parameter_set, and t_eval as
        arguments and return the model output.
        _simulate is called by the simulate method in the BaseSim class via
        the model attribute provided by the __init__ method.
        _simulate will implement the solver if required.
        """
        raise NotImplementedError
