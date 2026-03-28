"""Tools for the Decision Brief Generator agent.

Provides dissent surfacing and confidence rating for board-ready briefs.
These tools compare outputs from upstream agents to identify disagreements
and assess overall recommendation quality.
"""

import json


def surface_dissent(
    genome_ranking_json: str, chemistry_report_json: str,
) -> dict:
    """Identify where STAFF agents disagree.

    Compares genome_agent candidate ranking with team_chemistry compatibility
    scores. Flags cases where the #1 candidate by fit has poor team chemistry,
    or where the best chemistry match ranks low on fit.

    Args:
        genome_ranking_json: JSON of ranked candidates by fit score.
        chemistry_report_json: JSON of team chemistry scores per candidate.

    Returns:
        Dissent report: disagreements, severity, explanation.
    """
    ranking = (
        json.loads(genome_ranking_json)
        if isinstance(genome_ranking_json, str)
        else genome_ranking_json
    )
    chemistry = (
        json.loads(chemistry_report_json)
        if isinstance(chemistry_report_json, str)
        else chemistry_report_json
    )

    disagreements: list[dict] = []

    if ranking and chemistry:
        # Check if top-ranked candidate has chemistry issues
        top_fit = ranking[0] if isinstance(ranking, list) else {}
        top_id = top_fit.get("leader_id", "")

        chem_list = (
            chemistry if isinstance(chemistry, list) else [chemistry]
        )
        chem_for_top = next(
            (c for c in chem_list if c.get("candidate_id") == top_id),
            None,
        )

        if chem_for_top and chem_for_top.get("average_synergy", 1) < 0.0:
            disagreements.append({
                "type": "fit_vs_chemistry",
                "candidate": top_fit.get("full_name", "Unknown"),
                "fit_rank": 1,
                "chemistry_score": chem_for_top.get("average_synergy"),
                "explanation": (
                    f"Top candidate by fit score has negative team synergy "
                    f"({chem_for_top.get('average_synergy', 0):.3f}). "
                    "Risk of interpersonal friction."
                ),
                "severity": "high",
            })

        # Check if a lower-ranked candidate has much better chemistry
        if len(ranking) >= 2:
            for i, cand in enumerate(ranking[1:5], start=2):
                cand_id = cand.get("leader_id", "")
                chem_for_cand = next(
                    (c for c in chem_list if c.get("candidate_id") == cand_id),
                    None,
                )
                if (
                    chem_for_cand
                    and chem_for_cand.get("average_synergy", 0) > 0.1
                    and chem_for_top
                    and chem_for_top.get("average_synergy", 0) < 0.0
                ):
                    disagreements.append({
                        "type": "chemistry_vs_fit",
                        "candidate": cand.get("full_name", "Unknown"),
                        "fit_rank": i,
                        "chemistry_score": chem_for_cand.get("average_synergy"),
                        "explanation": (
                            f"Rank #{i} candidate has better team chemistry "
                            f"than #1. Consider team fit trade-off."
                        ),
                        "severity": "medium",
                    })

    return {"disagreements": disagreements, "count": len(disagreements)}


def compute_confidence_rating(
    data_quality_json: str, agent_agreement_json: str,
) -> dict:
    """Rate overall recommendation confidence.

    Assesses confidence based on data completeness (genome coverage,
    calibration status) and agent agreement (dissent count).

    Args:
        data_quality_json: JSON summary of data completeness per candidate.
        agent_agreement_json: JSON summary of agent alignment.

    Returns:
        Confidence level (high/medium/low) with reasoning and improvement
        suggestions.
    """
    quality = (
        json.loads(data_quality_json)
        if isinstance(data_quality_json, str) and data_quality_json
        else data_quality_json if isinstance(data_quality_json, dict)
        else {}
    )
    agreement = (
        json.loads(agent_agreement_json)
        if isinstance(agent_agreement_json, str) and agent_agreement_json
        else agent_agreement_json if isinstance(agent_agreement_json, dict)
        else {}
    )

    issues: list[str] = []
    if quality.get("incomplete_genomes", 0) > 2:
        issues.append("Multiple candidates have incomplete genome data.")
    if agreement.get("disagreement_count", 0) > 0:
        issues.append("Agents disagree on top candidate.")
    if quality.get("wide_ci_count", 0) > 3:
        issues.append("Several dimensions have wide confidence intervals.")

    level = (
        "high" if len(issues) == 0
        else "medium" if len(issues) == 1
        else "low"
    )

    suggestions: list[str] = []
    if not quality.get("calibration_applied"):
        suggestions.append(
            "Run LEARN mode to apply historical calibration."
        )
    if quality.get("wide_ci_count", 0) > 0:
        suggestions.append(
            "Gather additional 360 feedback for candidates with "
            "wide confidence intervals."
        )
    if quality.get("feedback_count", 0) < 3:
        suggestions.append(
            "Collect more 360 feedback to strengthen genome accuracy."
        )

    return {
        "confidence": level,
        "reasoning": (
            "; ".join(issues) if issues
            else "All agents agree, data is complete."
        ),
        "improvement_suggestions": suggestions,
    }
