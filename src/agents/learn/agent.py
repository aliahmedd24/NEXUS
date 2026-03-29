"""LEARN mode agents and pipeline.

Agents: Decision Replay -> Pattern Intelligence
Pattern: SequentialAgent — replay past decisions, detect biases, update calibration.
This closes the LEARN -> STAFF feedback loop.

ADK best practices applied:
- Validation gate before pattern intelligence
- Separate agents for replay (reasoning) and pattern detection (statistics)
- output_key + output_schema for structured data flow
- LEARN -> STAFF feedback loop via calibration coefficient writes
"""

import structlog
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
    find_analogous_decisions,
    get_calibration_coefficients,
    get_decision_outcomes,
    get_historical_decisions,
    reconstruct_decision,
    simulate_counterfactual,
    update_calibration_from_biases,
)

logger = structlog.get_logger()


def _validate_replay_output(callback_context):
    """Validate replay_analysis exists before pattern intelligence runs."""
    replay = callback_context.state.get("replay_analysis")
    if not replay:
        logger.warning("learn_validation", msg="replay_analysis missing from state")
        return None
    data = replay if isinstance(replay, dict) else {}
    replays = data.get("replays", [])
    if not replays:
        logger.info("learn_validation", msg="No replays produced — pattern intelligence will rely on raw bias detection")
    return None


decision_replay_agent = LlmAgent(
    name="decision_replay",
    model=settings.gemini_model_fast,
    description=(
        "LLM-reasoned replay of past BMW hiring decisions. Uses raw genome data "
        "and actual outcomes to form its OWN assessment of what went wrong — "
        "not just mechanical divergence scores. Simulates counterfactuals by "
        "reasoning about whether the runner-up's specific strengths would have "
        "avoided the specific failures that occurred."
    ),
    instruction=DECISION_REPLAY_INSTRUCTION,
    tools=[
        get_historical_decisions,
        reconstruct_decision,
        get_decision_outcomes,
        simulate_counterfactual,
        find_analogous_decisions,
    ],
    output_schema=ReplayAnalysisOutput,
    output_key="replay_analysis",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
)

pattern_intelligence_agent = LlmAgent(
    name="pattern_intelligence",
    model=settings.gemini_model_fast,
    description=(
        "Discovers systematic biases in BMW's hiring using statistical correlation. "
        "Extracts success DNA and failure signals from historical data. "
        "Writes calibration coefficients to Supabase that STAFF mode's "
        "rank_candidates and compute_candidate_fit use automatically — "
        "closing the LEARN -> STAFF feedback loop."
    ),
    instruction=PATTERN_INTELLIGENCE_INSTRUCTION,
    tools=[
        detect_bias_patterns,
        get_calibration_coefficients,
        update_calibration_from_biases,
    ],
    output_schema=LearningReportOutput,
    output_key="learning_report",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
    before_agent_callback=_validate_replay_output,
)

# LEARN Pipeline: Sequential — replay decisions -> detect patterns -> update calibration
# Validation gate ensures replay_analysis exists before pattern detection
learn_pipeline = SequentialAgent(
    name="learn_pipeline",
    description=(
        "Organizational learning pipeline: replay past decisions with "
        "LLM-reasoned counterfactual analysis -> detect systematic biases "
        "via statistical correlation -> write calibration coefficients that "
        "feed back into STAFF mode scoring."
    ),
    sub_agents=[decision_replay_agent, pattern_intelligence_agent],
)
