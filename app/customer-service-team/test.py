import re
from digitalhq.session.base import BaseSession
from digitalhq.state.respond import SlackRespondState
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from digitalhq.brain.brain_prompts import ORCHESTRATION_TEMPLATE
from digitalhq.session.session_store import SessionStore, SlackSessionStore
from digitalhq.brain.Brain import Brain
from digitalhq.commons.common_types import Message

class OrchestrateState(SlackRespondState):
    """State for orchestrating and assigning the unsolved issues to other agents.
    E.g., @Matt: This is a customer with billing issues. Can you please check on this?
    @ Dan: Please unlock the user account for this customer.
    """

    name: str = "Orchestrate"
    desc: str = (
        "Orchestrating and assigning the unsolved issues or questions"
        " to other collegue agents for help."
    )
    K: int = 3
    monitor: dict = {"confirmation", "auth"}
    
    def perceive(self, session: BaseSession, *args, **kwargs):
        """Extract sufficient information from the session for this state."""
        observation = [
            item.model_dump_json(exclude={"mid", "time"})
            for item in session.content
            if item.type in self.monitor
        ]
        # Extract the last K messages as orchestration is near confirmation and is at the end of session.
        return "\n".join(observation[-self.K:])

    def _get_response(self,session, brain: Brain, *args, **kwargs):
        """Generate a response for the state."""
        observation = self.perceive(session)
        import ipdb; ipdb.set_trace()
        llm = brain.llm
        messages = [
            ChatMessage(
                role="user", content=ORCHESTRATION_TEMPLATE.format(
                    profile=brain.profile.model_dump_json(include={"name", "about_me", "abilities"}), 
                    colleagues=[colleague.model_dump_json(include={"name", "about_me", "abilities"}) for colleague in brain.profile.colleagues], 
                    messages=observation)
            )
        ]
            # import ipdb; ipdb.set_trace()
        import ipdb; ipdb.set_trace()
        self.response = llm.chat(messages).message.content
    
    def _extract_assingee(self):
        matches = re.findall(r"<@(\w+)>", self.response)
        unique_names = []
        for name in matches:
            if name not in unique_names:
                unique_names.append(name)
        return unique_names
    
    def run(
        self, session, session_store, brain: Brain, *args, **kwargs
    ):
        """Execute the runable for slack respond state with perception."""
        import ipdb; ipdb.set_trace()
        print("""Execute the runable for slack respond state with perception.""")
        self._get_response(session, brain)
        to_who = self._extract_assingee()
        # TODO: move this to a separate function
        content = self.response
        content_match = re.search(r"```(.*?)```", content, re.DOTALL)
        if content_match:
            content = content_match.group(1).strip()  # Extract the content and strip any leading/trailing whitespace

        # Remove "Main Message: " prefix if present
        if content.startswith("Main Message: "):
            content = content[len("Main Message: "):].strip()
        
        message = Message(
            type="task",
            info=content,
            from_who=brain.profile.name,
            to_who=to_who,
        )
        # Create a session object
        # TODO: link new session to parent session, i.e., this session
        child_session = session.create_child(
            session_store=session_store,
            owner=brain.profile.name,
            topic=content,
            channel_id=session.channel_id,
            message=message   
        )
        """Send the response to slack."""
        print("""Send the response to slack.""""")
        print(f"session info:{session.channel_id}{session.thread_ts}")
        child_session.post_message(message, brain.profile.slack_bot_token, thread_ts=child_session.thread_ts)

    def is_done(self, session_id: str, session_store:SessionStore , brain: Brain, *args, **kwargs):
        """Check if this state is done."""
        return True

if __name__ == "__main__":
    import pickle
    with open("session.pkl", "rb") as f:
        session = pickle.load(f)
    from roles.representative import CustomerServiceRepresentative

    SLACK_BOT_TOKEN = (
        "xoxb-7008638092481-7004461938482-zggkClX00gQH8qTRvLlBRJEv"
    )
    SLACK_APP_TOKEN = "xapp-1-A06VBQ8D93Q-7054624596768-b08f001d9ce2de1a2336efc18693f87103a6e3883ab76d57f2c20ee39b357241"
    config = {
        "PROCESS_URL": "http://localhost:30003/chat",
        "SLACK_BOT_TOKEN": SLACK_BOT_TOKEN,
        "SLACK_APP_TOKEN": SLACK_APP_TOKEN,
    }
    MODEL = "gpt-4-32k"  # "gpt-4"
    llm = OpenAI(model=MODEL)
    from digitalhq.session.session_store import RedisSessionStore
    session_store = RedisSessionStore()
    config_path = "app/customer_service/configs/representative.json"
    human = CustomerServiceRepresentative(config_path=config_path, llm=llm)
    state = OrchestrateState()
    state.run(session, session_store, human.brain)