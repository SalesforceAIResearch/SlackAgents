from typing import Dict, Union, Any
from networkx import DiGraph
import networkx as nx
import matplotlib.pyplot as plt

from slackagents.agent.base import BaseAgent, BaseExecutor
from slackagents.graph.base import BaseModule, BaseTransition, BaseGraph


class ExecutorModule(BaseModule):
    """Executor module.
    """
    def __init__(self, executor: BaseExecutor):
        self.name = executor.name
        self.desc = executor.desc
        self.executor = executor
        
    def execute(self, *args, **kwargs)-> Dict[str, Any]:
        """Execute the executor. Ensure it returns a dict with 'role' and 'content' keys."""
        return self.executor.execute(*args, **kwargs)


class ExecutionTransition(BaseTransition):
    """Execution transition."""
    def __init__(
        self,
        source_module: ExecutorModule,
        target_module: ExecutorModule,
        desc: str
    ):
        self.source_module = source_module
        self.target_module = target_module
        self.desc = desc

class ExecutionGraph(DiGraph, BaseGraph):
    """Execution graph on multiple executor.
    Node: ExecutorModule
    Edge: ExecutionTransition
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def set_initial_module(self, module: Union[BaseModule, ExecutorModule]):
        """Set the initial module of the graph."""
        self.initial_module = module
    
    def add_agent(self, agent: BaseExecutor):
        """Add an agent to the graph."""
        self.add_module(ExecutorModule(agent))

    def add_module(self, module: Union[BaseModule, ExecutorModule]):
        """Add a module to the graph."""
        self.add_node(module.name, data=module)

    def add_transition(self, transition: Union[ExecutionTransition, BaseTransition]):
        """Add a transition to the graph."""
        self.add_module(transition.source_module)
        self.add_module(transition.target_module)
        self.add_edge(
            transition.source_module.name,
            transition.target_module.name,
            data=transition,
        )

    def get_module(self, module_name: str) -> Union[BaseModule, ExecutorModule]:
        """Get a module from the graph."""
        return self.nodes[module_name]["data"]

    def neighbor_modules(self, module: BaseModule) -> list[Union[BaseModule, ExecutorModule]]:
        """Get the neighbor states of a state."""
        return [
            self.get_module(neighbor)
            for neighbor in self.neighbors(module.name)
        ]

    def get_transition(
        self, source: BaseModule, target: BaseModule
    ) -> ExecutionTransition:
        """Get a transition between two modules from the graph."""
        transition = self.get_edge_data(
            source.name, target.name
        )
        return transition["data"]
    
    def get_all_transitions(self, source_module: BaseModule) -> list[ExecutionTransition]:
        """Get all possible transitions from a source module."""
        transitions = []
        for target_module in self.neighbor_modules(source_module):
            transitions.append(self.get_transition(source_module, target_module))
        return transitions

    def draw(self):
        """Draw the graph."""
        nx.draw(self, with_labels=True)
        plt.show()
