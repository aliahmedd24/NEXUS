"""STAFF mode agents and pipeline.

Agents: JD Generator -> Genome Agent -> Team Chemistry -> Portfolio Optimizer
Pattern: SequentialAgent with structured output schemas and validation callbacks.
"""

from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types

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
        "Retrieves and adapts job descriptions for target roles based on "
        "active stress scenarios. Critiques adapted JDs for common problems."
    ),
    instruction=JD_GENERATOR_INSTRUCTION,
    tools=[get_jd_template, adapt_jd_to_scenario, critique_jd],
    output_schema=AdaptedJDOutput,
    output_key="adapted_jd",
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

genome_agent = LlmAgent(
    name="genome_agent",
    model=settings.gemini_model_fast,
    description=(
        "Builds 12-dimension leadership genome profiles, computes candidate "
        "fit scores, ranks candidates, and applies bias corrections."
    ),
    instruction=GENOME_AGENT_INSTRUCTION,
    tools=[get_candidate_pool, get_leader_genome, compute_candidate_fit, rank_candidates],
    output_schema=GenomeAnalysisOutput,
    output_key="genome_analysis",
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)

team_chemistry_agent = LlmAgent(
    name="team_chemistry_engine",
    model=settings.gemini_model_fast,
    description=(
        "Evaluates team compatibility by computing pairwise synergy scores "
        "and team balance impact for candidate additions."
    ),
    instruction=TEAM_CHEMISTRY_INSTRUCTION,
    tools=[get_existing_team, compute_team_compatibility],
    output_schema=TeamChemistryOutput,
    output_key="chemistry_report",
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

portfolio_optimizer_agent = LlmAgent(
    name="portfolio_optimizer",
    model=settings.gemini_model_fast,
    description=(
        "Optimizes staffing decisions across all open roles. Evaluates "
        "sourcing options, generates staffing plans, computes ROI, and "
        "builds development pathways for internal candidates."
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
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

# STAFF Pipeline: Sequential — JD adapt -> genome scoring -> chemistry -> portfolio
staff_pipeline = SequentialAgent(
    name="staff_pipeline",
    description=(
        "Fill leadership vacancies: adapt JD -> score genomes -> "
        "model chemistry -> optimize portfolio."
    ),
    sub_agents=[
        jd_generator_agent,
        genome_agent,
        team_chemistry_agent,
        portfolio_optimizer_agent,
    ],
)
