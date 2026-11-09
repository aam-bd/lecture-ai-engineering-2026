"""第3回 宿題（発展 a）: Google ADK (Agent Development Kit) による学習支援エージェントの再構築。

Pydantic AI で作成したエージェントと同じ INSTRUCTIONS と tools (search_glossary,
get_lecture_summary, make_quiz) を流用し、ADK 2.0 形式の Agent として定義する。
"""

from google.adk.agents import Agent

from app import tools
from app.agent import INSTRUCTIONS

root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="glossary_agent",
    instruction=INSTRUCTIONS,
    tools=[tools.search_glossary, tools.get_lecture_summary, tools.make_quiz],
)
