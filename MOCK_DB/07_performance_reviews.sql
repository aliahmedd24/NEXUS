-- ============================================================================
-- NEXUS Seed Data: 07 — Performance Reviews
-- 2-3 review periods per current leader
-- NOTE: Raw ratings deliberately compressed into 6.5-8.5 range to demonstrate
-- the "safe rating" bias problem that NEXUS's Genome Agent decompresses
-- ============================================================================

INSERT INTO performance_reviews (id, leader_id, review_period, overall_rating, goal_completion_pct, reviewer_id, review_narrative, team_engagement_score, team_attrition_rate) VALUES

-- === Dr. Katharina Weiss (EXCELLENT — but ratings look similar to average leaders) ===
('62000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '2024',    8.2, 94.0, NULL,
 'Dr. Weiss exceeded all plant-level targets. Munich achieved record throughput while maintaining quality standards. Led iFACTORY pilot launch on schedule. Works council relationship rated exemplary by HR Central. Recommended for Group-level leadership development program.',
 4.3, 0.04),

('62000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '2025-H1', 8.0, 91.0, NULL,
 'Continued strong performance. Successfully managed production ramp of new 3-series variant while integrating EV line preparations. Minor delay in sustainability KPIs due to energy cost volatility. Team engagement remains highest in plant network.',
 4.4, 0.03),

('62000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', '2023',    8.1, 92.0, NULL,
 'Led Munich plant through challenging year including chip shortage tail effects and energy cost crisis. Maintained production targets through creative scheduling optimization. Zero safety incidents in leadership team.',
 4.2, 0.05),

-- === Thomas Richter (RETIRING — ratings compressed, don't show the problem) ===
('62000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000002', '2024',    7.8, 88.0, NULL,
 'Richter delivered solid production numbers. OEE at 98.2%, best in network. Some delays in digital twin adoption not reflected in quantitative targets. Succession planning initiated given planned 2027 retirement.',
 3.5, 0.08),

('62000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000002', '2025-H1', 7.5, 82.0, NULL,
 'Production targets met. iFACTORY KPIs missed — digital readiness assessment scored 42% vs. 65% target. Engagement scores declining among younger engineers. Retirement timeline under discussion with HR.',
 3.3, 0.10),

('62000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000002', '2023',    7.9, 90.0, NULL,
 'Strong operational year. Richter managed the supplier disruption with minimal production impact through creative line balancing. Traditional approach continues to deliver in steady-state conditions.',
 3.7, 0.06),

-- === Markus Brenner (SOLID — ratings look nearly identical to struggling leaders) ===
('62000000-0000-0000-0000-000000000007', '30000000-0000-0000-0000-000000000003', '2024',    7.8, 89.0, NULL,
 'Quality metrics improved 12% YoY. Field claim rate for Munich-produced vehicles at historic low. Audit scores consistently above 95%. Works council praised quality team transparency during incident investigations.',
 3.9, 0.05),

('62000000-0000-0000-0000-000000000008', '30000000-0000-0000-0000-000000000003', '2025-H1', 7.7, 87.0, NULL,
 'Maintained quality standards during 3-series variant launch. Minor hesitation on AI-driven inspection rollout but ultimately supported pilot. Team stability excellent.',
 3.8, 0.04),

-- === Dr. Lena Hoffmann (BEING POACHED — high performer but compressed ratings hide it) ===
('62000000-0000-0000-0000-000000000009', '30000000-0000-0000-0000-000000000004', '2024',    8.3, 96.0, NULL,
 'Exceptional year. Rebuilt supplier risk framework. Achieved €2.9B in cost savings through strategic sourcing optimization. Led crisis response during Tier-2 supplier bankruptcy affecting Dingolfing. Zero production stops attributable to supply chain.',
 3.8, 0.07),

('62000000-0000-0000-0000-000000000010', '30000000-0000-0000-0000-000000000004', '2025-H1', 8.1, 93.0, NULL,
 'Continued strong performance. On track for Neue Klasse supplier onboarding milestones. Some concern about team development delegation — Hoffmann tends to handle critical negotiations personally rather than developing deputies.',
 3.6, 0.09),

-- === Stefan Krause (WRONG ROLE — ratings don't flag the fundamental mismatch) ===
('62000000-0000-0000-0000-000000000011', '30000000-0000-0000-0000-000000000005', '2024',    7.2, 78.0, NULL,
 'IT infrastructure reliability maintained at high levels. iFACTORY pilot delayed 4 months — attributed to vendor issues but root cause analysis suggests leadership vision gap. Digital talent retention concerning — 3 senior engineers departed for competitors.',
 3.1, 0.14),

('62000000-0000-0000-0000-000000000012', '30000000-0000-0000-0000-000000000005', '2025-H1', 6.8, 72.0, NULL,
 'iFACTORY program now 8 months behind schedule. Krause struggles to articulate compelling digital vision to plant leadership. Recommend performance improvement plan or role reassignment discussion.',
 2.9, 0.18),

-- === Anna Bergmann (SOLID HR Director) ===
('62000000-0000-0000-0000-000000000013', '30000000-0000-0000-0000-000000000006', '2024',    7.9, 90.0, NULL,
 'Successfully negotiated flexible working time agreement with works council. Zero labor disputes. Talent pipeline for production leadership strengthened with cross-plant rotation program launch. Employee satisfaction survey highest in 5 years.',
 4.1, 0.03),

('62000000-0000-0000-0000-000000000014', '30000000-0000-0000-0000-000000000006', '2025-H1', 7.8, 88.0, NULL,
 'Managed sensitive restructuring of Hall 4 assembly line automation with zero grievances. Retraining program for 120 affected associates on track. Works council relationship remains strong anchor.',
 4.0, 0.04),

-- === Jürgen Mayer (STRUGGLING — but even his ratings aren't catastrophic) ===
('62000000-0000-0000-0000-000000000015', '30000000-0000-0000-0000-000000000007', '2024',    7.0, 74.0, NULL,
 'Transition to Head of Logistics has been challenging. Inbound delivery accuracy declined from 97.8% to 95.2%. Team escalations to VP Production increased 3x. Mayer is working hard but the role complexity exceeds current capabilities. Development support recommended.',
 2.8, 0.15),

('62000000-0000-0000-0000-000000000016', '30000000-0000-0000-0000-000000000007', '2025-H1', 6.5, 68.0, NULL,
 'Further decline in logistics KPIs. Delivery accuracy now at 94.1%. Three senior team members requested transfers. JIT sequencing errors caused two partial line stops in Q1 2026. Urgent intervention required — recommend executive coaching and interim deputy appointment.',
 2.4, 0.22),

-- === James Carter (DECENT, mismatched for EV future) ===
('62000000-0000-0000-0000-000000000017', '30000000-0000-0000-0000-000000000008', '2024',    7.9, 91.0, NULL,
 'Spartanburg plant performance excellent. Record X5 production volume. Workforce attrition well below regional average. Carter is highly effective in current ICE production context. Concern noted for 2028 EV transition readiness.',
 4.0, 0.05),

('62000000-0000-0000-0000-000000000018', '30000000-0000-0000-0000-000000000008', '2025-H1', 7.7, 87.0, NULL,
 'Continued strong ICE production numbers. EV preparation milestones partially missed — Carter has not completed assigned EV manufacturing leadership program modules. Development plan needs enforcement.',
 3.9, 0.06);
