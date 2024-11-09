import unittest
from dotenv import load_dotenv
load_dotenv()
from slackagents.llms.openai import OpenAILLM
from slackagents.llms.base import BaseLLMConfig

class TestOpenAILLM(unittest.TestCase):

    def setUp(self):
        self.config = BaseLLMConfig(model="gpt-4o", temperature=0.7, max_tokens=100, top_p=1.0)

    def test_chat_completion(self):
        llm = OpenAILLM(config=self.config)
        messages = [
            {"role": "system", "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."},
            {"role": "user", "content": "Hi"}
        ]
        response = llm.chat_completion(messages)
        print(response)
    
    def test_chat_completion_with_tools(self):
        llm = OpenAILLM(config=self.config)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_delivery_date",
                    "description": "Get the delivery date for a customer's order. Call this whenever you need to know the delivery date, for example when a customer asks 'Where is my package'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The customer's order ID.",
                            },
                        },
                        "required": ["order_id"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "respond",
                    "description": "Generate and send a response to a given message. This function allows the assistant to formulate and deliver appropriate replies based on the input message and the context of the conversation. Generate a concise response for s",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The content of the message to respond to. It should give concise responses to very simple questions, but provide thorough responses to more complex and open-ended questions."
                            },
                        },
                        "required": ["message"],
                    },
                },
            }
        ]
        
        messages = [
            {"role": "system", "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."},
            {"role": "user", "content": "Hi, can you tell me the delivery date for my order? My order IDs are 1234567890 and 1234567891."}
        ]
        
        response = llm.chat_completion(messages, tools=tools)
        self.assertIsInstance(response, dict)
        self.assertAlmostEqual(response["content"], None)
        self.assertIsInstance(response["tool_calls"], list)
        self.assertEqual(response["tool_calls"][0]['function']['name'], "get_delivery_date")
        
if __name__ == '__main__':
    unittest.main()