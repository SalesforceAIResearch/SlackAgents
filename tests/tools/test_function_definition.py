import unittest
from slackagents.tools.utils import (
    generate_function_definition_from_callable,
)

class TestFunctionDefinition(unittest.TestCase):
  
  def test_generate_function_definition_from_callable(self):
      def test_function(arg1: str, arg2: int = 0) -> bool:
          """Test function description
          :param arg1: The first argument
          :param arg2: The second argument
          :return: The result
          """
          pass

      result = generate_function_definition_from_callable(test_function)
      assert result["name"] == "test_function"
      assert "arg1" in result["parameters"]["properties"]
    
if __name__ == "__main__":
    unittest.main()