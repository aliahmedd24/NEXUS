-- ============================================================================
-- NEXUS Seed Data: 09 — Historical Decisions & Outcomes
-- 10 past leadership appointments with known results
-- 3 clear successes, 3 mis-hires, 4 suboptimal
-- These feed the Decision Replay Agent and Pattern Intelligence Agent
-- ============================================================================

-- We'll reuse some leader IDs for "historical" context and create a few
-- placeholder IDs for historical-only candidates (not in current pipeline)

-- Historical-only leader placeholders (past candidates who weren't selected or have since left)
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('33000000-0000-0000-0000-000000000001', 'Dr. Martin Scholz',     NULL, 'internal_current', 26, 20, 'phd',     ARRAY['automotive','manufacturing'], ARRAY['Munich'], 0.05),
('33000000-0000-0000-0000-000000000002', 'Christina Bauer',       NULL, 'internal_current', 19, 14, 'masters', ARRAY['automotive','quality_management'], ARRAY['Munich'], 0.10),
('33000000-0000-0000-0000-000000000003', 'Henrik Larsson',        NULL, 'internal_current', 22, 0,  'mba',     ARRAY['automotive','consulting'], ARRAY['Stockholm','Munich'], NULL),
('33000000-0000-0000-0000-000000000004', 'Dr. Priya Sharma',      NULL, 'internal_current', 17, 8,  'phd',     ARRAY['tech','battery_technology'], ARRAY['Munich'], 0.30),
('33000000-0000-0000-0000-000000000005', 'Wolfgang Huber',        NULL, 'internal_current', 30, 28, 'masters', ARRAY['automotive'], ARRAY['Munich','Dingolfing'], 0.05),
('33000000-0000-0000-0000-000000000006', 'Simone Roth',           NULL, 'internal_current', 15, 10, 'masters', ARRAY['automotive','hr_consulting'], ARRAY['Munich'], 0.12),
('33000000-0000-0000-0000-000000000007', 'Takeshi Nakamura',      NULL, 'internal_current', 20, 0,  'masters', ARRAY['automotive','supply_chain'], ARRAY['Munich','Tokyo'], NULL),
('33000000-0000-0000-0000-000000000008', 'Dr. Andreas Fink',      NULL, 'internal_current', 18, 12, 'phd',     ARRAY['automotive','manufacturing','ev_systems'], ARRAY['Munich'], 0.15);


-- ============================================================================
-- HISTORICAL DECISIONS
-- ============================================================================

INSERT INTO historical_decisions (id, role_id, decision_date, scenario_at_decision, selected_candidate_id, runner_up_candidate_id, decision_criteria_used, decision_reasoning, decision_maker_id, time_to_fill_days, cost_of_hire_eur) VALUES

-- HD01: SUCCESS — Dr. Katharina Weiss appointed Plant Director Munich (2020)
-- Runner-up was more senior but less capable. System would have agreed with this choice.
('80000000-0000-0000-0000-000000000001',
 '20000000-0000-0000-0000-000000000001', '2020-03-15', 'COVID crisis + EV transition beginning',
 '30000000-0000-0000-0000-000000000001', '33000000-0000-0000-0000-000000000005',
 '{"strategic_thinking": 0.20, "operational_execution": 0.25, "crisis_leadership": 0.20, "people_development": 0.15, "change_management": 0.10, "cultural_sensitivity": 0.10}',
 'Selected Weiss over Huber despite Huber having 8 more years seniority. Weiss demonstrated superior crisis leadership during COVID interview simulations and stronger change management credentials for upcoming EV transition. Board took a calculated risk on relative youth.',
 NULL, 95, 15000),

-- HD02: MIS-HIRE — Stefan Krause appointed Head of Digital/iFACTORY (2023)
-- Runner-up was Dr. Priya Sharma (tech background, would have been better)
('80000000-0000-0000-0000-000000000002',
 '20000000-0000-0000-0000-000000000006', '2023-06-01', 'iFACTORY initiative launch',
 '30000000-0000-0000-0000-000000000005', '33000000-0000-0000-0000-000000000004',
 '{"operational_execution": 0.25, "technical_depth": 0.25, "years_at_bmw": 0.20, "cultural_sensitivity": 0.15, "people_development": 0.15}',
 'Selected Krause over Sharma because of 14 years BMW tenure and reliable IT operations track record. Sharma had stronger technical vision but only 3 years at BMW. Decision prioritized cultural fit and operational reliability over transformation capability. This was the safe choice.',
 NULL, 45, 0),

-- HD03: SUCCESS — Markus Brenner appointed VP Quality Munich (2022)
('80000000-0000-0000-0000-000000000003',
 '20000000-0000-0000-0000-000000000003', '2022-01-15', 'Post-COVID quality recovery',
 '30000000-0000-0000-0000-000000000003', '33000000-0000-0000-0000-000000000002',
 '{"technical_depth": 0.25, "operational_execution": 0.20, "cross_functional_collaboration": 0.15, "cultural_sensitivity": 0.15, "crisis_leadership": 0.15, "people_development": 0.10}',
 'Brenner selected for deep quality management expertise and proven works council collaboration. Bauer was equally qualified technically but had weaker cross-functional network. Correct decision for steady-state quality leadership.',
 NULL, 72, 0),

-- HD04: MIS-HIRE — Jürgen Mayer appointed Head of Production Logistics (2024)
-- Runner-up was an external candidate who would have been significantly better
('80000000-0000-0000-0000-000000000004',
 '20000000-0000-0000-0000-000000000008', '2024-02-01', 'Predecessor sudden departure',
 '30000000-0000-0000-0000-000000000007', '33000000-0000-0000-0000-000000000007',
 '{"years_at_bmw": 0.25, "operational_execution": 0.20, "technical_depth": 0.20, "cultural_sensitivity": 0.15, "people_development": 0.10, "strategic_thinking": 0.10}',
 'Emergency appointment after predecessor resigned with 2 weeks notice. Mayer was the most senior internal candidate available immediately. Nakamura (external, ex-Toyota logistics VP) was in final interview stage but would have required 90-day notice period. Urgency drove the decision over quality.',
 NULL, 14, 0),

-- HD05: SUBOPTIMAL — James Carter appointed VP Production Spartanburg (2021)
-- Good choice at the time, but scenario has shifted. Not a mis-hire, but wrong for the future.
('80000000-0000-0000-0000-000000000005',
 '20000000-0000-0000-0000-000000000010', '2021-09-01', 'Steady-state ICE growth',
 '30000000-0000-0000-0000-000000000008', '33000000-0000-0000-0000-000000000003',
 '{"operational_execution": 0.30, "technical_depth": 0.20, "people_development": 0.15, "cultural_sensitivity": 0.15, "stakeholder_management": 0.10, "strategic_thinking": 0.10}',
 'Carter selected for exceptional ICE manufacturing expertise and strong local community relationships. Larsson (ex-Volvo, McKinsey) had stronger strategic and transformation profile but was seen as a culture risk for Spartanburg. At the time, EV transition for Spartanburg was planned for 2030, not 2028.',
 NULL, 82, 85000),

-- HD06: MIS-HIRE — Previous Head of EV Battery Systems (departed after 8 months)
('80000000-0000-0000-0000-000000000006',
 '20000000-0000-0000-0000-000000000005', '2025-01-15', 'Neue Klasse development phase',
 '33000000-0000-0000-0000-000000000003', '31000000-0000-0000-0000-000000000004',
 '{"strategic_thinking": 0.20, "technical_depth": 0.20, "innovation_orientation": 0.15, "stakeholder_management": 0.15, "change_management": 0.15, "cross_functional_collaboration": 0.15}',
 'Selected Larsson (ex-McKinsey, ex-Volvo battery strategy) over Dr. Patel (internal battery cell engineering). Larsson had impressive strategic credentials but lacked hands-on battery manufacturing knowledge. Departed after 8 months citing misalignment on execution pace. Role now vacant.',
 NULL, 110, 220000),

-- HD07: SUCCESS — Dr. Lena Hoffmann appointed Head of Supply Chain EMEA (2022)
('80000000-0000-0000-0000-000000000007',
 '20000000-0000-0000-0000-000000000004', '2022-04-01', 'Post-chip-shortage recovery',
 '30000000-0000-0000-0000-000000000004', '33000000-0000-0000-0000-000000000007',
 '{"crisis_leadership": 0.25, "strategic_thinking": 0.20, "stakeholder_management": 0.15, "risk_calibration": 0.15, "cross_functional_collaboration": 0.10, "operational_execution": 0.15}',
 'Hoffmann selected during acute chip shortage crisis. Her PhD research on supply chain risk modeling and McKinsey consulting background gave her unique combination of theoretical framework and practical urgency. Nakamura (Toyota) was strong operationally but lacked crisis strategic vision.',
 NULL, 68, 0),

-- HD08: SUBOPTIMAL — Anna Bergmann appointed HR Director Plant Munich (2021)
-- Good HR leader but missed opportunity to bring in someone with stronger transformation credentials
('80000000-0000-0000-0000-000000000008',
 '20000000-0000-0000-0000-000000000007', '2021-06-01', 'Steady-state operations',
 '30000000-0000-0000-0000-000000000006', '33000000-0000-0000-0000-000000000006',
 '{"cultural_sensitivity": 0.25, "people_development": 0.20, "stakeholder_management": 0.20, "operational_execution": 0.15, "cross_functional_collaboration": 0.10, "change_management": 0.10}',
 'Bergmann selected for exceptional works council relationships and institutional knowledge. Roth (external, Siemens HR transformation lead) had stronger change management and digital HR skills but was seen as risky for works council relationships. Correct for 2021, possibly suboptimal for 2026 transformation needs.',
 NULL, 55, 0),

-- HD09: SUBOPTIMAL — Thomas Richter retained as VP Production Munich (2022 renewal)
-- Should have started transition planning earlier
('80000000-0000-0000-0000-000000000009',
 '20000000-0000-0000-0000-000000000002', '2022-12-01', 'EV transition planning phase',
 '30000000-0000-0000-0000-000000000002', '31000000-0000-0000-0000-000000000001',
 '{"operational_execution": 0.30, "technical_depth": 0.25, "years_at_bmw": 0.20, "crisis_leadership": 0.10, "people_development": 0.10, "change_management": 0.05}',
 'Extended Richter''s appointment for 3 more years rather than beginning succession transition. Hartmann was ready as deputy but board preferred stability. Change management weighted at only 5% despite EV transition accelerating. In hindsight, succession should have started here.',
 NULL, 0, 0),

-- HD10: SUBOPTIMAL — Previous Head of Production Logistics (resigned, replaced by Mayer)
-- The original appointee was good but left due to compensation dispute
('80000000-0000-0000-0000-000000000010',
 '20000000-0000-0000-0000-000000000008', '2021-03-01', 'Steady-state operations',
 '33000000-0000-0000-0000-000000000001', NULL,
 '{"operational_execution": 0.25, "technical_depth": 0.20, "strategic_thinking": 0.15, "cross_functional_collaboration": 0.15, "people_development": 0.10, "cultural_sensitivity": 0.15}',
 'Dr. Scholz appointed as Head of Production Logistics. Strong initial performance. Departed in Jan 2024 after compensation counter-offer from Porsche — BMW HR failed to match despite retention warning from his manager. Created the emergency vacancy that led to Mayer mis-hire.',
 NULL, 78, 0);


-- ============================================================================
-- DECISION OUTCOMES
-- Multiple time horizons per decision (6, 12, 18, 24 months)
-- ============================================================================

INSERT INTO decision_outcomes (id, decision_id, months_elapsed, performance_rating, goal_completion_pct, team_engagement_delta, team_attrition_delta, project_delivery_score, still_in_role, departure_reason) VALUES

-- HD01 outcomes: Dr. Weiss — SUCCESS trajectory
('81000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', 6,  7.8, 88.0,  0.2,  -0.01, 0.85, TRUE,  NULL),
('81000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000001', 12, 8.0, 92.0,  0.4,  -0.02, 0.90, TRUE,  NULL),
('81000000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000001', 24, 8.2, 94.0,  0.5,  -0.02, 0.92, TRUE,  NULL),

-- HD02 outcomes: Krause — MIS-HIRE trajectory (declining)
('81000000-0000-0000-0000-000000000004', '80000000-0000-0000-0000-000000000002', 6,  7.5, 82.0,  0.0,  0.02,  0.72, TRUE,  NULL),
('81000000-0000-0000-0000-000000000005', '80000000-0000-0000-0000-000000000002', 12, 7.2, 78.0, -0.3,  0.06,  0.60, TRUE,  NULL),
('81000000-0000-0000-0000-000000000006', '80000000-0000-0000-0000-000000000002', 24, 6.8, 72.0, -0.6,  0.10,  0.45, TRUE,  NULL),

-- HD03 outcomes: Brenner — SUCCESS (steady)
('81000000-0000-0000-0000-000000000007', '80000000-0000-0000-0000-000000000003', 6,  7.5, 85.0,  0.1,  0.00,  0.82, TRUE,  NULL),
('81000000-0000-0000-0000-000000000008', '80000000-0000-0000-0000-000000000003', 12, 7.8, 89.0,  0.3,  -0.01, 0.88, TRUE,  NULL),
('81000000-0000-0000-0000-000000000009', '80000000-0000-0000-0000-000000000003', 24, 7.8, 89.0,  0.3,  -0.01, 0.90, TRUE,  NULL),

-- HD04 outcomes: Mayer — MIS-HIRE trajectory (rapid decline)
('81000000-0000-0000-0000-000000000010', '80000000-0000-0000-0000-000000000004', 6,  7.0, 74.0, -0.2,  0.05,  0.62, TRUE,  NULL),
('81000000-0000-0000-0000-000000000011', '80000000-0000-0000-0000-000000000004', 12, 6.5, 68.0, -0.5,  0.12,  0.48, TRUE,  NULL),

-- HD05 outcomes: Carter — SUBOPTIMAL (good now, declining future fit)
('81000000-0000-0000-0000-000000000012', '80000000-0000-0000-0000-000000000005', 6,  7.8, 90.0,  0.2,  -0.01, 0.88, TRUE,  NULL),
('81000000-0000-0000-0000-000000000013', '80000000-0000-0000-0000-000000000005', 12, 7.9, 91.0,  0.3,  -0.01, 0.90, TRUE,  NULL),
('81000000-0000-0000-0000-000000000014', '80000000-0000-0000-0000-000000000005', 24, 7.7, 87.0,  0.1,   0.02, 0.82, TRUE,  NULL),

-- HD06 outcomes: Larsson as Head of EV Battery Systems — MIS-HIRE (departed)
('81000000-0000-0000-0000-000000000015', '80000000-0000-0000-0000-000000000006', 6,  6.5, 62.0, -0.4,  0.08,  0.42, TRUE,  NULL),
('81000000-0000-0000-0000-000000000016', '80000000-0000-0000-0000-000000000006', 12, NULL, NULL, -0.6,  0.15,  0.30, FALSE, 'voluntary'),

-- HD07 outcomes: Dr. Hoffmann — SUCCESS
('81000000-0000-0000-0000-000000000017', '80000000-0000-0000-0000-000000000007', 6,  7.8, 88.0,  0.1,  0.00,  0.85, TRUE,  NULL),
('81000000-0000-0000-0000-000000000018', '80000000-0000-0000-0000-000000000007', 12, 8.1, 93.0,  0.3,  -0.01, 0.92, TRUE,  NULL),
('81000000-0000-0000-0000-000000000019', '80000000-0000-0000-0000-000000000007', 24, 8.3, 96.0,  0.4,  -0.01, 0.95, TRUE,  NULL),

-- HD08 outcomes: Bergmann — SUBOPTIMAL (solid but not transformative)
('81000000-0000-0000-0000-000000000020', '80000000-0000-0000-0000-000000000008', 6,  7.5, 85.0,  0.2,  0.00,  0.80, TRUE,  NULL),
('81000000-0000-0000-0000-000000000021', '80000000-0000-0000-0000-000000000008', 12, 7.8, 88.0,  0.3,  -0.01, 0.85, TRUE,  NULL),
('81000000-0000-0000-0000-000000000022', '80000000-0000-0000-0000-000000000008', 24, 7.9, 90.0,  0.3,  -0.01, 0.85, TRUE,  NULL),

-- HD09 outcomes: Richter renewal — SUBOPTIMAL (delayed succession)
('81000000-0000-0000-0000-000000000023', '80000000-0000-0000-0000-000000000009', 12, 7.8, 88.0,  -0.1,  0.02, 0.82, TRUE,  NULL),
('81000000-0000-0000-0000-000000000024', '80000000-0000-0000-0000-000000000009', 24, 7.5, 82.0,  -0.3,  0.05, 0.72, TRUE,  NULL),

-- HD10 outcomes: Dr. Scholz — good then left (SUBOPTIMAL because retention failed)
('81000000-0000-0000-0000-000000000025', '80000000-0000-0000-0000-000000000010', 6,  7.8, 90.0,  0.2,  0.00,  0.88, TRUE,  NULL),
('81000000-0000-0000-0000-000000000026', '80000000-0000-0000-0000-000000000010', 12, 8.0, 92.0,  0.3,  -0.01, 0.90, TRUE,  NULL),
('81000000-0000-0000-0000-000000000027', '80000000-0000-0000-0000-000000000010', 24, 8.1, 93.0,  0.4,  -0.01, 0.92, TRUE,  NULL),
('81000000-0000-0000-0000-000000000028', '80000000-0000-0000-0000-000000000010', 36, NULL, NULL, -0.8,  0.18,  NULL, FALSE, 'poached');


-- ============================================================================
-- CALIBRATION COEFFICIENTS (Learned from historical patterns)
-- These represent the biases the Pattern Intelligence Agent has identified
-- ============================================================================

INSERT INTO calibration_coefficients (id, dimension, historical_overweight, correction_factor, evidence_count, confidence) VALUES

('82000000-0000-0000-0000-000000000001', 'operational_execution', 0.35, 0.74, 8, 0.82),
('82000000-0000-0000-0000-000000000002', 'technical_depth',       0.22, 0.82, 8, 0.75),
('82000000-0000-0000-0000-000000000003', 'change_management',    -0.28, 1.39, 8, 0.88),
('82000000-0000-0000-0000-000000000004', 'innovation_orientation',-0.25, 1.33, 7, 0.72),
('82000000-0000-0000-0000-000000000005', 'cross_functional_collaboration', -0.18, 1.22, 6, 0.65),
('82000000-0000-0000-0000-000000000006', 'cultural_sensitivity',  0.15, 0.87, 7, 0.60),
('82000000-0000-0000-0000-000000000007', 'strategic_thinking',   -0.08, 1.09, 8, 0.55),
('82000000-0000-0000-0000-000000000008', 'crisis_leadership',    -0.12, 1.14, 5, 0.50),
('82000000-0000-0000-0000-000000000009', 'people_development',   -0.15, 1.18, 7, 0.68),
('82000000-0000-0000-0000-000000000010', 'risk_calibration',     -0.05, 1.05, 6, 0.45),
('82000000-0000-0000-0000-000000000011', 'stakeholder_management', 0.08, 0.93, 6, 0.48),
('82000000-0000-0000-0000-000000000012', 'resilience_adaptability', -0.10, 1.11, 5, 0.42);
