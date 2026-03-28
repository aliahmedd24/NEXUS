-- ============================================================================
-- NEXUS Seed Data: 06 — 360° Feedback (Unstructured Text)
-- 3-5 entries per current leader, BMW-specific language
-- ============================================================================

INSERT INTO feedback_360 (id, leader_id, feedback_text, feedback_type, feedback_period, sentiment_score, extracted_traits) VALUES

-- === Dr. Katharina Weiss (EXCELLENT) ===
('61000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001',
 'Katharina is the most effective plant director I have worked with in 18 years at BMW. She navigated the COVID production shutdowns with remarkable composure and kept the works council aligned throughout the iFACTORY pilot. Her ability to communicate a clear vision while managing day-to-day operations is exceptional.',
 'peer_review', '2025-H2', 0.92,
 '{"strategic_thinking": 0.90, "crisis_leadership": 0.88, "cultural_sensitivity": 0.85, "stakeholder_management": 0.92}'),

('61000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001',
 'Dr. Weiss consistently invests in her people. She personally mentors three high-potential managers and has a strong track record of promoting talent into leadership roles. The only area where I see room for growth is in embracing more radical digital innovation — she tends to prefer proven approaches.',
 'direct_report', '2025-H2', 0.78,
 '{"people_development": 0.92, "innovation_orientation": 0.62, "risk_calibration": 0.75}'),

('61000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001',
 'Strong leader who understands the works council dynamic better than most. Her Dingolfing experience shows — she knows how to balance productivity targets with employee representation requirements. Betriebsrat trusts her.',
 'peer_review', '2025-H1', 0.85,
 '{"cultural_sensitivity": 0.90, "stakeholder_management": 0.88, "operational_execution": 0.82}'),

-- === Thomas Richter (RETIRING, analog mindset) ===
('61000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000002',
 'Thomas is a production legend — nobody understands the Munich body shop and paint shop better. But he has openly resisted the iFACTORY digital twin rollout, calling it "solutions looking for problems." His team respects his expertise but the younger engineers are frustrated by the lack of digital tooling.',
 'direct_report', '2025-H2', 0.35,
 '{"operational_execution": 0.92, "technical_depth": 0.88, "innovation_orientation": 0.25, "change_management": 0.30}'),

('61000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000002',
 'Richter delivered 98.2% OEE last quarter — best in the network. However, his reluctance to adopt predictive maintenance analytics and his preference for paper-based shift planning is creating a gap between Munich and the digital-first plants. Retirement cannot come soon enough for the transformation roadmap.',
 'manager', '2025-H2', 0.20,
 '{"operational_execution": 0.95, "innovation_orientation": 0.20, "change_management": 0.28, "resilience_adaptability": 0.45}'),

('61000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000002',
 'Solid production leader who knows every machine on the floor by name. Extremely reliable under pressure — during the 2024 supplier disruption he kept the line running with creative workarounds. Just not the right profile for where Munich production needs to go next.',
 'peer_review', '2025-H1', 0.55,
 '{"crisis_leadership": 0.85, "technical_depth": 0.90, "strategic_thinking": 0.55, "change_management": 0.35}'),

-- === Markus Brenner (SOLID quality VP) ===
('61000000-0000-0000-0000-000000000007', '30000000-0000-0000-0000-000000000003',
 'Markus runs a tight quality operation. Field quality metrics for Munich-built vehicles improved 12% year-over-year under his leadership. He works exceptionally well with the production team and has built a quality culture that extends to the shop floor.',
 'manager', '2025-H2', 0.82,
 '{"operational_execution": 0.88, "technical_depth": 0.85, "cross_functional_collaboration": 0.82}'),

('61000000-0000-0000-0000-000000000008', '30000000-0000-0000-0000-000000000003',
 'Brenner is reliable and thorough. My concern is that he is extremely comfortable in the current quality paradigm and may struggle with the shift to AI-driven quality inspection that iFACTORY demands. He prefers manual audit processes and has not shown enthusiasm for computer vision QC.',
 'peer_review', '2025-H1', 0.55,
 '{"operational_execution": 0.85, "innovation_orientation": 0.42, "change_management": 0.48}'),

('61000000-0000-0000-0000-000000000009', '30000000-0000-0000-0000-000000000003',
 'Very approachable leader. The works council appreciates his transparency during quality incident investigations. He never tries to hide problems, which builds trust across the organization.',
 'direct_report', '2025-H2', 0.80,
 '{"cultural_sensitivity": 0.88, "stakeholder_management": 0.80, "people_development": 0.72}'),

-- === Dr. Lena Hoffmann (BEING POACHED) ===
('61000000-0000-0000-0000-000000000010', '30000000-0000-0000-0000-000000000004',
 'Lena single-handedly rebuilt our European supplier risk management framework after the chip shortage. She identified the semiconductor concentration risk 6 months before it hit. Her strategic vision for supply chain is world-class. We cannot afford to lose her.',
 'manager', '2025-H2', 0.90,
 '{"strategic_thinking": 0.95, "crisis_leadership": 0.90, "risk_calibration": 0.88, "innovation_orientation": 0.82}'),

('61000000-0000-0000-0000-000000000011', '30000000-0000-0000-0000-000000000004',
 'Dr. Hoffmann is brilliant but can be impatient with team development. She sometimes takes over complex negotiations herself rather than coaching her deputies through them. Sandra Voss has grown significantly but mostly through observing Hoffmann rather than structured mentoring.',
 'direct_report', '2025-H1', 0.50,
 '{"strategic_thinking": 0.90, "people_development": 0.52, "stakeholder_management": 0.88}'),

('61000000-0000-0000-0000-000000000012', '30000000-0000-0000-0000-000000000004',
 'Outstanding negotiator. Managed the €90B purchasing volume renegotiation with Tier-1 suppliers and achieved 3.2% cost reduction while maintaining quality commitments. Her departure would leave a significant capability gap that internal successors cannot immediately fill.',
 'peer_review', '2025-H2', 0.85,
 '{"stakeholder_management": 0.92, "operational_execution": 0.85, "resilience_adaptability": 0.88}'),

-- === Stefan Krause (WRONG ROLE) ===
('61000000-0000-0000-0000-000000000013', '30000000-0000-0000-0000-000000000005',
 'Stefan keeps the IT infrastructure running reliably. Server uptime is 99.97%. But iFACTORY is not about uptime — it is about reimagining manufacturing through digital twins, AI, and real-time data. Stefan manages systems; we need someone who transforms through technology. There is a fundamental mismatch between his capabilities and the role requirements.',
 'manager', '2025-H2', 0.15,
 '{"operational_execution": 0.88, "innovation_orientation": 0.28, "strategic_thinking": 0.35, "change_management": 0.30}'),

('61000000-0000-0000-0000-000000000014', '30000000-0000-0000-0000-000000000005',
 'Krause is a nice colleague who tries hard, but the digital transformation agenda has stalled under his leadership. The iFACTORY pilot in Munich is 8 months behind schedule. He struggles to articulate a compelling digital vision to plant leadership and cannot inspire the younger digital talent we are trying to recruit.',
 'peer_review', '2025-H1', 0.22,
 '{"change_management": 0.32, "stakeholder_management": 0.45, "people_development": 0.50, "innovation_orientation": 0.30}'),

('61000000-0000-0000-0000-000000000015', '30000000-0000-0000-0000-000000000005',
 'I appreciate Stefan''s reliability and his willingness to fix issues quickly. However, I have been in three meetings where he could not explain how AI-powered quality inspection would work technically. The team is losing confidence in the digital roadmap.',
 'direct_report', '2025-H2', 0.30,
 '{"technical_depth": 0.60, "strategic_thinking": 0.38, "cross_functional_collaboration": 0.48}'),

-- === Anna Bergmann (SOLID HR Director) ===
('61000000-0000-0000-0000-000000000016', '30000000-0000-0000-0000-000000000006',
 'Anna is the glue that holds Munich plant HR together. Her relationship with the Betriebsrat is exceptional — she navigated the 2025 flexible working time agreement without a single escalation. She understands German co-determination law better than most lawyers.',
 'manager', '2025-H2', 0.88,
 '{"cultural_sensitivity": 0.95, "stakeholder_management": 0.88, "cross_functional_collaboration": 0.85}'),

('61000000-0000-0000-0000-000000000017', '30000000-0000-0000-0000-000000000006',
 'Bergmann is very supportive of talent development. She championed the cross-plant rotation program that sent two of my team members to Spartanburg. Her people-first approach is valued across the organization.',
 'peer_review', '2025-H1', 0.82,
 '{"people_development": 0.90, "cross_functional_collaboration": 0.82}'),

('61000000-0000-0000-0000-000000000018', '30000000-0000-0000-0000-000000000006',
 'Anna handles sensitive restructuring discussions with remarkable empathy. During the assembly line automation in Hall 4, she ensured every affected associate received retraining opportunities before the transition. No grievances filed.',
 'direct_report', '2025-H2', 0.85,
 '{"people_development": 0.88, "change_management": 0.78, "cultural_sensitivity": 0.90}'),

-- === Jürgen Mayer (STRUGGLING) ===
('61000000-0000-0000-0000-000000000019', '30000000-0000-0000-0000-000000000007',
 'Jürgen is overwhelmed. Since his predecessor left abruptly, he has been unable to stabilize the logistics operation. Inbound delivery accuracy dropped from 97.8% to 94.1%. Three of his senior team members have requested transfers. He needs either significant support or a role change.',
 'manager', '2025-H2', -0.45,
 '{"operational_execution": 0.42, "crisis_leadership": 0.35, "people_development": 0.30, "resilience_adaptability": 0.28}'),

('61000000-0000-0000-0000-000000000020', '30000000-0000-0000-0000-000000000007',
 'I do not feel supported by my manager. Decision-making is paralyzed — Jürgen escalates everything to the VP Production instead of making calls himself. Team morale is at an all-time low. Two colleagues have already accepted offers at other companies.',
 'direct_report', '2025-H2', -0.65,
 '{"crisis_leadership": 0.25, "risk_calibration": 0.30, "people_development": 0.22, "stakeholder_management": 0.35}'),

('61000000-0000-0000-0000-000000000021', '30000000-0000-0000-0000-000000000007',
 'Jürgen was an excellent senior manager but the jump to Head of Logistics was too much too fast. He lacks the strategic perspective and stakeholder management skills required at this level. A developmental demotion with coaching would be more humane than letting him continue to fail.',
 'peer_review', '2025-H1', -0.30,
 '{"strategic_thinking": 0.38, "stakeholder_management": 0.40, "resilience_adaptability": 0.32}'),

-- === James Carter (DECENT, ICE specialist) ===
('61000000-0000-0000-0000-000000000022', '30000000-0000-0000-0000-000000000008',
 'James runs Spartanburg like clockwork. The X3, X4, X5, X6, and X7 production lines are optimized to an impressive degree. He has deep relationships with the local workforce and the Spartanburg community. The concern is what happens when those lines transition to EV in 2028 — James has no EV manufacturing experience whatsoever.',
 'manager', '2025-H2', 0.60,
 '{"operational_execution": 0.88, "people_development": 0.82, "cultural_sensitivity": 0.70, "change_management": 0.38}'),

('61000000-0000-0000-0000-000000000023', '30000000-0000-0000-0000-000000000008',
 'Carter is a respected leader in Spartanburg. His open-door policy and genuine interest in associates'' welfare has kept plant attrition below 5% — remarkable for the Upstate SC labor market. He will need significant development to lead the EV production transition.',
 'peer_review', '2025-H1', 0.65,
 '{"people_development": 0.85, "operational_execution": 0.82, "innovation_orientation": 0.40, "change_management": 0.42}'),

('61000000-0000-0000-0000-000000000024', '30000000-0000-0000-0000-000000000008',
 'James is technically strong in ICE assembly and body-in-white processes. However, during the recent EV strategy briefing, he asked basic questions about battery pack integration that suggested minimal preparation. The Spartanburg EV transition will need either a transformed Carter or a different leader.',
 'direct_report', '2025-H2', 0.40,
 '{"technical_depth": 0.82, "innovation_orientation": 0.35, "strategic_thinking": 0.55}');
