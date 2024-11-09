import unittest
from unittest.mock import MagicMock
from slackagents.agent.assistant import Assistant
from slackagents.agent.workflow_agent import WorkflowAgent
from slackagents.graph.execution_graph import ExecutionGraph, ExecutionTransition
from slackagents.llms.base import BaseLLM

class TestWorkflowAgent(unittest.TestCase):
    class TestAgent(Assistant):
        def __init__(self, name: str, desc: str):
            super().__init__(name, desc)
            self.tools = []
        
        def execute(self, *args, **kwargs):
            return {"role": "assistant", "content": f"{self.name} executed"}

    def setUp(self):
        # Set up mock LLM
        self.mock_llm = MagicMock(spec=BaseLLM)
        self.mock_llm.chat_completion.return_value = {"content": "Test response"}

        # Create test executors
        self.step_1 = self.TestAgent(name="executor_1", desc="First executor")
        self.step_2 = self.TestAgent(name="executor_2", desc="Second executor")
        self.step_3 = self.TestAgent(name="executor_3", desc="Third executor")

        # Build execution graph
        self.graph = ExecutionGraph()
        self.graph.add_agent(self.step_1)
        self.graph.add_agent(self.step_2)
        self.graph.add_agent(self.step_3)
        
        # Add transitions
        self.graph.add_transition(
            ExecutionTransition(
                source_module=self.graph.get_module("executor_1"),
                target_module=self.graph.get_module("executor_2"),
                desc="Transition 1->2"
            )
        )
        self.graph.add_transition(
            ExecutionTransition(
                source_module=self.graph.get_module("executor_2"),
                target_module=self.graph.get_module("executor_3"),
                desc="Transition 2->3"
            )
        )
        self.graph.set_initial_module(self.graph.get_module("executor_1"))

        # Create workflow agent
        self.agent = WorkflowAgent(
            name="TestAgent",
            desc="Test workflow agent",
            graph=self.graph,
            llm=self.mock_llm,
            verbose=False
        )

    def test_initialization(self):
        """Test proper initialization of WorkflowAgent"""
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.cur_module.name, "executor_1")
        self.assertEqual(len(self.agent.messages), 0)

    def test_chat_simple_response(self):
        """Test basic chat functionality without transitions"""
        self.mock_llm.chat_completion.return_value = {"content": "Simple response"}
        response = self.agent.chat("Hello")
        self.assertEqual(response, "Simple response")
        self.assertEqual(len(self.agent.messages), 3)  # system prompt + user message + assistant response

    def test_transition_between_modules(self):
        """Test transition between modules using tool calls"""
        # Mock LLM responses for transition
        self.mock_llm.chat_completion.side_effect = [
            {
                "tool_calls": [{
                    "id": "1",
                    "type": "function",
                    "function": {
                        "name": "transition",
                        "arguments": '{"next_module": "executor_2", "reason": "Test reason", "summary": "Test summary"}'
                    }
                }]
            },
            {"content": "Transitioned to executor_2"}
        ]

        response = self.agent.chat("Trigger transition")
        
        self.assertEqual(self.agent.cur_module.name, "executor_2")
        self.assertIn("You are now in the executor_2 module", 
                     next(msg["content"] for msg in self.agent.messages if msg["role"] == "tool"))

    def test_system_prompt_update(self):
        """Test system prompt updates when switching modules"""
        initial_system_prompt = self.agent.messages[0]["content"] if self.agent.messages else None
        
        # Trigger transition to new module
        self.mock_llm.chat_completion.side_effect = [
            {
                "tool_calls": [{
                    "id": "1",
                    "type": "function",
                    "function": {
                        "name": "transition",
                        "arguments": '{"next_module": "executor_2", "reason": "Test", "summary": "Test"}'
                    }
                }]
            },
            {"content": "Done"}
        ]
        
        self.agent.chat("Switch module")
        new_system_prompt = self.agent.messages[0]["content"]
        
        self.assertNotEqual(initial_system_prompt, new_system_prompt)

    def test_custom_tool_handling(self):
        """Test handling of custom tools in modules"""
        # Add a mock tool to executor_1
        mock_tool = MagicMock()
        mock_tool.info = {
            "type": "function",
            "function": {
                "name": "custom_tool",
                "description": "Test tool",
                "parameters": {}
            }
        }
        
        # Add the mock tool to the agent
        self.step_1.add_tool(mock_tool)

        # Mock LLM to call the custom tool
        self.mock_llm.chat_completion.side_effect = [
            {
                "tool_calls": [{
                    "id": "1",
                    "type": "function",
                    "function": {
                        "name": "custom_tool",
                        "arguments": "{}"
                    }
                }]
            },
            {"content": "Tool executed"}
        ]

        self.agent.chat("Use custom tool")
        tool_messages = [msg for msg in self.agent.messages if msg.get("tool_call_id") == "1"]
        self.assertTrue(len(tool_messages) > 0)

if __name__ == "__main__":
    unittest.main() 