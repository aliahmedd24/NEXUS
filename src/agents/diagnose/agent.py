"""DIAGNOSE mode agents and pipeline.

Agents: Scenario Architect -> Vulnerability Scanner -> Cascade Modeler
Pattern: SequentialAgent with structured output schemas and validation callbacks.
"""

import click
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
    create_compound_scenario,
    get_scenario_by_name,
    get_scenario_library,
    identify_single_points_of_failure,
    scan_vulnerabilities,
)


def _log_tool_call(tool, args, tool_context):
    """Print tool calls to terminal so the user sees progress."""
    click.echo(f"  ⚙ {tool.name}({', '.join(f'{k}={v!r}' for k, v in args.items())})", err=True)
    return None

scenario_architect = LlmAgent(
    name="scenario_architect",
    model=settings.gemini_model_fast,
    description=(
        "Selects and analyzes BMW stress-test scenarios. Handles scenario "
        "library lookup, compound scenario creation, and business impact assessment."
    ),
    instruction=SCENARIO_ARCHITECT_INSTRUCTION,
    tools=[get_scenario_library, get_scenario_by_name, create_compound_scenario],
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
        "Scans leadership roles against scenario demands. Produces color-coded "
        "vulnerability heatmap and identifies single points of failure."
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
)

cascade_modeler = LlmAgent(
    name="cascade_modeler",
    model=settings.gemini_model_pro,
    description=(
        "Models downstream cascade impacts when leadership roles fail. Quantifies "
        "business exposure in EUR and identifies optimal intervention points."
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
)

# DIAGNOSE Pipeline: Sequential — scenario -> vulnerability -> cascade
diagnose_pipeline = SequentialAgent(
    name="diagnose_pipeline",
    description=(
        "Full organizational stress-test: scenario analysis -> "
        "vulnerability scan -> cascade modeling."
    ),
    sub_agents=[scenario_architect, vulnerability_scanner, cascade_modeler],
)
