"""NEXUS root agent — the Orchestrator.

Routes user intent to DIAGNOSE, STAFF, or LEARN pipelines and manages
session context across modes. This is the ADK framework entry point.
"""

from google.adk.agents import LlmAgent
from google.genai import types

from src.agents.brief.agent import brief_generator_agent
from src.agents.diagnose.agent import diagnose_pipeline
from src.agents.learn.agent import learn_pipeline
from src.agents.prompts import ORCHESTRATOR_INSTRUCTION
from src.agents.staff.agent import staff_pipeline
from src.config import settings
from src.tools.orchestrator_tools import suggest_scenarios

orchestrator_agent = LlmAgent(
    name="orchestrator",
    model=settings.gemini_model_fast,
    description=(
        "NEXUS session router. Classifies user intent by CONTENT and "
        "immediately transfers to the matching pipeline. Does NOT answer "
        "directly — always delegates. Carries scenario context across turns."
    ),
    instruction=ORCHESTRATOR_INSTRUCTION,
    tools=[suggest_scenarios],
    sub_agents=[
        diagnose_pipeline,
        staff_pipeline,
        learn_pipeline,
        brief_generator_agent,
    ],
    output_key="session_output",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
)

# ADK framework entry point
root_agent = orchestrator_agent
