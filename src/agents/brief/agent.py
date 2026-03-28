"""Decision Brief Generator agent.

Uses Gemini Pro for higher-quality narrative generation.
Reads upstream agent outputs from ADK session state and produces
board-ready decision briefs with dissent reports and confidence ratings.
"""

from google.adk.agents import LlmAgent
from google.genai import types

from src.agents.prompts import BRIEF_GENERATOR_INSTRUCTION
from src.config import settings
from src.schemas.agent_outputs import DecisionBriefOutput
from src.tools.brief_tools import compute_confidence_rating, surface_dissent

brief_generator_agent = LlmAgent(
    name="brief_generator",
    model=settings.gemini_model_pro,
    description=(
        "Produces board-ready decision briefs by synthesizing outputs from "
        "upstream DIAGNOSE, STAFF, or LEARN agents. Surfaces disagreements "
        "between agents and rates recommendation confidence."
    ),
    instruction=BRIEF_GENERATOR_INSTRUCTION,
    tools=[surface_dissent, compute_confidence_rating],
    output_schema=DecisionBriefOutput,
    output_key="decision_brief",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
)
