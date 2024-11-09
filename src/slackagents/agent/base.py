import uuid
from abc import ABC, abstractmethod
from pydantic import Field, BaseModel
from typing import Any


class BaseAgent(ABC):
    name: str
    desc: str
    a_id: str
    
    def __init__(
        self, 
        name: str, 
        desc: str,
        a_id: str = str(uuid.uuid4()),
        *args: Any, 
        **kwargs: Any
    ):
        super().__init__()
        self.name:str = name
        self.desc:str = desc
        self.a_id:str = a_id
    
    def __str__(self):
        return f"Agent: {self.name}\nDescription: {self.desc}\nID: {self.a_id}"
    
    def __repr__(self):
        return self.__str__()

class BaseAssistant(BaseAgent):
    """Assistant class is the base class for assistant. It will be used to set up an assistant."""
    
    @abstractmethod
    def chat(self, *args, **kwargs):
        """define the chat logic here"""
        pass
    
class BaseExecutor(BaseAgent):
    """Executor class is the base class for execution. It will be used to set up an runnable execution unit."""
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        """define the execution logic here"""
        pass
    
    # @abstractmethod
    # def reason(self, *args, **kwargs):
    #     """define the reasoning logic here"""
    #     # TODO: enabling a reasoning step before execution if needed
    #     pass

class BaseSlackAgent(BaseAgent):
    """SlackAgent class is the base class for slack agent. It will be used to set up an slack agent."""
    
    @abstractmethod
    def chat(self, channel_id: str, *args, **kwargs):
        """define the chat logic here"""
        pass

if __name__ == "__main__":
    name = "BaseAgent"
    desc = "This is a base agent"
    agent = BaseAgent(name, desc)
    agent.a_id = "123"
    print(agent)
