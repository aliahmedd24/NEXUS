# NEXUS — Synthetic Seed Data

## Quick Start

```bash
# Create the database
createdb nexus

# Run all seed files in order
chmod +x run_seed.sh
./run_seed.sh postgresql://localhost:5432/nexus

# Or run individually:
psql nexus -f 00_schema.sql
psql nexus -f 01_org_structure.sql
# ... etc
```

## Data Inventory

| File | Table(s) | Rows | Description |
|------|----------|------|-------------|
| 00_schema.sql | All tables | DDL | Schema creation with all constraints |
| 01_org_structure.sql | org_units, org_dependencies | 13 + 12 | BMW Group org hierarchy and cascade graph |
| 02_leaders_and_roles.sql | leaders, roles | 24 + 10 | All leaders/candidates and role definitions |
| 03_jd_templates.sql | jd_templates | 8 | Base JD competency weightings per role type |
| 04_leadership_genomes.sql | leader_capability_scores | 288 | 12-dimension genome for all 24 profiles |
| 05_scenarios.sql | scenarios | 8 | BMW-specific stress scenarios |
| 06_feedback_360.sql | feedback_360 | 24 | Unstructured 360° feedback text |
| 07_performance_reviews.sql | performance_reviews | 18 | Performance data showing compressed ratings |
| 08_interaction_rules.sql | interaction_rules | 15 | Team chemistry dimension interaction rules |
| 09_historical_decisions.sql | historical_decisions, decision_outcomes, calibration_coefficients | 10 + 28 + 12 | Past appointments with outcomes for LEARN mode |
| 10_vulnerability_and_cascades.sql | vulnerability_assessments, cascade_impacts | 18 + 5 | Pre-computed scenario vulnerability analysis |
| 11_counterfactuals_and_compatibility.sql | counterfactual_results, compatibility_assessments | 5 + 15 | What-if analyses and team chemistry data |

## Entity Relationship Map

```
BMW Group HQ
├── Plant Munich ─────────────── Plant Director (Dr. Katharina Weiss) ★ EXCELLENT
│   ├── VP Production (Thomas Richter) ★ RETIRING
│   ├── VP Quality (Markus Brenner) ★ SOLID
│   ├── Head of Logistics (Jürgen Mayer) ★ STRUGGLING
│   └── HR Director (Anna Bergmann) ★ SOLID
├── Plant Dingolfing
├── Plant Spartanburg ────────── VP Production (James Carter) ★ ICE SPECIALIST
├── Plant Debrecen ───────────── Plant Director ★★ VACANT (Neue Klasse)
├── Neue Klasse Program Office
│   └── EV Battery Systems ──── Head of EV Battery ★★ VACANT (critical)
├── Supply Chain EMEA ────────── Head of SC (Dr. Lena Hoffmann) ★ FLIGHT RISK
├── IT & Digital / iFACTORY ──── Head of Digital (Stefan Krause) ★ WRONG ROLE
├── HR Central
├── Quality Central
├── R&D FIZ
└── BMW Motorrad
```

## Candidate Archetypes (Demo Narratives)

### Internal Candidates
| Name | Archetype | Demo Purpose |
|------|-----------|-------------|
| Dr. Felix Hartmann | "Internal Favorite" | Everyone expects him to replace Richter, but genome shows he's steady-state, not transformation. System flags the mismatch. |
| Lisa Weber | "Hidden Potential" | Junior title but exceptional change management and cross-functional scores. System surfaces her as unexpected top candidate. |
| Dr. Aisha Patel | "Domain Expert" | Deep battery expertise, natural fit for EV Battery Systems. System validates with high technical_depth confidence. |
| Michael Schneider | "Solid, Low Risk" | Baseline comparison. Good but unexceptional. Shows what "safe choice" looks like in the genome. |
| Sandra Voss | "Succession Backup" | Hoffmann's deputy. If Hoffmann leaves, Voss is the pipeline. Shows succession planning in action. |
| Tobias Krüger | "Long-term Bet" | 24-month readiness. Demonstrates the develop/internal strategy option. |

### External Candidates
| Name | Archetype | Demo Purpose |
|------|-----------|-------------|
| David Park (Amazon) | **THE UNICORN** | Perfect on paper — top scores on execution, strategy, innovation. But cultural_sensitivity: 0.32, cross_functional: 0.38. Team chemistry engine flags him as destructive. **Key demo moment.** |
| Dr. Elena Voronova (Bosch) | **THE HIDDEN GEM** | No OEM experience (apparent weakness). But change_management: 0.92, cultural_sensitivity: 0.90, people_development: 0.85. Genome reveals her as the best team fit. **Key demo moment.** |
| Sarah Chen (Tesla) | "Culture Clash Risk" | EV-native, high innovation, but Tesla culture ≠ BMW culture. Team chemistry shows friction with works council dynamics. |
| Claudia Fischer (VW) | "Proven at Scale" | Led VW Zwickau EV transformation. Strongest all-round external candidate. Non-compete risk. |
| Dr. Klaus Reimann (Mercedes) | "Competitor Veteran" | Strong but incremental improvement over internal options. High cost. |
| Marcus Williams (McKinsey) | "Strategy Without Execution" | Strategic_thinking: 0.92, operational_execution: 0.48. Demonstrates why consulting backgrounds fail in plant leadership. |

## Key Demo Data Points

### Compressed Ratings Problem
Performance reviews show ratings clustered in 6.5–8.5 range. The Leadership Genome Agent decompresses these using 360° text analysis and project outcome data:
- Thomas Richter: review rating 7.8 → genome change_management corrected to 0.45 (was 0.70 raw)
- Stefan Krause: review rating 7.2 → genome innovation_orientation corrected to 0.38 (was 0.68 raw)

### Scenario Sensitivity
Under S1 (Neue Klasse Ramp-Up), the org has **4 RED cells** in the vulnerability heatmap:
1. VP Production Munich (Richter) — gap 0.58
2. Head of EV Battery Systems (VACANT) — gap 0.95
3. Head of Digital/iFACTORY (Krause) — gap 0.52
4. Head of Production Logistics (Mayer) — gap 0.62

Under S7 (Steady-State Growth), only **1 RED cell** remains (Mayer, who's struggling regardless).

### Cascade Impact (€ values)
- EV Battery Systems vacancy cascade: **€15.5M** + 120 days delay
- Plant Director Debrecen vacancy cascade: **€42M** + 180 days delay
- VP Production Munich gap cascade: **€8.2M** + 45 days delay

### Historical Learning (Bias Mirror)
The calibration coefficients reveal BMW's systematic biases:
- **Overweighted**: operational_execution (+35%), technical_depth (+22%), cultural_sensitivity (+15%)
- **Underweighted**: change_management (-28%), innovation_orientation (-25%), people_development (-15%)

This directly explains the Krause and Mayer mis-hires.

## UUID Scheme

For easy debugging, UUIDs follow a deterministic pattern:

| Prefix | Entity |
|--------|--------|
| 10000000-... | Org units |
| 11000000-... | Org dependencies |
| 20000000-... | Roles |
| 30000000-... | Current leaders |
| 31000000-... | Internal candidates |
| 32000000-... | External candidates |
| 33000000-... | Historical-only leaders |
| 40000000-... | Scenarios |
| 50000000-... | JD templates |
| 60000000-... | Leadership genome scores |
| 61000000-... | 360° feedback |
| 62000000-... | Performance reviews |
| 70000000-... | Interaction rules |
| 80000000-... | Historical decisions |
| 81000000-... | Decision outcomes |
| 82000000-... | Calibration coefficients |
| 83000000-... | Counterfactual results |
| 84000000-... | Compatibility assessments |
| 90000000-... | Vulnerability assessments |
| 91000000-... | Cascade impacts |
