"""
NEXUS — Leadership Genome Score Generator
Generates 12-dimension genome profiles for all 24 leaders/candidates.
Each profile is hand-tuned to match their narrative role in the demo.
"""

import uuid
import json

DIMENSIONS = [
    "strategic_thinking",
    "operational_execution",
    "change_management",
    "crisis_leadership",
    "people_development",
    "technical_depth",
    "cross_functional_collaboration",
    "innovation_orientation",
    "cultural_sensitivity",
    "risk_calibration",
    "stakeholder_management",
    "resilience_adaptability",
]

# Format: (leader_id, name, narrative_role, scores_dict, bias_corrections, assessor_type)
# Scores: raw_score, then we apply bias corrections to get corrected_score
# Confidence intervals are ± offset from corrected score

PROFILES = [
    # ========== CURRENT LEADERS (8) ==========

    # L01: Dr. Katharina Weiss — Plant Director Munich (EXCELLENT)
    ("30000000-0000-0000-0000-000000000001", "Dr. Katharina Weiss", {
        "strategic_thinking":              (0.78, 0.91, 0.06, "assessment_center"),
        "operational_execution":           (0.82, 0.88, 0.05, "manager"),
        "change_management":               (0.75, 0.87, 0.07, "assessment_center"),
        "crisis_leadership":               (0.80, 0.85, 0.06, "peer"),
        "people_development":              (0.82, 0.90, 0.05, "direct_report"),
        "technical_depth":                 (0.72, 0.76, 0.08, "assessment_center"),
        "cross_functional_collaboration":  (0.80, 0.88, 0.05, "peer"),
        "innovation_orientation":          (0.68, 0.74, 0.08, "peer"),
        "cultural_sensitivity":            (0.85, 0.89, 0.04, "peer"),
        "risk_calibration":                (0.78, 0.82, 0.06, "assessment_center"),
        "stakeholder_management":          (0.82, 0.90, 0.05, "manager"),
        "resilience_adaptability":         (0.80, 0.86, 0.05, "ai_extracted"),
    }),

    # L02: Thomas Richter — VP Production Munich (RETIRING, analog mindset)
    ("30000000-0000-0000-0000-000000000002", "Thomas Richter", {
        "strategic_thinking":              (0.72, 0.68, 0.07, "manager"),
        "operational_execution":           (0.85, 0.92, 0.04, "manager"),
        "change_management":               (0.70, 0.45, 0.10, "peer"),        # big correction — rated safe but actually resistant
        "crisis_leadership":               (0.78, 0.82, 0.06, "assessment_center"),
        "people_development":              (0.75, 0.72, 0.07, "direct_report"),
        "technical_depth":                 (0.82, 0.88, 0.05, "assessment_center"),
        "cross_functional_collaboration":  (0.72, 0.65, 0.08, "peer"),
        "innovation_orientation":          (0.68, 0.35, 0.12, "ai_extracted"), # big correction — analog mindset
        "cultural_sensitivity":            (0.75, 0.78, 0.06, "peer"),
        "risk_calibration":                (0.72, 0.70, 0.07, "assessment_center"),
        "stakeholder_management":          (0.78, 0.75, 0.06, "manager"),
        "resilience_adaptability":         (0.72, 0.58, 0.09, "ai_extracted"),
    }),

    # L03: Markus Brenner — VP Quality Munich (SOLID, steady)
    ("30000000-0000-0000-0000-000000000003", "Markus Brenner", {
        "strategic_thinking":              (0.72, 0.70, 0.07, "manager"),
        "operational_execution":           (0.80, 0.85, 0.05, "manager"),
        "change_management":               (0.72, 0.58, 0.09, "peer"),
        "crisis_leadership":               (0.78, 0.80, 0.06, "assessment_center"),
        "people_development":              (0.75, 0.73, 0.07, "direct_report"),
        "technical_depth":                 (0.82, 0.88, 0.05, "assessment_center"),
        "cross_functional_collaboration":  (0.78, 0.82, 0.06, "peer"),
        "innovation_orientation":          (0.68, 0.55, 0.10, "ai_extracted"),
        "cultural_sensitivity":            (0.82, 0.85, 0.05, "peer"),         # great with works council
        "risk_calibration":                (0.78, 0.80, 0.06, "assessment_center"),
        "stakeholder_management":          (0.75, 0.78, 0.06, "manager"),
        "resilience_adaptability":         (0.72, 0.72, 0.07, "ai_extracted"),
    }),

    # L04: Dr. Lena Hoffmann — Head of Supply Chain EMEA (BEING POACHED, brilliant)
    ("30000000-0000-0000-0000-000000000004", "Dr. Lena Hoffmann", {
        "strategic_thinking":              (0.80, 0.92, 0.05, "assessment_center"),
        "operational_execution":           (0.78, 0.82, 0.06, "manager"),
        "change_management":               (0.78, 0.85, 0.06, "peer"),
        "crisis_leadership":               (0.82, 0.90, 0.05, "assessment_center"),  # rebuilt post chip-shortage
        "people_development":              (0.72, 0.70, 0.08, "direct_report"),
        "technical_depth":                 (0.75, 0.78, 0.07, "assessment_center"),
        "cross_functional_collaboration":  (0.78, 0.84, 0.06, "peer"),
        "innovation_orientation":          (0.75, 0.80, 0.07, "ai_extracted"),
        "cultural_sensitivity":            (0.72, 0.75, 0.07, "peer"),
        "risk_calibration":                (0.78, 0.85, 0.06, "assessment_center"),
        "stakeholder_management":          (0.80, 0.88, 0.05, "manager"),
        "resilience_adaptability":         (0.80, 0.88, 0.05, "ai_extracted"),
    }),

    # L05: Stefan Krause — Head of Digital/iFACTORY (WRONG ROLE)
    ("30000000-0000-0000-0000-000000000005", "Stefan Krause", {
        "strategic_thinking":              (0.72, 0.48, 0.11, "ai_extracted"),   # big gap — rated OK but actually limited
        "operational_execution":           (0.82, 0.85, 0.05, "manager"),         # strong execution
        "change_management":               (0.70, 0.42, 0.12, "peer"),           # can't drive transformation
        "crisis_leadership":               (0.75, 0.72, 0.07, "assessment_center"),
        "people_development":              (0.72, 0.68, 0.08, "direct_report"),
        "technical_depth":                 (0.78, 0.75, 0.07, "assessment_center"), # good IT ops, weak on vision
        "cross_functional_collaboration":  (0.70, 0.58, 0.10, "peer"),
        "innovation_orientation":          (0.68, 0.38, 0.13, "ai_extracted"),   # critical gap for digital role
        "cultural_sensitivity":            (0.72, 0.70, 0.08, "peer"),
        "risk_calibration":                (0.72, 0.62, 0.09, "assessment_center"),
        "stakeholder_management":          (0.70, 0.60, 0.09, "manager"),
        "resilience_adaptability":         (0.72, 0.65, 0.08, "ai_extracted"),
    }),

    # L06: Anna Bergmann — HR Director Plant Munich (SOLID)
    ("30000000-0000-0000-0000-000000000006", "Anna Bergmann", {
        "strategic_thinking":              (0.72, 0.72, 0.07, "manager"),
        "operational_execution":           (0.78, 0.80, 0.06, "manager"),
        "change_management":               (0.75, 0.75, 0.07, "peer"),
        "crisis_leadership":               (0.70, 0.68, 0.08, "assessment_center"),
        "people_development":              (0.82, 0.88, 0.05, "direct_report"),
        "technical_depth":                 (0.68, 0.65, 0.09, "assessment_center"),
        "cross_functional_collaboration":  (0.80, 0.85, 0.05, "peer"),
        "innovation_orientation":          (0.68, 0.62, 0.09, "ai_extracted"),
        "cultural_sensitivity":            (0.85, 0.92, 0.04, "peer"),           # exceptional works council relations
        "risk_calibration":                (0.72, 0.72, 0.07, "assessment_center"),
        "stakeholder_management":          (0.80, 0.85, 0.05, "manager"),
        "resilience_adaptability":         (0.75, 0.78, 0.06, "ai_extracted"),
    }),

    # L07: Jürgen Mayer — Head of Production Logistics (STRUGGLING)
    ("30000000-0000-0000-0000-000000000007", "Jürgen Mayer", {
        "strategic_thinking":              (0.72, 0.45, 0.12, "ai_extracted"),
        "operational_execution":           (0.75, 0.55, 0.10, "manager"),
        "change_management":               (0.70, 0.40, 0.13, "peer"),
        "crisis_leadership":               (0.68, 0.42, 0.12, "assessment_center"),
        "people_development":              (0.68, 0.38, 0.14, "direct_report"),   # team attrition rising
        "technical_depth":                 (0.72, 0.68, 0.08, "assessment_center"),
        "cross_functional_collaboration":  (0.70, 0.50, 0.11, "peer"),
        "innovation_orientation":          (0.68, 0.52, 0.10, "ai_extracted"),
        "cultural_sensitivity":            (0.72, 0.65, 0.08, "peer"),
        "risk_calibration":                (0.68, 0.42, 0.13, "assessment_center"),  # overwhelmed
        "stakeholder_management":          (0.70, 0.48, 0.11, "manager"),
        "resilience_adaptability":         (0.68, 0.40, 0.14, "ai_extracted"),    # not coping
    }),

    # L08: James Carter — VP Production Spartanburg (DECENT, ICE specialist)
    ("30000000-0000-0000-0000-000000000008", "James Carter", {
        "strategic_thinking":              (0.72, 0.68, 0.08, "manager"),
        "operational_execution":           (0.82, 0.85, 0.05, "manager"),
        "change_management":               (0.70, 0.50, 0.10, "peer"),            # limited transformation experience
        "crisis_leadership":               (0.75, 0.78, 0.07, "assessment_center"),
        "people_development":              (0.78, 0.80, 0.06, "direct_report"),
        "technical_depth":                 (0.80, 0.82, 0.06, "assessment_center"), # ICE manufacturing depth
        "cross_functional_collaboration":  (0.75, 0.72, 0.07, "peer"),
        "innovation_orientation":          (0.68, 0.48, 0.11, "ai_extracted"),     # traditional approach
        "cultural_sensitivity":            (0.70, 0.65, 0.09, "peer"),
        "risk_calibration":                (0.75, 0.75, 0.07, "assessment_center"),
        "stakeholder_management":          (0.78, 0.80, 0.06, "manager"),
        "resilience_adaptability":         (0.72, 0.70, 0.08, "ai_extracted"),
    }),

    # ========== INTERNAL CANDIDATES (6) ==========

    # IC01: Dr. Felix Hartmann — "Internal Favorite" (steady-state, NOT transformation)
    ("31000000-0000-0000-0000-000000000001", "Dr. Felix Hartmann", {
        "strategic_thinking":              (0.75, 0.65, 0.08, "assessment_center"),
        "operational_execution":           (0.82, 0.88, 0.05, "manager"),          # his strength
        "change_management":               (0.72, 0.48, 0.11, "peer"),            # THE critical gap
        "crisis_leadership":               (0.72, 0.70, 0.08, "assessment_center"),
        "people_development":              (0.75, 0.72, 0.07, "direct_report"),
        "technical_depth":                 (0.80, 0.85, 0.06, "assessment_center"),
        "cross_functional_collaboration":  (0.72, 0.68, 0.08, "peer"),
        "innovation_orientation":          (0.68, 0.45, 0.12, "ai_extracted"),    # traditional thinker
        "cultural_sensitivity":            (0.78, 0.80, 0.06, "peer"),
        "risk_calibration":                (0.72, 0.68, 0.08, "assessment_center"),
        "stakeholder_management":          (0.75, 0.72, 0.07, "manager"),
        "resilience_adaptability":         (0.72, 0.65, 0.08, "ai_extracted"),
    }),

    # IC02: Lisa Weber — Hidden Potential (cross-functional superstar)
    ("31000000-0000-0000-0000-000000000002", "Lisa Weber", {
        "strategic_thinking":              (0.72, 0.82, 0.07, "assessment_center"),
        "operational_execution":           (0.72, 0.72, 0.08, "manager"),
        "change_management":               (0.75, 0.88, 0.06, "peer"),           # exceptional for her level
        "crisis_leadership":               (0.68, 0.72, 0.08, "assessment_center"),
        "people_development":              (0.72, 0.78, 0.07, "direct_report"),
        "technical_depth":                 (0.75, 0.80, 0.07, "assessment_center"), # battery integration workstream
        "cross_functional_collaboration":  (0.78, 0.90, 0.05, "peer"),           # superstar here
        "innovation_orientation":          (0.75, 0.85, 0.06, "ai_extracted"),
        "cultural_sensitivity":            (0.72, 0.75, 0.07, "peer"),
        "risk_calibration":                (0.68, 0.72, 0.08, "assessment_center"),
        "stakeholder_management":          (0.68, 0.70, 0.08, "manager"),
        "resilience_adaptability":         (0.75, 0.82, 0.06, "ai_extracted"),
    }),

    # IC03: Michael Schneider — Solid, Low Risk
    ("31000000-0000-0000-0000-000000000003", "Michael Schneider", {
        "strategic_thinking":              (0.70, 0.65, 0.08, "manager"),
        "operational_execution":           (0.80, 0.82, 0.06, "manager"),
        "change_management":               (0.72, 0.62, 0.09, "peer"),
        "crisis_leadership":               (0.72, 0.72, 0.07, "assessment_center"),
        "people_development":              (0.75, 0.75, 0.07, "direct_report"),
        "technical_depth":                 (0.78, 0.80, 0.06, "assessment_center"),
        "cross_functional_collaboration":  (0.72, 0.70, 0.08, "peer"),
        "innovation_orientation":          (0.68, 0.58, 0.10, "ai_extracted"),
        "cultural_sensitivity":            (0.75, 0.78, 0.07, "peer"),
        "risk_calibration":                (0.72, 0.72, 0.07, "assessment_center"),
        "stakeholder_management":          (0.72, 0.70, 0.08, "manager"),
        "resilience_adaptability":         (0.72, 0.72, 0.07, "ai_extracted"),
    }),

    # IC04: Dr. Aisha Patel — Deep EV Battery Expert
    ("31000000-0000-0000-0000-000000000004", "Dr. Aisha Patel", {
        "strategic_thinking":              (0.75, 0.80, 0.07, "assessment_center"),
        "operational_execution":           (0.72, 0.72, 0.08, "manager"),
        "change_management":               (0.72, 0.78, 0.07, "peer"),
        "crisis_leadership":               (0.68, 0.68, 0.09, "assessment_center"),
        "people_development":              (0.70, 0.68, 0.08, "direct_report"),
        "technical_depth":                 (0.85, 0.95, 0.03, "assessment_center"), # exceptional battery expertise
        "cross_functional_collaboration":  (0.72, 0.75, 0.07, "peer"),
        "innovation_orientation":          (0.80, 0.88, 0.05, "ai_extracted"),
        "cultural_sensitivity":            (0.68, 0.65, 0.09, "peer"),             # still adapting to BMW from CATL
        "risk_calibration":                (0.72, 0.75, 0.07, "assessment_center"),
        "stakeholder_management":          (0.68, 0.65, 0.09, "manager"),
        "resilience_adaptability":         (0.75, 0.80, 0.06, "ai_extracted"),
    }),

    # IC05: Tobias Krüger — Quality Specialist, International
    ("31000000-0000-0000-0000-000000000005", "Tobias Krüger", {
        "strategic_thinking":              (0.68, 0.62, 0.09, "manager"),
        "operational_execution":           (0.75, 0.78, 0.07, "manager"),
        "change_management":               (0.68, 0.60, 0.09, "peer"),
        "crisis_leadership":               (0.68, 0.65, 0.09, "assessment_center"),
        "people_development":              (0.72, 0.72, 0.08, "direct_report"),
        "technical_depth":                 (0.78, 0.82, 0.06, "assessment_center"),
        "cross_functional_collaboration":  (0.72, 0.72, 0.08, "peer"),
        "innovation_orientation":          (0.68, 0.62, 0.09, "ai_extracted"),
        "cultural_sensitivity":            (0.78, 0.85, 0.06, "peer"),            # Munich + Spartanburg experience
        "risk_calibration":                (0.72, 0.72, 0.07, "assessment_center"),
        "stakeholder_management":          (0.68, 0.65, 0.09, "manager"),
        "resilience_adaptability":         (0.72, 0.72, 0.07, "ai_extracted"),
    }),

    # IC06: Sandra Voss — Deputy Supply Chain EMEA
    ("31000000-0000-0000-0000-000000000006", "Sandra Voss", {
        "strategic_thinking":              (0.72, 0.75, 0.07, "assessment_center"),
        "operational_execution":           (0.78, 0.80, 0.06, "manager"),
        "change_management":               (0.72, 0.72, 0.08, "peer"),
        "crisis_leadership":               (0.72, 0.75, 0.07, "assessment_center"),
        "people_development":              (0.72, 0.72, 0.08, "direct_report"),
        "technical_depth":                 (0.75, 0.78, 0.07, "assessment_center"),
        "cross_functional_collaboration":  (0.75, 0.78, 0.07, "peer"),
        "innovation_orientation":          (0.68, 0.68, 0.08, "ai_extracted"),
        "cultural_sensitivity":            (0.72, 0.75, 0.07, "peer"),
        "risk_calibration":                (0.72, 0.75, 0.07, "assessment_center"),
        "stakeholder_management":          (0.72, 0.75, 0.07, "manager"),
        "resilience_adaptability":         (0.75, 0.78, 0.06, "ai_extracted"),
    }),

    # ========== EXTERNAL CANDIDATES (10) ==========

    # EC01: Dr. Klaus Reimann — Mercedes VP Manufacturing
    ("32000000-0000-0000-0000-000000000001", "Dr. Klaus Reimann", {
        "strategic_thinking":              (0.78, 0.82, 0.07, "assessment_center"),
        "operational_execution":           (0.82, 0.85, 0.06, "assessment_center"),
        "change_management":               (0.75, 0.78, 0.07, "reference_check"),
        "crisis_leadership":               (0.78, 0.80, 0.07, "assessment_center"),
        "people_development":              (0.72, 0.72, 0.08, "reference_check"),
        "technical_depth":                 (0.82, 0.88, 0.05, "assessment_center"),
        "cross_functional_collaboration":  (0.72, 0.72, 0.08, "reference_check"),
        "innovation_orientation":          (0.72, 0.72, 0.08, "assessment_center"),
        "cultural_sensitivity":            (0.70, 0.68, 0.09, "reference_check"),
        "risk_calibration":                (0.75, 0.78, 0.07, "assessment_center"),
        "stakeholder_management":          (0.78, 0.80, 0.07, "reference_check"),
        "resilience_adaptability":         (0.75, 0.78, 0.07, "assessment_center"),
    }),

    # EC02: Sarah Chen — Tesla Gigafactory Berlin
    ("32000000-0000-0000-0000-000000000002", "Sarah Chen", {
        "strategic_thinking":              (0.78, 0.82, 0.07, "assessment_center"),
        "operational_execution":           (0.80, 0.82, 0.06, "assessment_center"),
        "change_management":               (0.82, 0.90, 0.05, "reference_check"),  # Tesla = constant change
        "crisis_leadership":               (0.80, 0.85, 0.06, "assessment_center"),
        "people_development":              (0.65, 0.58, 0.10, "reference_check"),   # Tesla burn-and-churn
        "technical_depth":                 (0.80, 0.85, 0.06, "assessment_center"),  # EV native
        "cross_functional_collaboration":  (0.68, 0.62, 0.09, "reference_check"),   # Tesla = top-down
        "innovation_orientation":          (0.85, 0.92, 0.04, "assessment_center"),  # exceptional
        "cultural_sensitivity":            (0.60, 0.48, 0.12, "reference_check"),    # Tesla culture ≠ BMW culture
        "risk_calibration":                (0.75, 0.80, 0.07, "assessment_center"),
        "stakeholder_management":          (0.65, 0.60, 0.10, "reference_check"),
        "resilience_adaptability":         (0.82, 0.88, 0.05, "assessment_center"),
    }),

    # EC03: Marcus Williams — McKinsey Partner
    ("32000000-0000-0000-0000-000000000003", "Marcus Williams", {
        "strategic_thinking":              (0.85, 0.92, 0.04, "assessment_center"),  # consulting strength
        "operational_execution":           (0.62, 0.48, 0.12, "assessment_center"),  # never run a production line
        "change_management":               (0.78, 0.82, 0.07, "reference_check"),
        "crisis_leadership":               (0.68, 0.62, 0.09, "assessment_center"),  # theoretical
        "people_development":              (0.72, 0.68, 0.08, "reference_check"),
        "technical_depth":                 (0.55, 0.42, 0.13, "assessment_center"),  # critical gap
        "cross_functional_collaboration":  (0.80, 0.85, 0.06, "reference_check"),
        "innovation_orientation":          (0.80, 0.85, 0.06, "assessment_center"),
        "cultural_sensitivity":            (0.72, 0.70, 0.08, "reference_check"),
        "risk_calibration":                (0.68, 0.65, 0.09, "assessment_center"),
        "stakeholder_management":          (0.82, 0.88, 0.05, "reference_check"),   # consulting polish
        "resilience_adaptability":         (0.72, 0.72, 0.08, "assessment_center"),
    }),

    # EC04: Dr. Raj Mehta — CATL Europe VP Battery
    ("32000000-0000-0000-0000-000000000004", "Dr. Raj Mehta", {
        "strategic_thinking":              (0.75, 0.78, 0.07, "assessment_center"),
        "operational_execution":           (0.72, 0.72, 0.08, "assessment_center"),
        "change_management":               (0.68, 0.65, 0.09, "reference_check"),
        "crisis_leadership":               (0.72, 0.72, 0.08, "assessment_center"),
        "people_development":              (0.65, 0.60, 0.10, "reference_check"),
        "technical_depth":                 (0.88, 0.95, 0.03, "assessment_center"),  # world-class battery
        "cross_functional_collaboration":  (0.65, 0.60, 0.10, "reference_check"),
        "innovation_orientation":          (0.82, 0.88, 0.05, "assessment_center"),
        "cultural_sensitivity":            (0.65, 0.58, 0.10, "reference_check"),
        "risk_calibration":                (0.72, 0.72, 0.07, "assessment_center"),
        "stakeholder_management":          (0.65, 0.62, 0.09, "reference_check"),
        "resilience_adaptability":         (0.72, 0.72, 0.08, "assessment_center"),
    }),

    # EC05: Claudia Fischer — VW SVP Production (EV transformation proven)
    ("32000000-0000-0000-0000-000000000005", "Claudia Fischer", {
        "strategic_thinking":              (0.78, 0.82, 0.06, "assessment_center"),
        "operational_execution":           (0.82, 0.88, 0.05, "assessment_center"),
        "change_management":               (0.80, 0.88, 0.05, "reference_check"),  # Zwickau transformation
        "crisis_leadership":               (0.78, 0.80, 0.06, "assessment_center"),
        "people_development":              (0.75, 0.78, 0.07, "reference_check"),
        "technical_depth":                 (0.80, 0.85, 0.06, "assessment_center"),
        "cross_functional_collaboration":  (0.75, 0.78, 0.07, "reference_check"),
        "innovation_orientation":          (0.75, 0.78, 0.07, "assessment_center"),
        "cultural_sensitivity":            (0.72, 0.70, 0.08, "reference_check"),
        "risk_calibration":                (0.78, 0.80, 0.06, "assessment_center"),
        "stakeholder_management":          (0.78, 0.82, 0.06, "reference_check"),
        "resilience_adaptability":         (0.78, 0.82, 0.06, "assessment_center"),
    }),

    # EC06: David Park — Amazon Robotics (THE UNICORN — great on paper, bad team fit)
    ("32000000-0000-0000-0000-000000000006", "David Park", {
        "strategic_thinking":              (0.82, 0.88, 0.05, "assessment_center"),
        "operational_execution":           (0.85, 0.90, 0.04, "assessment_center"),  # Amazon execution culture
        "change_management":               (0.78, 0.82, 0.06, "reference_check"),
        "crisis_leadership":               (0.80, 0.85, 0.06, "assessment_center"),
        "people_development":              (0.58, 0.42, 0.13, "reference_check"),    # Amazon burn rate
        "technical_depth":                 (0.82, 0.88, 0.05, "assessment_center"),
        "cross_functional_collaboration":  (0.55, 0.38, 0.14, "reference_check"),    # CRITICAL: individualistic
        "innovation_orientation":          (0.82, 0.88, 0.05, "assessment_center"),
        "cultural_sensitivity":            (0.50, 0.32, 0.15, "reference_check"),    # CRITICAL: no patience for consensus
        "risk_calibration":                (0.78, 0.82, 0.07, "assessment_center"),
        "stakeholder_management":          (0.62, 0.52, 0.11, "reference_check"),
        "resilience_adaptability":         (0.80, 0.85, 0.06, "assessment_center"),
    }),

    # EC07: Dr. Elena Voronova — Bosch (THE HIDDEN GEM)
    ("32000000-0000-0000-0000-000000000007", "Dr. Elena Voronova", {
        "strategic_thinking":              (0.72, 0.82, 0.07, "assessment_center"),  # underrated
        "operational_execution":           (0.75, 0.78, 0.07, "assessment_center"),
        "change_management":               (0.78, 0.92, 0.04, "reference_check"),   # EXCEPTIONAL — Bosch plant transformation
        "crisis_leadership":               (0.75, 0.80, 0.07, "assessment_center"),
        "people_development":              (0.78, 0.85, 0.06, "reference_check"),    # known talent developer
        "technical_depth":                 (0.72, 0.72, 0.08, "assessment_center"),  # Tier-1, not OEM — apparent weakness
        "cross_functional_collaboration":  (0.80, 0.90, 0.05, "reference_check"),   # bridge builder
        "innovation_orientation":          (0.78, 0.85, 0.06, "assessment_center"),
        "cultural_sensitivity":            (0.82, 0.90, 0.05, "reference_check"),   # German works council expert
        "risk_calibration":                (0.75, 0.80, 0.07, "assessment_center"),
        "stakeholder_management":          (0.78, 0.85, 0.06, "reference_check"),
        "resilience_adaptability":         (0.78, 0.85, 0.06, "assessment_center"),
    }),

    # EC08: Pierre Dubois — Stellantis VP Supply Chain
    ("32000000-0000-0000-0000-000000000008", "Pierre Dubois", {
        "strategic_thinking":              (0.75, 0.78, 0.07, "assessment_center"),
        "operational_execution":           (0.78, 0.80, 0.06, "assessment_center"),
        "change_management":               (0.72, 0.72, 0.08, "reference_check"),
        "crisis_leadership":               (0.78, 0.82, 0.06, "assessment_center"),
        "people_development":              (0.72, 0.72, 0.08, "reference_check"),
        "technical_depth":                 (0.75, 0.78, 0.07, "assessment_center"),
        "cross_functional_collaboration":  (0.75, 0.78, 0.07, "reference_check"),
        "innovation_orientation":          (0.68, 0.65, 0.09, "assessment_center"),
        "cultural_sensitivity":            (0.78, 0.82, 0.06, "reference_check"),  # French + European multi-country
        "risk_calibration":                (0.75, 0.78, 0.07, "assessment_center"),
        "stakeholder_management":          (0.78, 0.82, 0.06, "reference_check"),
        "resilience_adaptability":         (0.72, 0.75, 0.07, "assessment_center"),
    }),

    # EC09: Dr. Yuki Tanaka — Siemens AI Manufacturing
    ("32000000-0000-0000-0000-000000000009", "Dr. Yuki Tanaka", {
        "strategic_thinking":              (0.80, 0.85, 0.06, "assessment_center"),
        "operational_execution":           (0.68, 0.65, 0.09, "assessment_center"),
        "change_management":               (0.78, 0.82, 0.06, "reference_check"),
        "crisis_leadership":               (0.65, 0.62, 0.09, "assessment_center"),
        "people_development":              (0.72, 0.72, 0.08, "reference_check"),
        "technical_depth":                 (0.85, 0.92, 0.04, "assessment_center"),  # AI/digital manufacturing expert
        "cross_functional_collaboration":  (0.75, 0.78, 0.07, "reference_check"),
        "innovation_orientation":          (0.85, 0.92, 0.04, "assessment_center"),  # innovation leader
        "cultural_sensitivity":            (0.75, 0.78, 0.07, "reference_check"),
        "risk_calibration":                (0.72, 0.72, 0.07, "assessment_center"),
        "stakeholder_management":          (0.68, 0.68, 0.08, "reference_check"),
        "resilience_adaptability":         (0.72, 0.75, 0.07, "assessment_center"),
    }),

    # EC10: Robert Schwarz — BMW Motorrad VP Operations (internal-adjacent)
    ("32000000-0000-0000-0000-000000000010", "Robert Schwarz", {
        "strategic_thinking":              (0.72, 0.72, 0.08, "assessment_center"),
        "operational_execution":           (0.80, 0.82, 0.06, "assessment_center"),
        "change_management":               (0.68, 0.65, 0.09, "reference_check"),
        "crisis_leadership":               (0.72, 0.72, 0.08, "assessment_center"),
        "people_development":              (0.78, 0.82, 0.06, "reference_check"),
        "technical_depth":                 (0.72, 0.72, 0.08, "assessment_center"),
        "cross_functional_collaboration":  (0.72, 0.72, 0.08, "reference_check"),
        "innovation_orientation":          (0.65, 0.60, 0.10, "assessment_center"),
        "cultural_sensitivity":            (0.82, 0.88, 0.05, "reference_check"),   # knows BMW culture deeply
        "risk_calibration":                (0.72, 0.72, 0.08, "assessment_center"),
        "stakeholder_management":          (0.75, 0.78, 0.07, "reference_check"),
        "resilience_adaptability":         (0.72, 0.75, 0.07, "assessment_center"),
    }),
]


def generate_sql():
    lines = []
    lines.append("-- ============================================================================")
    lines.append("-- NEXUS Seed Data: 04 — Leadership Genome Scores")
    lines.append("-- 12 dimensions × 24 leaders/candidates = 288 rows")
    lines.append("-- ============================================================================\n")
    lines.append("INSERT INTO leader_capability_scores (id, leader_id, dimension, raw_score, corrected_score, confidence_low, confidence_high, evidence_sources, bias_corrections_applied, assessed_at, assessor_type) VALUES\n")

    values = []
    counter = 0
    for leader_id, name, scores in PROFILES:
        lines.append(f"-- {name}")
        for dim in DIMENSIONS:
            raw, corrected, ci_offset, assessor = scores[dim]
            conf_low = round(max(0.0, corrected - ci_offset), 2)
            conf_high = round(min(1.0, corrected + ci_offset), 2)

            # Compute bias correction
            correction = round(corrected - raw, 2)
            bias_json = {}
            if abs(correction) > 0.05:
                if correction > 0:
                    bias_json["central_tendency_correction"] = round(correction, 2)
                else:
                    bias_json["halo_effect_correction"] = round(correction, 2)

            evidence = []
            if assessor == "assessment_center":
                evidence = ["assessment_center_2025", "structured_interview"]
            elif assessor == "manager":
                evidence = ["annual_review_2025", "goal_tracking"]
            elif assessor == "peer":
                evidence = ["360_peer_feedback_2025H1", "cross_team_survey"]
            elif assessor == "direct_report":
                evidence = ["360_direct_report_2025H1", "team_engagement_survey"]
            elif assessor == "ai_extracted":
                evidence = ["360_text_analysis", "project_outcome_nlp", "meeting_pattern_analysis"]
            elif assessor == "reference_check":
                evidence = ["reference_check_2026", "background_verification"]

            counter += 1
            uid = f"60000000-0000-0000-0000-{counter:012d}"

            val = (
                f"('{uid}', '{leader_id}', '{dim}', "
                f"{raw}, {corrected}, {conf_low}, {conf_high}, "
                f"ARRAY{evidence}, "
                f"'{json.dumps(bias_json)}'::jsonb, "
                f"'2026-02-15', '{assessor}')"
            )
            values.append(val)

    lines.append(",\n".join(values) + ";\n")
    return "\n".join(lines)


if __name__ == "__main__":
    sql = generate_sql()
    with open("/home/claude/nexus-seed-data/04_leadership_genomes.sql", "w") as f:
        f.write(sql)
    print(f"Generated {len(PROFILES) * len(DIMENSIONS)} genome score rows.")
