from abc import ABC, abstractmethod
from typing import Callable
from pydantic import BaseModel, Field

class BaseModule(ABC):
    """Base class for task."""
    name: str = Field(..., description="The name of the module")
    desc: str = Field(..., description="The description of the module")
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

class BaseTransition(ABC):
    """Base class for step transition."""
    source_module: BaseModule = Field(
        ..., description="The source module of the transition"
    )
    target_module: BaseModule = Field(
        ..., description="The target module of the transition"
    )
    desc: str = Field(
        ..., description="The description of the transition"
    )
    
class BaseGraph(ABC):
    """Graph representation modules."""

    initial_module: BaseModule = Field(
        ..., description="The initial module of the graph"
    )

    @abstractmethod
    def add_module(self, module: BaseModule):
        """Add a module to the graph."""

    @abstractmethod
    def add_transition(self, transition: BaseTransition):
        """Add a transition to the graph."""

    @abstractmethod
    def get_module(self, module_name: str) -> BaseModule:
        """Get a module from the graph."""

    @abstractmethod
    def neighbor_modules(self, state: BaseModule) -> list[BaseModule]:
        """Get the neighbor states of a state."""

    @abstractmethod
    def get_transition(
        self, source: BaseModule, target: BaseModule
    ) -> BaseTransition:
        """Get a transition from the graph."""
