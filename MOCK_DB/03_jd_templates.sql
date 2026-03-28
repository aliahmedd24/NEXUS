-- ============================================================================
-- NEXUS Seed Data: 03 — JD Templates
-- Base job descriptions with competency weightings per §4.2
-- ============================================================================

INSERT INTO jd_templates (id, role_type, base_description, competency_weightings, min_experience_years, typical_compensation_range, typical_time_to_fill_days, version) VALUES

('50000000-0000-0000-0000-000000000001', 'plant_director',
 'The Plant Director leads all operations for a BMW Group production facility, including production, quality, logistics, HR, and finance. Responsible for annual output targets, workforce of 5,000–18,000, and capital investment programs. Must navigate German works council requirements and BMW Group manufacturing standards. Accountable to the Board of Management for plant-level P&L.',
 '{"strategic_thinking": 0.15, "operational_execution": 0.20, "change_management": 0.12, "crisis_leadership": 0.08, "people_development": 0.10, "technical_depth": 0.08, "cross_functional_collaboration": 0.08, "innovation_orientation": 0.05, "cultural_sensitivity": 0.05, "risk_calibration": 0.03, "stakeholder_management": 0.04, "resilience_adaptability": 0.02}',
 20, '{"min_eur": 250000, "max_eur": 400000}', 105, 1),

('50000000-0000-0000-0000-000000000002', 'vp_production',
 'VP Production manages all manufacturing operations within a BMW plant, including body shop, paint shop, assembly, and engine/drivetrain production. Directly responsible for daily output volumes, OEE, and defect rates. Manages 2,000–5,000 production associates. Reports to Plant Director.',
 '{"strategic_thinking": 0.05, "operational_execution": 0.25, "change_management": 0.10, "crisis_leadership": 0.10, "people_development": 0.08, "technical_depth": 0.15, "cross_functional_collaboration": 0.07, "innovation_orientation": 0.05, "cultural_sensitivity": 0.03, "risk_calibration": 0.05, "stakeholder_management": 0.04, "resilience_adaptability": 0.03}',
 15, '{"min_eur": 200000, "max_eur": 320000}', 88, 1),

('50000000-0000-0000-0000-000000000003', 'vp_quality',
 'VP Quality owns the quality management system for a BMW production facility. Responsible for incoming quality, in-process quality, final audit, and field quality feedback loops. Manages 300–800 quality professionals. Coordinates with Quality Management Central on standards and audit programs. Must maintain BMW premium quality reputation.',
 '{"strategic_thinking": 0.08, "operational_execution": 0.18, "change_management": 0.05, "crisis_leadership": 0.10, "people_development": 0.08, "technical_depth": 0.18, "cross_functional_collaboration": 0.10, "innovation_orientation": 0.05, "cultural_sensitivity": 0.03, "risk_calibration": 0.08, "stakeholder_management": 0.05, "resilience_adaptability": 0.02}',
 12, '{"min_eur": 180000, "max_eur": 300000}', 80, 1),

('50000000-0000-0000-0000-000000000004', 'head_supply_chain',
 'Head of Supply Chain EMEA manages BMW Group''s European supplier network supporting 36M+ parts/day across all European plants. Responsible for supplier selection, contract negotiation (€90B annual purchasing volume), logistics network design, and supply risk management. Must manage relationships with 1,800+ Tier-1 suppliers.',
 '{"strategic_thinking": 0.15, "operational_execution": 0.12, "change_management": 0.08, "crisis_leadership": 0.12, "people_development": 0.05, "technical_depth": 0.08, "cross_functional_collaboration": 0.10, "innovation_orientation": 0.05, "cultural_sensitivity": 0.08, "risk_calibration": 0.08, "stakeholder_management": 0.07, "resilience_adaptability": 0.02}',
 15, '{"min_eur": 160000, "max_eur": 260000}', 75, 1),

('50000000-0000-0000-0000-000000000005', 'head_ev_systems',
 'Head of EV Battery Systems leads BMW Group''s battery cell integration, pack design, and battery lifecycle management for the Neue Klasse platform and beyond. Responsible for battery supply partnerships (CATL, Samsung SDI, Northvolt), cell chemistry roadmap, and production readiness at Debrecen and future battery plants. This is a newly created role reflecting BMW''s EV transformation.',
 '{"strategic_thinking": 0.12, "operational_execution": 0.10, "change_management": 0.15, "crisis_leadership": 0.05, "people_development": 0.08, "technical_depth": 0.20, "cross_functional_collaboration": 0.10, "innovation_orientation": 0.10, "cultural_sensitivity": 0.03, "risk_calibration": 0.03, "stakeholder_management": 0.02, "resilience_adaptability": 0.02}',
 12, '{"min_eur": 200000, "max_eur": 350000}', 105, 1),

('50000000-0000-0000-0000-000000000006', 'head_digital_it',
 'Head of Digital / iFACTORY leads the digital transformation of BMW Group manufacturing. Responsible for the iFACTORY concept (LEAN, GREEN, DIGITAL), including digital twin deployment, IoT sensor networks, AI-powered quality inspection, and predictive maintenance across all plants. Coordinates with BMW Group IT on enterprise architecture.',
 '{"strategic_thinking": 0.15, "operational_execution": 0.08, "change_management": 0.15, "crisis_leadership": 0.03, "people_development": 0.08, "technical_depth": 0.18, "cross_functional_collaboration": 0.12, "innovation_orientation": 0.12, "cultural_sensitivity": 0.02, "risk_calibration": 0.03, "stakeholder_management": 0.02, "resilience_adaptability": 0.02}',
 12, '{"min_eur": 180000, "max_eur": 300000}', 95, 1),

('50000000-0000-0000-0000-000000000007', 'hr_director',
 'HR Director — Plant Munich is the senior HR business partner for BMW Group Plant Munich (7,800 employees). Manages workforce planning, labor relations (works council), compensation, talent development, and HR shared services. Must maintain productive relationship with Betriebsrat (works council) per German co-determination law (BetrVG).',
 '{"strategic_thinking": 0.10, "operational_execution": 0.10, "change_management": 0.10, "crisis_leadership": 0.05, "people_development": 0.18, "technical_depth": 0.05, "cross_functional_collaboration": 0.10, "innovation_orientation": 0.03, "cultural_sensitivity": 0.15, "risk_calibration": 0.05, "stakeholder_management": 0.07, "resilience_adaptability": 0.02}',
 10, '{"min_eur": 140000, "max_eur": 220000}', 60, 1),

('50000000-0000-0000-0000-000000000008', 'head_logistics',
 'Head of Production Logistics manages inbound logistics, line-side delivery, sequencing, and finished vehicle logistics for a BMW production plant. Responsible for JIT/JIS delivery to production lines, warehouse management, and outbound vehicle distribution. Coordinates with Supply Chain EMEA and plant production leadership.',
 '{"strategic_thinking": 0.08, "operational_execution": 0.22, "change_management": 0.08, "crisis_leadership": 0.08, "people_development": 0.07, "technical_depth": 0.12, "cross_functional_collaboration": 0.10, "innovation_orientation": 0.05, "cultural_sensitivity": 0.03, "risk_calibration": 0.08, "stakeholder_management": 0.05, "resilience_adaptability": 0.04}',
 10, '{"min_eur": 150000, "max_eur": 240000}', 70, 1);
