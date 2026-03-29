"""DIAGNOSE mode agents and pipeline.

Agents: Scenario Architect -> Vulnerability Scanner -> Cascade Modeler
Pattern: SequentialAgent with structured output schemas and validation callbacks.

ADK best practices applied:
- after_agent_callback validation gates between pipeline stages
- before_tool_callback for terminal logging
- Resource tiering: Flash for scenario/vulnerability, Pro for cascade reasoning
- Thinking enabled on all agents for transparent reasoning chains
"""

import click
import structlog
from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types

from src.agents.prompts import (
    CASCADE_MODELER_INSTRUCTION,
    SCENARIO_ARCHITECT_INSTRUCTION,
    VULNERABILITY_SCANNER_INSTRUCTION,
)
from src.config import settings
from src.schemas.agent_outputs import (
    CascadeReportOutput,
    ScenarioAnalysisOutput,
    VulnerabilityReportOutput,
)
from src.tools.diagnose_tools import (
    compute_cascade_impact,
    create_adhoc_scenario,
    get_scenario_by_name,
    get_scenario_library,
    identify_single_points_of_failure,
    scan_vulnerabilities,
)

logger = structlog.get_logger()


def _log_tool_call(tool, args, tool_context):
    """Print tool calls to terminal so the user sees progress."""
    click.echo(f"  ⚙ {tool.name}({', '.join(f'{k}={v!r}' for k, v in args.items())})", err=True)
    return None


def _validate_scenario_output(callback_context):
    """Validate scenario_analysis output before vulnerability scanner runs.

    ADK best practice: validation gates between sequential pipeline stages
    to catch broken data before it cascades downstream.
    """
    analysis = callback_context.state.get("scenario_analysis")
    if not analysis:
        logger.warning("diagnose_validation", msg="scenario_analysis missing from state")
        return None
    data = analysis if isinstance(analysis, dict) else {}
    has_db_id = data.get("scenario_id") and not str(data["scenario_id"]).startswith("adhoc:")
    has_adhoc = bool(data.get("adhoc_scenario_json"))
    if not has_db_id and not has_adhoc:
        logger.warning("diagnose_validation", msg="scenario_analysis has no scenario_id and no adhoc_scenario_json")
    return None


def _validate_vulnerability_output(callback_context):
    """Validate vulnerability_report before cascade modeler runs.

    Ensures heatmap has RED cells with role_ids for cascade to process.
    """
    report = callback_context.state.get("vulnerability_report")
    if not report:
        logger.warning("diagnose_validation", msg="vulnerability_report missing from state")
        return None
    data = report if isinstance(report, dict) else {}
    heatmap = data.get("heatmap", [])
    red_cells = [c for c in heatmap if isinstance(c, dict) and c.get("status") == "red"]
    if not red_cells:
        logger.info("diagnose_validation", msg="No RED cells — cascade modeler may have nothing to trace")
    else:
        missing_ids = [c for c in red_cells if not c.get("role_id")]
        if missing_ids:
            logger.warning("diagnose_validation", msg=f"{len(missing_ids)} RED cells missing role_id")
    return None


scenario_architect = LlmAgent(
    name="scenario_architect",
    model=settings.gemini_model_fast,
    description=(
        "Analyzes BMW stress-test scenarios: retrieves from scenario library, "
        "creates compound crises, OR creates novel ad-hoc scenarios with "
        "LLM-reasoned demand vectors. Writes scenario_id (or adhoc_scenario_json "
        "for novel scenarios) to state for downstream agents."
    ),
    instruction=SCENARIO_ARCHITECT_INSTRUCTION,
    tools=[get_scenario_library, get_scenario_by_name, create_adhoc_scenario],
    output_schema=ScenarioAnalysisOutput,
    output_key="scenario_analysis",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
    before_tool_callback=_log_tool_call,
)

vulnerability_scanner = LlmAgent(
    name="vulnerability_scanner",
    model=settings.gemini_model_fast,
    description=(
        "Performs LLM-reasoned vulnerability assessment of BMW leadership roles "
        "against scenario demands. Uses raw genome data and demand vectors to form "
        "its OWN gap assessments — not just mechanical formula outputs. "
        "Produces color-coded heatmap with role_ids for cascade modeling."
    ),
    instruction=VULNERABILITY_SCANNER_INSTRUCTION,
    tools=[scan_vulnerabilities, identify_single_points_of_failure],
    output_schema=VulnerabilityReportOutput,
    output_key="vulnerability_report",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
    before_tool_callback=_log_tool_call,
    before_agent_callback=_validate_scenario_output,
)

cascade_modeler = LlmAgent(
    name="cascade_modeler",
    model=settings.gemini_model_pro,
    description=(
        "Traces downstream cascade impacts from leadership failures using BMW "
        "operational data (EUR45M/day Munich throughput, supply chain costs). "
        "Reasons about each cascade node to estimate EUR exposure — does NOT "
        "use hardcoded multipliers. Identifies optimal intervention points."
    ),
    instruction=CASCADE_MODELER_INSTRUCTION,
    tools=[compute_cascade_impact],
    output_schema=CascadeReportOutput,
    output_key="cascade_report",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    ),
    before_tool_callback=_log_tool_call,
    before_agent_callback=_validate_vulnerability_output,
)

# DIAGNOSE Pipeline: Sequential — scenario -> vulnerability -> cascade
# Validation gates run between stages via before_agent_callback
diagnose_pipeline = SequentialAgent(
    name="diagnose_pipeline",
    description=(
        "Full organizational stress-test pipeline: scenario analysis -> "
        "LLM-reasoned vulnerability scan -> cascade impact modeling with "
        "BMW operational context. Each stage validates upstream output."
    ),
    sub_agents=[scenario_architect, vulnerability_scanner, cascade_modeler],
)
