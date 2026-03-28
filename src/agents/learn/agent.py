"""LEARN mode agents and pipeline.

Agents: Decision Replay -> Pattern Intelligence
Pattern: SequentialAgent — replay past decisions, detect biases, update calibration.
This closes the LEARN -> STAFF feedback loop.
"""

from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types

from src.agents.prompts import (
    DECISION_REPLAY_INSTRUCTION,
    PATTERN_INTELLIGENCE_INSTRUCTION,
)
from src.config import settings
from src.schemas.agent_outputs import (
    LearningReportOutput,
    ReplayAnalysisOutput,
)
from src.tools.learn_tools import (
    detect_bias_patterns,
    get_calibration_coefficients,
    get_decision_outcomes,
    get_historical_decisions,
    reconstruct_decision,
    simulate_counterfactual,
    update_calibration_from_biases,
)

decision_replay_agent = LlmAgent(
    name="decision_replay",
    model=settings.gemini_model_fast,
    description=(
        "Replays past hiring decisions: retrieves historical data, simulates "
        "counterfactuals with runner-up candidates, and classifies each "
        "decision as optimal, suboptimal, costly error, or critical miss."
    ),
    instruction=DECISION_REPLAY_INSTRUCTION,
    tools=[
        get_historical_decisions,
        reconstruct_decision,
        get_decision_outcomes,
        simulate_counterfactual,
    ],
    output_schema=ReplayAnalysisOutput,
    output_key="replay_analysis",
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)

pattern_intelligence_agent = LlmAgent(
    name="pattern_intelligence",
    model=settings.gemini_model_fast,
    description=(
        "Discovers systematic biases across all historical decisions. "
        "Extracts success/failure patterns and writes calibration "
        "coefficients that STAFF mode uses for scoring."
    ),
    instruction=PATTERN_INTELLIGENCE_INSTRUCTION,
    tools=[
        detect_bias_patterns,
        get_calibration_coefficients,
        update_calibration_from_biases,
    ],
    output_schema=LearningReportOutput,
    output_key="learning_report",
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)

# LEARN Pipeline: Sequential — replay decisions -> detect patterns -> update calibration
learn_pipeline = SequentialAgent(
    name="learn_pipeline",
    description=(
        "Learn from past decisions: replay -> detect biases -> "
        "update calibration coefficients."
    ),
    sub_agents=[decision_replay_agent, pattern_intelligence_agent],
)
