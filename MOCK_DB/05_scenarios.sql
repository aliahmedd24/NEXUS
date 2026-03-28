-- ============================================================================
-- NEXUS Seed Data: 05 — Scenarios & Stress Tests
-- 8 scenarios per §4.1 including 1 compound scenario
-- ============================================================================

INSERT INTO scenarios (id, name, category, narrative, probability, capability_demand_vector, affected_org_units, time_horizon_months, compound_of) VALUES

-- S1: Neue Klasse Ramp-Up Accelerated
('40000000-0000-0000-0000-000000000001',
 'Neue Klasse Ramp-Up Accelerated (6 months earlier)',
 'transformation',
 'BMW Board of Management decides to accelerate the Neue Klasse platform launch by 6 months to counter competitive pressure from Mercedes EQ and Chinese EV manufacturers. Plant Debrecen must achieve Job 1 by Q2 2026 instead of Q4 2026. Munich plant EV line integration moves forward simultaneously. All EV-related leadership positions face dramatically increased pressure. Supply chain must onboard 200+ new EV component suppliers in compressed timeline.',
 0.40,
 '{"change_management": 0.95, "technical_depth": 0.85, "innovation_orientation": 0.80, "operational_execution": 0.75, "crisis_leadership": 0.70, "cross_functional_collaboration": 0.80, "strategic_thinking": 0.70, "resilience_adaptability": 0.85, "people_development": 0.60, "cultural_sensitivity": 0.50, "risk_calibration": 0.65, "stakeholder_management": 0.60}',
 ARRAY['10000000-0000-0000-0000-000000000005','10000000-0000-0000-0000-000000000006','10000000-0000-0000-0000-000000000011','10000000-0000-0000-0000-000000000002','10000000-0000-0000-0000-000000000007']::UUID[],
 18,
 NULL),

-- S2: Tier-1 Battery Supplier Default
('40000000-0000-0000-0000-000000000002',
 'Tier-1 Battery Supplier Default',
 'crisis',
 'A major Tier-1 battery cell supplier (representing 35% of BMW''s planned Neue Klasse cell supply) files for bankruptcy protection after failing to achieve volume production targets. BMW faces a 6-month supply gap affecting Debrecen plant ramp-up and Munich EV line. Alternative suppliers require 9-12 months to qualify. Emergency dual-sourcing negotiations needed with Samsung SDI and Northvolt.',
 0.15,
 '{"crisis_leadership": 0.95, "stakeholder_management": 0.90, "strategic_thinking": 0.85, "cross_functional_collaboration": 0.80, "risk_calibration": 0.85, "resilience_adaptability": 0.90, "operational_execution": 0.70, "change_management": 0.65, "technical_depth": 0.75, "innovation_orientation": 0.40, "people_development": 0.30, "cultural_sensitivity": 0.60}',
 ARRAY['10000000-0000-0000-0000-000000000011','10000000-0000-0000-0000-000000000007','10000000-0000-0000-0000-000000000006','10000000-0000-0000-0000-000000000005']::UUID[],
 12,
 NULL),

-- S3: EU Mandates 100% EV Sales by 2030
('40000000-0000-0000-0000-000000000003',
 'EU Mandates 100% EV Sales by 2030',
 'regulatory',
 'European Commission passes emergency regulation mandating 100% zero-emission new vehicle sales by 2030, four years ahead of previous 2035 target. BMW must accelerate ICE wind-down across all European plants. Dingolfing (7-series, 5-series) and Munich face dual production challenge. Workforce reskilling timeline compressed. €2B+ additional capital investment required for production conversion.',
 0.25,
 '{"strategic_thinking": 0.90, "change_management": 0.90, "people_development": 0.80, "risk_calibration": 0.80, "stakeholder_management": 0.75, "operational_execution": 0.70, "cross_functional_collaboration": 0.75, "resilience_adaptability": 0.80, "technical_depth": 0.65, "innovation_orientation": 0.70, "crisis_leadership": 0.55, "cultural_sensitivity": 0.65}',
 ARRAY['10000000-0000-0000-0000-000000000002','10000000-0000-0000-0000-000000000003','10000000-0000-0000-0000-000000000006','10000000-0000-0000-0000-000000000001']::UUID[],
 36,
 NULL),

-- S4: Competitor Poaches 3 Senior Leaders
('40000000-0000-0000-0000-000000000004',
 'Competitor Poaches 3 Senior Leaders',
 'competitive',
 'Mercedes-Benz and Rivian simultaneously recruit three BMW senior leaders: Head of Supply Chain EMEA (Dr. Hoffmann), a Plant Director candidate, and the Head of EV Battery Systems (vacant role becomes even more critical). BMW faces cascading succession gaps in Q3 2026. Internal pipeline tested under extreme conditions. Employer brand in EV leadership market damaged.',
 0.20,
 '{"people_development": 0.90, "resilience_adaptability": 0.90, "cross_functional_collaboration": 0.80, "change_management": 0.75, "cultural_sensitivity": 0.80, "stakeholder_management": 0.75, "crisis_leadership": 0.70, "strategic_thinking": 0.65, "operational_execution": 0.60, "risk_calibration": 0.65, "technical_depth": 0.50, "innovation_orientation": 0.45}',
 ARRAY['10000000-0000-0000-0000-000000000007','10000000-0000-0000-0000-000000000011','10000000-0000-0000-0000-000000000001']::UUID[],
 12,
 NULL),

-- S5: Connected Vehicle Cybersecurity Breach
('40000000-0000-0000-0000-000000000005',
 'Connected Vehicle Cybersecurity Breach',
 'crisis',
 'A zero-day vulnerability in BMW''s Connected Drive platform is exploited, affecting 2.3 million vehicles worldwide. Remote access to vehicle telemetry and limited control functions compromised. Regulatory investigation in EU, US, and China launched simultaneously. Production of affected models halted pending software patch verification. Brand reputation crisis requires coordinated C-suite response.',
 0.10,
 '{"crisis_leadership": 0.95, "stakeholder_management": 0.90, "cross_functional_collaboration": 0.85, "technical_depth": 0.85, "risk_calibration": 0.80, "resilience_adaptability": 0.85, "strategic_thinking": 0.70, "cultural_sensitivity": 0.65, "operational_execution": 0.60, "change_management": 0.50, "people_development": 0.35, "innovation_orientation": 0.45}',
 ARRAY['10000000-0000-0000-0000-000000000008','10000000-0000-0000-0000-000000000012','10000000-0000-0000-0000-000000000001']::UUID[],
 6,
 NULL),

-- S6: China Market Access Restricted
('40000000-0000-0000-0000-000000000006',
 'China Market Access Restricted',
 'market',
 'Escalating trade tensions result in 45% tariff on European luxury vehicles entering China and forced technology transfer requirements for continued production at BMW Brilliance Automotive (Shenyang). China represents ~33% of BMW Group sales. Board must decide: absorb margins, localize further, or pivot to other growth markets. Workforce restructuring across European plants if China volume falls 25%+.',
 0.15,
 '{"strategic_thinking": 0.95, "risk_calibration": 0.90, "stakeholder_management": 0.85, "resilience_adaptability": 0.85, "change_management": 0.80, "cultural_sensitivity": 0.80, "operational_execution": 0.65, "people_development": 0.65, "cross_functional_collaboration": 0.70, "crisis_leadership": 0.70, "technical_depth": 0.45, "innovation_orientation": 0.50}',
 ARRAY['10000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000007','10000000-0000-0000-0000-000000000004']::UUID[],
 24,
 NULL),

-- S7: Steady-State Premium Growth
('40000000-0000-0000-0000-000000000007',
 'Steady-State Premium Growth',
 'market',
 'Global premium automotive market grows 4-6% annually through 2028. No major disruptions. BMW''s order book strong across all models. Plants running at 92%+ capacity utilization. Focus shifts to operational efficiency, quality leadership, and margin optimization. The "boring but important" scenario — requires operational excellence rather than transformation.',
 0.35,
 '{"operational_execution": 0.90, "stakeholder_management": 0.70, "people_development": 0.70, "risk_calibration": 0.65, "cross_functional_collaboration": 0.60, "strategic_thinking": 0.55, "cultural_sensitivity": 0.55, "technical_depth": 0.65, "resilience_adaptability": 0.50, "change_management": 0.35, "crisis_leadership": 0.30, "innovation_orientation": 0.45}',
 ARRAY['10000000-0000-0000-0000-000000000002','10000000-0000-0000-0000-000000000003','10000000-0000-0000-0000-000000000004','10000000-0000-0000-0000-000000000010']::UUID[],
 24,
 NULL),

-- S8: Compound — Ramp-up during supplier crisis (S1 + S2)
('40000000-0000-0000-0000-000000000008',
 'Compound: Neue Klasse Ramp-Up + Battery Supplier Default',
 'compound',
 'The nightmare scenario. BMW accelerates Neue Klasse ramp-up AND a critical battery supplier defaults simultaneously. Every leadership role in the EV/manufacturing chain faces extreme pressure. The compound effect creates emergent demands: leaders must manage transformation AND crisis concurrently, requiring both change management and crisis leadership at maximum levels. No single leader profile covers both — team composition becomes existentially important.',
 0.06,
 '{"change_management": 0.98, "crisis_leadership": 0.98, "resilience_adaptability": 0.95, "cross_functional_collaboration": 0.90, "strategic_thinking": 0.90, "technical_depth": 0.88, "operational_execution": 0.85, "risk_calibration": 0.88, "stakeholder_management": 0.85, "innovation_orientation": 0.75, "people_development": 0.65, "cultural_sensitivity": 0.60}',
 ARRAY['10000000-0000-0000-0000-000000000005','10000000-0000-0000-0000-000000000006','10000000-0000-0000-0000-000000000011','10000000-0000-0000-0000-000000000007','10000000-0000-0000-0000-000000000002']::UUID[],
 18,
 ARRAY['40000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000002']::UUID[]);
