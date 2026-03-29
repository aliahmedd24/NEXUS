"""STAFF mode agents and pipeline.

Agents: JD Generator -> Genome Agent -> Team Chemistry -> Portfolio Optimizer
Pattern: SequentialAgent with structured output schemas and validation callbacks.

ADK best practices applied:
- after_agent_callback validation gates between stages
- One agent = one responsibility (4 focused specialists)
- output_key + output_schema for reliable data flow
- Resource tiering: all Flash (cost-effective for scoring tasks)
- Thinking enabled for transparent reasoning
"""

import click
import structlog
from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types

logger = structlog.get_logger()


def _log_tool_call(tool, args, tool_context):
    """Print tool calls to terminal so the user sees progress."""
    click.echo(f"  ⚙ {tool.name}({', '.join(f'{k}={v!r}' for k, v in args.items())})", err=True)
    return None


def _validate_genome_input(callback_context):
    """Validate adapted_jd exists before genome agent runs."""
    jd = callback_context.state.get("adapted_jd")
    if not jd:
        logger.warning("staff_validation", msg="adapted_jd missing — genome agent may lack role context")
    return None


def _validate_chemistry_input(callback_context):
    """Validate genome_analysis has candidate_id and org_unit_id for chemistry."""
    analysis = callback_context.state.get("genome_analysis")
    if not analysis:
        logger.warning("staff_validation", msg="genome_analysis missing from state")
        return None
    data = analysis if isinstance(analysis, dict) else {}
    candidates = data.get("ranked_candidates", [])
    if not candidates:
        logger.warning("staff_validation", msg="genome_analysis has no ranked_candidates")
    elif not candidates[0].get("candidate_id"):
        logger.warning("staff_validation", msg="Top candidate missing candidate_id — chemistry will fail")
    if not data.get("org_unit_id"):
        logger.warning("staff_validation", msg="genome_analysis missing org_unit_id — chemistry will fail")
    return None


def _validate_portfolio_input(callback_context):
    """Validate chemistry_report exists before portfolio optimizer."""
    report = callback_context.state.get("chemistry_report")
    if not report:
        logger.info("staff_validation", msg="chemistry_report missing — portfolio will work without it")
    return None


from src.agents.prompts import (
    GENOME_AGENT_INSTRUCTION,
    JD_GENERATOR_INSTRUCTION,
    PORTFOLIO_OPTIMIZER_INSTRUCTION,
    TEAM_CHEMISTRY_INSTRUCTION,
)
from src.config import settings
from src.schemas.agent_outputs import (
    AdaptedJDOutput,
    GenomeAnalysisOutput,
    PortfolioOptimizerOutput,
    TeamChemistryOutput,
)
from src.tools.staff_tools import (
    adapt_jd_to_scenario,
    compute_candidate_fit,
    compute_team_compatibility,
    critique_jd,
    evaluate_sourcing_options,
    generate_development_pathway,
    generate_staffing_plan,
    get_candidate_pool,
    get_existing_team,
    get_jd_template,
    get_leader_genome,
    rank_candidates,
)

jd_generator_agent = LlmAgent(
    name="jd_generator",
    model=settings.gemini_model_fast,
    description=(
        "Adapts job descriptions for BMW leadership roles based on active "
        "stress scenarios. Critiques adapted JDs for unicorn profiles, "
        "conflicting requirements, and gender-coded language. Writes "
        "adapted_jd to state with scenario-weighted competency requirements."
    ),
    instruction=JD_GENERATOR_INSTRUCTION,
    tools=[get_jd_template, adapt_jd_to_scenario, critique_jd],
    output_schema=AdaptedJDOutput,
    output_key="adapted_jd",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
    before_tool_callback=_log_tool_call,
)

genome_agent = LlmAgent(
    name="genome_agent",
    model=settings.gemini_model_fast,
    description=(
        "LLM-reasoned candidate ranking using 12-dimension leadership genomes. "
        "Uses raw genome data, calibration coefficients, and BMW leadership "
        "culture context to form its OWN fit assessments — not just mechanical "
        "weighted averages. Writes ranked_candidates with candidate_ids and "
        "org_unit_id to state for team chemistry."
    ),
    instruction=GENOME_AGENT_INSTRUCTION,
    tools=[get_candidate_pool, get_leader_genome, compute_candidate_fit, rank_candidates],
    output_schema=GenomeAnalysisOutput,
    output_key="genome_analysis",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
    before_tool_callback=_log_tool_call,
    before_agent_callback=_validate_genome_input,
)

team_chemistry_agent = LlmAgent(
    name="team_chemistry_engine",
    model=settings.gemini_model_fast,
    description=(
        "LLM-reasoned team dynamics assessment. Analyzes pairwise compatibility "
        "between top candidate and existing team using interaction rules and "
        "genome profiles. Names specific people and predicts specific conflicts "
        "in BMW's consensus-driven culture."
    ),
    instruction=TEAM_CHEMISTRY_INSTRUCTION,
    tools=[get_existing_team, compute_team_compatibility],
    output_schema=TeamChemistryOutput,
    output_key="chemistry_report",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
    before_tool_callback=_log_tool_call,
    before_agent_callback=_validate_chemistry_input,
)

portfolio_optimizer_agent = LlmAgent(
    name="portfolio_optimizer",
    model=settings.gemini_model_fast,
    description=(
        "Talent investment strategist. Evaluates sourcing options with BMW-specific "
        "cost ranges (not hardcoded), generates staffing plans with efficient "
        "frontier optimization, and reasons about ROI using cascade exposure data. "
        "Every recommendation includes a EUR figure and time-to-impact estimate."
    ),
    instruction=PORTFOLIO_OPTIMIZER_INSTRUCTION,
    tools=[
        evaluate_sourcing_options,
        generate_staffing_plan,
        generate_development_pathway,
        rank_candidates,
    ],
    output_schema=PortfolioOptimizerOutput,
    output_key="staffing_plan",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
    before_tool_callback=_log_tool_call,
    before_agent_callback=_validate_portfolio_input,
)

# STAFF Pipeline: Sequential — JD adapt -> genome scoring -> chemistry -> portfolio
# Validation gates run between stages via before_agent_callback
staff_pipeline = SequentialAgent(
    name="staff_pipeline",
    description=(
        "LLM-driven talent intelligence pipeline: adapt JD to scenario -> "
        "rank candidates with reasoned fit scores -> model team chemistry "
        "dynamics -> optimize staffing portfolio with ROI. Each stage "
        "validates upstream output before proceeding."
    ),
    sub_agents=[
        jd_generator_agent,
        genome_agent,
        team_chemistry_agent,
        portfolio_optimizer_agent,
    ],
)
