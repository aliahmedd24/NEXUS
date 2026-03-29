"""Shared ADK callbacks used across all NEXUS agents."""

import re

import click
import structlog

logger = structlog.get_logger()

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?\s*```$", re.DOTALL)


def strip_code_fences(callback_context, llm_response):
    """Strip markdown code fences from LLM text responses.

    Gemini models often wrap JSON output in ```json ... ``` even when
    output_schema is set. This after_model_callback strips the fences
    so ADK's Pydantic validation receives clean JSON.

    Args:
        callback_context: ADK callback context.
        llm_response: The LlmResponse from the model.

    Returns:
        The modified LlmResponse if fences were stripped, else None.
    """
    if not llm_response.content or not llm_response.content.parts:
        return None

    modified = False
    for part in llm_response.content.parts:
        if part.text:
            match = _FENCE_RE.match(part.text.strip())
            if match:
                part.text = match.group(1)
                modified = True
                logger.debug(
                    "strip_code_fences",
                    msg="Stripped markdown code fences from model response",
                )

    return llm_response if modified else None


def log_tool_call(tool, args, tool_context):
    """Print tool calls to terminal so the user sees progress."""
    click.echo(
        f"  \u2699 {tool.name}({', '.join(f'{k}={v!r}' for k, v in args.items())})",
        err=True,
    )
    return None
