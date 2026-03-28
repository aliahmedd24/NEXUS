-- ============================================================================
-- NEXUS Seed Data: 11 — Counterfactual Results & Compatibility Assessments
-- ============================================================================

-- ============================================================================
-- COUNTERFACTUAL RESULTS
-- "What if we'd chosen differently?" for key historical decisions
-- ============================================================================

INSERT INTO counterfactual_results (id, decision_id, alternative_candidate_id, simulated_outcome, divergence_score, divergence_category) VALUES

-- HD02 counterfactual: What if Dr. Priya Sharma had been chosen for Head of Digital instead of Krause?
('83000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000002',
 '33000000-0000-0000-0000-000000000004',
 '{"months_elapsed": 24, "performance_rating": 8.2, "goal_completion_pct": 91.0, "team_engagement_delta": 0.5, "team_attrition_delta": -0.04, "project_delivery_score": 0.88, "still_in_role": true}',
 0.38, 'critical_miss'),

-- HD04 counterfactual: What if Nakamura had been chosen for Head of Logistics instead of Mayer?
('83000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000004',
 '33000000-0000-0000-0000-000000000007',
 '{"months_elapsed": 12, "performance_rating": 8.0, "goal_completion_pct": 90.0, "team_engagement_delta": 0.3, "team_attrition_delta": -0.02, "project_delivery_score": 0.88, "still_in_role": true}',
 0.35, 'critical_miss'),

-- HD05 counterfactual: What if Larsson had been chosen for Spartanburg instead of Carter?
-- Under CURRENT scenario (EV transition approaching), Larsson would score better
('83000000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000005',
 '33000000-0000-0000-0000-000000000003',
 '{"months_elapsed": 24, "performance_rating": 7.5, "goal_completion_pct": 82.0, "team_engagement_delta": -0.1, "team_attrition_delta": 0.03, "project_delivery_score": 0.78, "still_in_role": true, "note": "Better EV transition readiness but weaker day-to-day operations"}',
 0.08, 'suboptimal'),

-- HD06 counterfactual: What if Dr. Patel had been chosen for Head of EV Battery instead of Larsson?
('83000000-0000-0000-0000-000000000004', '80000000-0000-0000-0000-000000000006',
 '31000000-0000-0000-0000-000000000004',
 '{"months_elapsed": 12, "performance_rating": 8.0, "goal_completion_pct": 88.0, "team_engagement_delta": 0.2, "team_attrition_delta": -0.02, "project_delivery_score": 0.85, "still_in_role": true}',
 0.42, 'critical_miss'),

-- HD09 counterfactual: What if Hartmann had replaced Richter in 2022 instead of renewal?
('83000000-0000-0000-0000-000000000005', '80000000-0000-0000-0000-000000000009',
 '31000000-0000-0000-0000-000000000001',
 '{"months_elapsed": 24, "performance_rating": 7.8, "goal_completion_pct": 85.0, "team_engagement_delta": 0.1, "team_attrition_delta": 0.00, "project_delivery_score": 0.80, "still_in_role": true, "note": "Moderate improvement — Hartmann better than aging Richter but not transformational"}',
 0.12, 'suboptimal');


-- ============================================================================
-- COMPATIBILITY ASSESSMENTS
-- Pairwise compatibility for current Munich Plant leadership team
-- + key candidate-to-team assessments for demo
-- ============================================================================

INSERT INTO compatibility_assessments (id, leader_a_id, leader_b_id, relationship_type, synergy_score, friction_dimensions, synergy_dimensions, groupthink_risk) VALUES

-- === Current Munich Plant Leadership Team Compatibility ===

-- Weiss ↔ Richter (Plant Director ↔ VP Production): moderate friction due to digital gap
('84000000-0000-0000-0000-000000000001',
 '30000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000002',
 'hierarchical', 0.35,
 ARRAY['innovation_orientation', 'change_management'],
 ARRAY['operational_execution', 'crisis_leadership'],
 0.25),

-- Weiss ↔ Brenner (Plant Director ↔ VP Quality): strong synergy
('84000000-0000-0000-0000-000000000002',
 '30000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000003',
 'hierarchical', 0.72,
 ARRAY[]::VARCHAR(50)[],
 ARRAY['stakeholder_management', 'cultural_sensitivity', 'operational_execution'],
 0.30),

-- Richter ↔ Brenner (VP Production ↔ VP Quality): productive tension
('84000000-0000-0000-0000-000000000003',
 '30000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000003',
 'peer', 0.55,
 ARRAY['innovation_orientation'],
 ARRAY['operational_execution', 'technical_depth'],
 0.55),

-- Richter ↔ Mayer (VP Production ↔ Head of Logistics): friction (Mayer escalates everything to Richter)
('84000000-0000-0000-0000-000000000004',
 '30000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000007',
 'hierarchical', -0.15,
 ARRAY['strategic_thinking', 'crisis_leadership', 'resilience_adaptability'],
 ARRAY[]::VARCHAR(50)[],
 0.10),

-- Weiss ↔ Krause (Plant Director ↔ Head of Digital): frustration
('84000000-0000-0000-0000-000000000005',
 '30000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000005',
 'cross_functional', 0.15,
 ARRAY['innovation_orientation', 'strategic_thinking', 'change_management'],
 ARRAY['cultural_sensitivity'],
 0.15),

-- Weiss ↔ Bergmann (Plant Director ↔ HR Director): excellent partnership
('84000000-0000-0000-0000-000000000006',
 '30000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000006',
 'hierarchical', 0.82,
 ARRAY[]::VARCHAR(50)[],
 ARRAY['people_development', 'cultural_sensitivity', 'stakeholder_management'],
 0.20),


-- === KEY CANDIDATE COMPATIBILITY (for demo) ===

-- Dr. Felix Hartmann ↔ Brenner: high groupthink risk (both are steady-state operators)
('84000000-0000-0000-0000-000000000007',
 '31000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000003',
 'peer', 0.45,
 ARRAY[]::VARCHAR(50)[],
 ARRAY['operational_execution', 'technical_depth'],
 0.72),

-- Lisa Weber ↔ Brenner: strong complementary (transformation + quality rigor)
('84000000-0000-0000-0000-000000000008',
 '31000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000003',
 'peer', 0.78,
 ARRAY[]::VARCHAR(50)[],
 ARRAY['change_management', 'innovation_orientation', 'cross_functional_collaboration'],
 0.12),

-- David Park (UNICORN) ↔ Brenner: destructive friction
('84000000-0000-0000-0000-000000000009',
 '32000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000003',
 'peer', -0.42,
 ARRAY['cultural_sensitivity', 'cross_functional_collaboration', 'people_development'],
 ARRAY['operational_execution'],
 0.05),

-- David Park (UNICORN) ↔ Weiss: major friction
('84000000-0000-0000-0000-000000000010',
 '32000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000001',
 'hierarchical', -0.28,
 ARRAY['cultural_sensitivity', 'cross_functional_collaboration'],
 ARRAY['strategic_thinking', 'crisis_leadership'],
 0.08),

-- Dr. Elena Voronova (HIDDEN GEM) ↔ Brenner: excellent synergy
('84000000-0000-0000-0000-000000000011',
 '32000000-0000-0000-0000-000000000007', '30000000-0000-0000-0000-000000000003',
 'peer', 0.80,
 ARRAY[]::VARCHAR(50)[],
 ARRAY['change_management', 'people_development', 'cultural_sensitivity'],
 0.15),

-- Dr. Elena Voronova (HIDDEN GEM) ↔ Weiss: excellent synergy
('84000000-0000-0000-0000-000000000012',
 '32000000-0000-0000-0000-000000000007', '30000000-0000-0000-0000-000000000001',
 'hierarchical', 0.85,
 ARRAY[]::VARCHAR(50)[],
 ARRAY['change_management', 'cross_functional_collaboration', 'cultural_sensitivity', 'people_development'],
 0.18),

-- Claudia Fischer ↔ Weiss: strong but some strategic overlap
('84000000-0000-0000-0000-000000000013',
 '32000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000001',
 'hierarchical', 0.62,
 ARRAY['strategic_thinking'],
 ARRAY['operational_execution', 'change_management', 'technical_depth'],
 0.28),

-- Sarah Chen (Tesla) ↔ Brenner: friction on pace and process
('84000000-0000-0000-0000-000000000014',
 '32000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000003',
 'peer', 0.18,
 ARRAY['cultural_sensitivity', 'people_development'],
 ARRAY['innovation_orientation', 'resilience_adaptability'],
 0.08),

-- Sarah Chen (Tesla) ↔ Bergmann: friction on works council approach
('84000000-0000-0000-0000-000000000015',
 '32000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000006',
 'cross_functional', -0.10,
 ARRAY['cultural_sensitivity', 'people_development'],
 ARRAY['change_management'],
 0.05);
