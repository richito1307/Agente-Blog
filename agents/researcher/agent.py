import uuid

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from .schemas import SearchResponse
from .tools.prompts import INVESTIGATOR_PROMPT
from .tools.search_agent import news_agent
from shared.http import resolve_url


class SearchAgent:

    def __init__(self):
        self.agent: LlmAgent = None
        self.runner: Runner = None

        self.search_tool = agent_tool.AgentTool(agent=news_agent)
        self.session_service = InMemorySessionService()

        self.researcher_agent = LlmAgent(
            name="Investigator",
            model="gemini-2.0-flash",
            instruction=INVESTIGATOR_PROMPT,
            output_schema=SearchResponse,
            tools=[self.search_tool, resolve_url],
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True
        )

        self.runner = Runner(
            agent=self.researcher_agent,
            session_service=self.session_service,
            app_name="agents"
        )
    
    async def run_task(self, topic: str):
        new_message_content = Content(parts=[Part(text=topic)])

        static_user_id = "fastapi_user_1232"
        unique_session_id = str(uuid.uuid4())

        final_result_text = ""

        session_service = self.runner.session_service
        await session_service.create_session(
            app_name=self.runner.app_name, 
            user_id=static_user_id, 
            session_id=unique_session_id
        )

        async_generator = self.runner.run_async(
            user_id=static_user_id,
            session_id=unique_session_id,
            new_message=new_message_content
        )
        
        async for event in async_generator:
            if hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_result_text += part.text
        
        await session_service.delete_session(
            app_name=self.runner.app_name, 
            user_id=static_user_id, 
            session_id=unique_session_id
        )

        return final_result_text


search_agent = SearchAgent()
