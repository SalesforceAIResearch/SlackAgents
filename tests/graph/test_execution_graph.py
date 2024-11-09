import unittest
from slackagents.agent.base import BaseExecutor
from slackagents.graph.execution_graph import ExecutionGraph, ExecutorModule, ExecutionTransition

class TestExecutionGraph(unittest.TestCase):
    class TestExecutor(BaseExecutor):
        def __init__(self, name: str, desc: str):
            super().__init__(name, desc)
        
        def execute(self, *args, **kwargs):
            return f"{self.name} executed"

    def setUp(self):
        self.executor_1 = self.TestExecutor(name="executor_1", desc="executor 1")
        self.executor_2 = self.TestExecutor(name="executor_2", desc="executor 2")
        self.executor_3 = self.TestExecutor(name="executor_3", desc="executor 3")
        self.graph = ExecutionGraph()
        self.graph.add_module(ExecutorModule(self.executor_1))
        self.graph.add_module(ExecutorModule(self.executor_2))
        self.graph.add_module(ExecutorModule(self.executor_3))
        self.graph.add_transition(ExecutionTransition(source_module=self.graph.get_module("executor_1"), target_module=self.graph.get_module("executor_2"), desc="transition 0-1"))
        self.graph.add_transition(ExecutionTransition(source_module=self.graph.get_module("executor_2"), target_module=self.graph.get_module("executor_3"), desc="transition 1-2"))
        self.graph.add_transition(ExecutionTransition(source_module=self.graph.get_module("executor_3"), target_module=self.graph.get_module("executor_1"), desc="transition 2-0"))
        
    def test_transition(self):
        transition = self.graph.get_transition(self.graph.get_module("executor_1"), self.graph.get_module("executor_2"))
        self.assertEqual(transition.source_module.name, "executor_1")
        self.assertEqual(transition.target_module.name, "executor_2")

    def test_get_all_transitions(self):
        transitions = self.graph.get_all_transitions(self.graph.get_module("executor_1"))
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0].source_module.name, "executor_1")
        self.assertEqual(transitions[0].target_module.name, "executor_2")
    
    def test_graph_structure(self):
        self.assertEqual(len(self.graph.nodes), 3)
        self.assertEqual(len(self.graph.edges), 3)
        
    def test_get_transition_from_module(self):
        transitions = self.graph.get_all_transitions(self.graph.get_module("executor_1"))
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0].source_module.name, "executor_1")
        self.assertEqual(transitions[0].target_module.name, "executor_2")
        transitions = self.graph.get_all_transitions(self.graph.get_module("executor_2"))
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0].source_module.name, "executor_2")
        self.assertEqual(transitions[0].target_module.name, "executor_3")
        transitions = self.graph.get_all_transitions(self.graph.get_module("executor_3"))
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0].source_module.name, "executor_3")
        self.assertEqual(transitions[0].target_module.name, "executor_1")

    def test_draw_graph(self):
        from unittest.mock import patch
        with patch('networkx.draw') as mock_draw:
            self.graph.draw()
            mock_draw.assert_called_once()

if __name__ == "__main__":
    unittest.main()