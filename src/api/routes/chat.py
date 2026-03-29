"""Chat API route — exposes ADK agents via streaming SSE.

This is the core endpoint that lets the frontend converse with NEXUS agents.
Each message is routed through the ADK orchestrator, which delegates to
DIAGNOSE, STAFF, or LEARN pipelines. Tool calls and intermediate thinking
steps are streamed back as Server-Sent Events.
"""

import json
import time
import uuid

import click
import structlog
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from pydantic import BaseModel

from src.agents.agent import root_agent

logger = structlog.get_logger()

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Tools whose results should be forwarded to the frontend for visualization.
# Maps tool name → visualization type that the frontend routes on.
VISUALIZATION_TOOLS: dict[str, str] = {
    # DIAGNOSE
    "scan_vulnerabilities": "diagnose_heatmap",
    "compute_cascade_impact": "diagnose_cascade",
    "identify_single_points_of_failure": "diagnose_spof",
    # STAFF
    "rank_candidates": "staff_ranking",
    "get_leader_genome": "staff_genome",
    "compute_team_compatibility": "staff_chemistry",
    "generate_staffing_plan": "staff_plan",
    "compute_candidate_fit": "staff_fit",
    # LEARN
    "get_historical_decisions": "learn_decisions",
    "detect_bias_patterns": "learn_biases",
    "reconstruct_decision": "learn_replay",
    "get_decision_outcomes": "learn_outcomes",
    "simulate_counterfactual": "learn_counterfactual",
    "get_calibration_coefficients": "learn_calibration",
    "update_calibration_from_biases": "learn_calibration_updated",
}

# Default app name for ADK sessions
APP_NAME = "nexus"

# Singleton session service — persists sessions across requests
_session_service = InMemorySessionService()

# Singleton runner
_runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=_session_service,
)

# ─── Terminal Colors ──────────────────────────────────────────────────

CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
MAGENTA = "\033[35m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
BLUE = "\033[34m"


def _log_header(label: str, color: str, detail: str = "") -> None:
    """Print a prominent section header to the terminal."""
    detail_str = f"  {DIM}{detail}{RESET}" if detail else ""
    click.echo(f"\n{color}{BOLD}{'─' * 3} {label} {'─' * 40}{RESET}{detail_str}", err=True)


def _log_event(icon: str, color: str, label: str, detail: str = "") -> None:
    """Print a single event line to the terminal."""
    ts = time.strftime("%H:%M:%S")
    detail_str = f"  {DIM}{detail}{RESET}" if detail else ""
    click.echo(f"  {DIM}{ts}{RESET}  {color}{icon} {label}{RESET}{detail_str}", err=True)


def _detect_llm_viz_type(data: dict) -> str | None:
    """Detect which visualization type an LLM structured output maps to.

    Returns the viz type string if the output matches a known schema, else None.
    The LLM output contains REASONED values (not mechanical formula outputs).
    """
    if "heatmap" in data and "aggregate_resilience_score" in data:
        return "diagnose_heatmap_llm"
    if "cascade_chain" in data and "total_exposure_eur" in data:
        return "diagnose_cascade_llm"
    if "ranked_candidates" in data and "org_unit_id" in data:
        return "staff_ranking_llm"
    if "pairwise_assessments" in data and "overall_team_fit" in data:
        return "staff_chemistry_llm"
    if "staffing_recommendations" in data:
        return "staff_plan_llm"
    if "replays" in data and "overall_decision_quality" in data:
        return "learn_replay_llm"
    if "bias_mirror" in data and "success_dna" in data:
        return "learn_biases_llm"
    return None


def _summarize_json_response(text: str, author: str) -> str | None:
    """If text is structured JSON from an output_schema agent, return a human summary.

    Returns None if text is not JSON or cannot be summarized.
    """
    stripped = text.strip()
    if not (stripped.startswith("{") or stripped.startswith("[")):
        return None
    try:
        data = json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        return None

    if not isinstance(data, dict):
        return None

    lines: list[str] = []

    # ── DIAGNOSE: Scenario Analysis ──────────────────────────────────
    if "scenario_name" in data and "narrative_summary" in data:
        lines.append(f"**Scenario: {data.get('scenario_name', 'Unknown')}**")
        if data.get("narrative_summary"):
            lines.append(data["narrative_summary"])
        if data.get("recommendation"):
            lines.append(f"\n**Recommendation:** {data['recommendation']}")
        prob = data.get("probability")
        if prob is not None:
            lines.append(f"Probability: {prob * 100:.0f}%")

    # ── DIAGNOSE: Vulnerability Report ───────────────────────────────
    elif "aggregate_resilience_score" in data and "heatmap" in data:
        score = data.get("aggregate_resilience_score", 0)
        critical = data.get("critical_count", 0)
        warning = data.get("warning_count", 0)
        covered = data.get("covered_count", 0)
        scenario = data.get("scenario_name", "the scenario")
        lines.append(f"**Vulnerability scan complete for {scenario}.**")
        lines.append(f"Resilience: **{score * 100:.0f}%** — {critical} critical, {warning} warning, {covered} covered.")
        spofs = data.get("single_points_of_failure", [])
        if spofs:
            lines.append(f"Single points of failure: {', '.join(str(s) for s in spofs[:3])}")
        actions = data.get("priority_actions", [])
        if actions:
            lines.append("\n**Priority actions:**")
            for a in actions[:3]:
                lines.append(f"• {a}")

    # ── DIAGNOSE: Cascade Report ─────────────────────────────────────
    elif "cascade_chain" in data and ("total_exposure_eur" in data or "total_impact_eur" in data or "mechanical_total_eur" in data):
        trigger = data.get("trigger_role") or data.get("role_title") or data.get("trigger_scenario") or "trigger"
        exposure = data.get("total_exposure_eur") or data.get("total_impact_eur") or data.get("mechanical_total_eur", 0)
        chain = data.get("cascade_chain", [])
        lines.append(f"**Cascade impact analysis from {trigger}.**")
        lines.append(f"Total exposure: **€{exposure:,.0f}** across {len(chain)} downstream units.")
        if data.get("optimal_intervention"):
            lines.append(f"Optimal intervention: {data['optimal_intervention']}")
        if data.get("business_translation"):
            lines.append(f"\n{data['business_translation']}")

    # ── STAFF: Adapted JD ────────────────────────────────────────────
    elif "top_5_requirements" in data and "role_type" in data:
        role = data.get("role_type", "role")
        pool = data.get("estimated_market_pool_size", "unknown")
        lines.append(f"**Adapted job description for {role}.**")
        lines.append(f"Market pool: {pool}.")
        reqs = data.get("top_5_requirements", [])
        if reqs:
            lines.append("Top requirements:")
            for r in reqs[:5]:
                dim = r.get("dimension", "?").replace("_", " ").title()
                wt = r.get("adapted_weight", 0)
                lines.append(f"• {dim} (weight: {wt:.2f})")
        flags = data.get("critique_flags", [])
        if flags:
            lines.append(f"\n⚠ Flags: {'; '.join(str(f) for f in flags[:3])}")

    # ── STAFF: Genome Analysis / Ranking ─────────────────────────────
    elif "ranked_candidates" in data:
        role = data.get("role_type", "the role")
        candidates = data.get("ranked_candidates", [])
        lines.append(f"**Genome analysis complete for {role}.**")
        lines.append(f"{len(candidates)} candidates ranked.")
        for i, c in enumerate(candidates[:3]):
            name = c.get("candidate_name", "Unknown")
            fit = c.get("overall_fit_score", 0)
            ctype = c.get("leader_type", "").replace("_", " ")
            lines.append(f"{i + 1}. **{name}** ({ctype}) — fit: {fit:.2f}")
        if data.get("bias_detection_summary"):
            lines.append(f"\n*Bias note:* {data['bias_detection_summary']}")

    # ── STAFF: Team Chemistry ────────────────────────────────────────
    elif "overall_team_fit" in data and "pairwise_assessments" in data:
        name = data.get("candidate_name", "candidate")
        fit = data.get("overall_team_fit", 0)
        lines.append(f"**Team chemistry for {name}: {fit:.2f}**")
        for p in data.get("pairwise_assessments", [])[:3]:
            member = p.get("team_member_name", "?")
            synergy = p.get("synergy_score", 0)
            sign = "+" if synergy >= 0 else ""
            lines.append(f"• {member}: {sign}{synergy:.2f}")
        if data.get("headline_insight"):
            lines.append(f"\n{data['headline_insight']}")

    # ── STAFF: Portfolio Optimizer ────────────────────────────────────
    elif "staffing_recommendations" in data:
        recs = data.get("staffing_recommendations", [])
        total = data.get("total_investment_eur", 0)
        improvement = data.get("aggregate_resilience_improvement", 0)
        lines.append(f"**Staffing plan: {len(recs)} position(s), €{total:,.0f} investment.**")
        lines.append(f"Projected resilience improvement: {improvement * 100:.1f}%")
        for r in recs[:3]:
            role = r.get("role_title", "?")
            cand = r.get("recommended_candidate", "TBD")
            strategy = r.get("sourcing_strategy", "").replace("_", " ").lower()
            lines.append(f"• {role} → {cand} ({strategy})")
        if data.get("roi_estimate"):
            lines.append(f"\nROI: {data['roi_estimate']}")

    # ── LEARN: Replay Analysis ───────────────────────────────────────
    elif "replays" in data and "decisions_analyzed" in data:
        n = data.get("decisions_analyzed", 0)
        quality = data.get("overall_decision_quality", "")
        lines.append(f"**Decision replay: {n} decisions analyzed.**")
        if quality:
            lines.append(quality)
        for r in data.get("replays", [])[:3]:
            role = r.get("role_title", "?")
            cat = r.get("divergence_category", "?")
            lines.append(f"• {role}: **{cat}**")

    # ── LEARN: Learning Report / Bias ────────────────────────────────
    elif "bias_mirror" in data:
        biases = data.get("bias_mirror", [])
        lines.append(f"**Bias analysis: {len(biases)} dimensions evaluated.**")
        for b in biases[:4]:
            dim = b.get("dimension", "?").replace("_", " ").title()
            mag = b.get("magnitude_pct", 0)
            direction = b.get("direction", "?")
            lines.append(f"• {dim}: {'+' if mag > 0 else ''}{mag:.1f}% ({direction})")
        dna = data.get("success_dna", [])
        if dna:
            lines.append(f"\nSuccess DNA: {', '.join(str(d) for d in dna[:3])}")
        if data.get("calibration_updated"):
            lines.append("✓ Calibration coefficients updated.")

    # ── BRIEF: Decision Brief ────────────────────────────────────────
    elif "executive_summary" in data and "recommendation" in data:
        title = data.get("title", "Decision Brief")
        lines.append(f"**{title}**")
        lines.append(data.get("executive_summary", ""))
        lines.append(f"\n**Recommendation:** {data.get('recommendation', '')}")
        confidence = data.get("confidence_level", "")
        if confidence:
            lines.append(f"Confidence: {confidence} — {data.get('confidence_reasoning', '')}")
        steps = data.get("suggested_next_steps", [])
        if steps:
            lines.append("\n**Next steps:**")
            for s in steps[:3]:
                lines.append(f"• {s}")

    # ── Fallback: unknown JSON shape ─────────────────────────────────
    else:
        return None

    return "\n".join(lines) if lines else None


class ChatRequest(BaseModel):
    """Request body for chat messages."""

    message: str
    session_id: str | None = None
    mode: str | None = None  # diagnose, staff, learn — hint for orchestrator


class SessionResponse(BaseModel):
    """Response with session info."""

    session_id: str


@router.post("/session")
async def create_session() -> SessionResponse:
    """Create a new chat session. Returns session_id for subsequent messages."""
    session_id = str(uuid.uuid4())
    session = await _session_service.create_session(
        app_name=APP_NAME,
        user_id="nexus-user",
        session_id=session_id,
    )
    _log_event("●", GREEN, "SESSION CREATED", f"id={session.id[:12]}…")
    return SessionResponse(session_id=session.id)


@router.post("/message")
async def send_message(request: ChatRequest):
    """Send a message and stream back agent responses via SSE.

    Returns a stream of Server-Sent Events with these event types:
    - thinking: Agent's intermediate reasoning
    - tool_call: Tool invocation with name and arguments
    - tool_result: Tool response data
    - text: Agent's text response chunks
    - done: Final event, stream complete
    - error: Error occurred
    """
    session_id = request.session_id
    if not session_id:
        session = await _session_service.create_session(
            app_name=APP_NAME,
            user_id="nexus-user",
        )
        session_id = session.id

    # Ensure session exists
    existing = await _session_service.get_session(
        app_name=APP_NAME,
        user_id="nexus-user",
        session_id=session_id,
    )
    if not existing:
        await _session_service.create_session(
            app_name=APP_NAME,
            user_id="nexus-user",
            session_id=session_id,
        )

    # Pass message as-is — let the orchestrator infer intent from content.
    # The mode hint was causing conflicts when user intent didn't match the active UI tab.
    user_text = request.message

    user_content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=user_text)],
    )

    # ─── Verbose terminal logging ─────────────────────────────────────
    mode_colors = {"diagnose": RED, "staff": BLUE, "learn": MAGENTA}
    mode_color = mode_colors.get(request.mode or "", CYAN)
    _log_header(
        f"CHAT » {(request.mode or 'auto').upper()}",
        mode_color,
        f"session={session_id[:12]}…",
    )
    _log_event("▶", CYAN, "USER", request.message[:120])

    t_start = time.time()
    event_count = 0
    tool_count = 0

    async def event_stream():
        """Generate SSE events from ADK runner."""
        nonlocal event_count, tool_count

        try:
            yield _sse("session", {"session_id": session_id})

            async for event in _runner.run_async(
                user_id="nexus-user",
                session_id=session_id,
                new_message=user_content,
            ):
                event_count += 1

                # Tool calls
                func_calls = event.get_function_calls()
                if func_calls:
                    for fc in func_calls:
                        tool_count += 1
                        args_str = ", ".join(
                            f"{k}={repr(v)[:60]}" for k, v in (fc.args or {}).items()
                        )
                        _log_event(
                            "⚙",
                            YELLOW,
                            f"TOOL CALL [{event.author}]",
                            f"{fc.name}({args_str})",
                        )
                        yield _sse("tool_call", {
                            "agent": event.author,
                            "tool": fc.name,
                            "args": fc.args if fc.args else {},
                        })

                # Tool results
                func_responses = event.get_function_responses()
                if func_responses:
                    for fr in func_responses:
                        response_str = json.dumps(fr.response, default=str)
                        _log_event(
                            "✓",
                            GREEN,
                            f"TOOL RESULT [{event.author}]",
                            f"{fr.name} → {len(response_str)} chars",
                        )
                        truncated = response_str
                        if len(truncated) > 2000:
                            truncated = truncated[:2000] + "..."
                        yield _sse("tool_result", {
                            "agent": event.author,
                            "tool": fr.name,
                            "result_preview": truncated,
                        })

                        # Emit full visualization data for key tools
                        viz_type = VISUALIZATION_TOOLS.get(fr.name)
                        if viz_type and fr.response:
                            _log_event(
                                "📊",
                                MAGENTA,
                                f"VIZ [{viz_type}]",
                                f"{len(response_str)} chars → frontend",
                            )
                            yield _sse("visualization", {
                                "type": viz_type,
                                "tool": fr.name,
                                "data": fr.response,
                            })

                # Text content (agent responses + thinking)
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "thought") and part.thought:
                            thinking_preview = (part.text or "")[:150].replace("\n", " ")
                            _log_event(
                                "💭",
                                DIM,
                                f"THINKING [{event.author}]",
                                thinking_preview,
                            )
                            yield _sse("thinking", {
                                "agent": event.author,
                                "text": part.text or "",
                            })
                        elif part.text:
                            is_final = bool(event.is_final_response())

                            # Convert structured JSON output to readable text
                            display_text = part.text
                            summary = _summarize_json_response(part.text, event.author)
                            if summary:
                                display_text = summary
                                _log_event(
                                    "📝",
                                    GREEN,
                                    f"SUMMARIZED [{event.author}]",
                                    display_text[:150].replace("\n", " "),
                                )

                                # Emit LLM-reasoned output as visualization event
                                # so frontend can show LLM analysis overlaid on
                                # mechanical tool data
                                try:
                                    llm_data = json.loads(part.text)
                                    if isinstance(llm_data, dict):
                                        llm_viz_type = _detect_llm_viz_type(llm_data)
                                        if llm_viz_type:
                                            _log_event(
                                                "🧠",
                                                MAGENTA,
                                                f"LLM VIZ [{event.author}]",
                                                llm_viz_type,
                                            )
                                            yield _sse("visualization", {
                                                "type": llm_viz_type,
                                                "tool": f"llm:{event.author}",
                                                "data": llm_data,
                                            })
                                except (json.JSONDecodeError, ValueError):
                                    pass
                            else:
                                text_preview = part.text[:150].replace("\n", " ")
                                marker = f" {GREEN}[FINAL]{RESET}" if is_final else ""
                                _log_event(
                                    "◆",
                                    mode_color,
                                    f"TEXT [{event.author}]{marker}",
                                    text_preview,
                                )

                            yield _sse("text", {
                                "agent": event.author,
                                "text": display_text,
                                "is_final": is_final,
                            })

                # Final response marker
                if event.is_final_response():
                    elapsed = time.time() - t_start
                    _log_event(
                        "■",
                        GREEN,
                        "DONE",
                        f"{event_count} events, {tool_count} tool calls, {elapsed:.1f}s",
                    )
                    click.echo(
                        f"  {DIM}{'─' * 56}{RESET}\n",
                        err=True,
                    )
                    yield _sse("done", {"agent": event.author})

        except Exception as e:
            elapsed = time.time() - t_start
            _log_event("✗", RED, "ERROR", f"{type(e).__name__}: {e}")
            logger.error("chat_stream_error", error=str(e))
            yield _sse("error", {"message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _sse(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data, default=str)}\n\n"
