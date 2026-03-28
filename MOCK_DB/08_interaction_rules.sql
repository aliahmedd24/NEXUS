-- ============================================================================
-- NEXUS Seed Data: 08 — Interaction Rules
-- Defines how leadership genome dimensions interact in team contexts
-- These rules drive the Team Chemistry Engine Agent
-- ============================================================================

INSERT INTO interaction_rules (id, dimension_a, dimension_b, relationship_type, interaction_effect, effect_magnitude, description) VALUES

-- === COMPLEMENTARY POSITIVE (different strengths create synergy) ===

('70000000-0000-0000-0000-000000000001', 'strategic_thinking', 'operational_execution', 'peer',
 'complementary_positive', 0.85,
 'A strategist paired with an executor creates a complete leadership dyad. The strategist sets direction; the executor delivers. Classic VP Production + Plant Director dynamic at BMW.'),

('70000000-0000-0000-0000-000000000002', 'innovation_orientation', 'risk_calibration', 'peer',
 'complementary_positive', 0.75,
 'An innovator balanced by a risk-calibrated partner produces bold but controlled transformation. Critical for iFACTORY digital transformation leadership pairs.'),

('70000000-0000-0000-0000-000000000003', 'change_management', 'cultural_sensitivity', 'peer',
 'complementary_positive', 0.80,
 'Transformation leaders who lack cultural sensitivity run into works council resistance. A culturally sensitive partner enables smoother change. Essential in German automotive context.'),

('70000000-0000-0000-0000-000000000004', 'crisis_leadership', 'stakeholder_management', 'peer',
 'complementary_positive', 0.70,
 'During crises, one leader stabilizes operations while another manages external stakeholders (board, media, regulators). Both capabilities needed but rarely in one person.'),

('70000000-0000-0000-0000-000000000005', 'technical_depth', 'people_development', 'hierarchical',
 'complementary_positive', 0.65,
 'Technical experts who develop talent create self-sustaining capability pipelines. A VP with deep technical knowledge who also grows successors is extremely valuable.'),

('70000000-0000-0000-0000-000000000006', 'cross_functional_collaboration', 'operational_execution', 'peer',
 'complementary_positive', 0.70,
 'A bridge-builder paired with a strong executor enables cross-silo initiatives to actually deliver results, not just generate meetings.'),

-- === CLASH NEGATIVE (opposing styles on shared-authority axes create friction) ===

('70000000-0000-0000-0000-000000000007', 'innovation_orientation', 'operational_execution', 'peer',
 'clash_negative', 0.60,
 'When both leaders share authority over the same domain, a radical innovator and a process-disciplined executor will clash on priorities. Common VP Production vs Head of Digital friction.'),

('70000000-0000-0000-0000-000000000008', 'risk_calibration', 'crisis_leadership', 'peer',
 'clash_negative', 0.45,
 'A highly risk-averse leader paired with a crisis-mode operator creates decision paralysis during ambiguous situations — one wants to wait, the other wants to act immediately.'),

('70000000-0000-0000-0000-000000000009', 'strategic_thinking', 'strategic_thinking', 'peer',
 'clash_negative', 0.55,
 'Two strong strategists competing for the same strategic agenda create political tension. Each wants to define direction. Common at VP level when roles overlap.'),

('70000000-0000-0000-0000-000000000010', 'stakeholder_management', 'stakeholder_management', 'peer',
 'clash_negative', 0.40,
 'Two leaders who both excel at managing upward can create competitive dynamics for board attention and sponsorship. Particularly toxic at SVP level.'),

-- === OVERLAP GROUPTHINK (identical profiles everywhere → blind spots) ===

('70000000-0000-0000-0000-000000000011', 'operational_execution', 'operational_execution', 'peer',
 'overlap_groupthink', 0.70,
 'A leadership team where everyone is an executor produces excellent short-term results but misses strategic shifts. The entire Munich plant leadership cannot be operators — someone needs to look up.'),

('70000000-0000-0000-0000-000000000012', 'risk_calibration', 'risk_calibration', 'peer',
 'overlap_groupthink', 0.65,
 'If all leaders are risk-averse, the organization becomes paralyzed during transformation. If all are risk-seeking, reckless decisions multiply. Diverse risk appetites are essential.'),

('70000000-0000-0000-0000-000000000013', 'cultural_sensitivity', 'cultural_sensitivity', 'peer',
 'overlap_groupthink', 0.50,
 'A team of exclusively consensus-oriented leaders avoids necessary conflict. In quality management, constructive tension between production and quality is healthy.'),

('70000000-0000-0000-0000-000000000014', 'change_management', 'change_management', 'peer',
 'overlap_groupthink', 0.55,
 'An all-transformation team loses operational discipline. BMW plants cannot afford to sacrifice daily production quality for long-term change initiatives.'),

('70000000-0000-0000-0000-000000000015', 'innovation_orientation', 'innovation_orientation', 'peer',
 'overlap_groupthink', 0.60,
 'A team of pure innovators generates ideas without execution. BMW''s premium quality standards require disciplined implementation alongside innovation.');
