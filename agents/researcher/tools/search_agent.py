from google.adk.agents import Agent
from google.adk.tools import google_search

from .prompts import RESEARCHER_PROMPT_DYNAMIC


news_agent = Agent(
    name="Investigador",
    model="gemini-2.0-flash",
    description="Investigador de noticias o temas emergentes",
    instruction=RESEARCHER_PROMPT_DYNAMIC,
    tools=[google_search]
)
