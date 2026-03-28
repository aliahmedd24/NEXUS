-- ============================================================================
-- NEXUS Seed Data: 02 — Leaders, Candidates, and Roles
-- 8 current leaders, 6 internal candidates, 10 external candidates, 10 roles
-- ============================================================================

-- ============================================================================
-- STEP 1: Insert all leaders WITHOUT current_role_id (avoid circular FK)
-- ============================================================================

-- === CURRENT LEADERS (8) ===

-- L01: Dr. Katharina Weiss — Plant Director Munich (EXCELLENT leader)
-- Narrative: 22-year BMW veteran, led Dingolfing through COVID, drove iFACTORY pilot. Gold standard.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('30000000-0000-0000-0000-000000000001', 'Dr. Katharina Weiss', NULL, 'internal_current', 28, 22, 'phd', ARRAY['automotive','manufacturing'], ARRAY['Munich','Dingolfing'], 0.08);

-- L02: Thomas Richter — VP Production Munich (RETIRING in ~12 months)
-- Narrative: 30-year veteran, exceptional operational leader but analog mindset. Retirement triggers the demo vacancy.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('30000000-0000-0000-0000-000000000002', 'Thomas Richter', NULL, 'internal_current', 34, 30, 'masters', ARRAY['automotive'], ARRAY['Munich'], 0.85);

-- L03: Markus Brenner — VP Quality Munich (SOLID, steady performer)
-- Narrative: Quality obsessive, excellent with works council, limited transformation appetite.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('30000000-0000-0000-0000-000000000003', 'Markus Brenner', NULL, 'internal_current', 21, 18, 'masters', ARRAY['automotive','consulting'], ARRAY['Munich'], 0.12);

-- L04: Dr. Lena Hoffmann — Head of Supply Chain EMEA (BEING POACHED by Mercedes)
-- Narrative: Brilliant strategist, rebuilt supply chain post-chip-shortage. Mercedes offering €80K more + board track.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('30000000-0000-0000-0000-000000000004', 'Dr. Lena Hoffmann', NULL, 'internal_current', 19, 11, 'phd', ARRAY['automotive','consulting','logistics'], ARRAY['Munich','Stuttgart'], 0.72);

-- L05: Stefan Krause — Head of Digital/iFACTORY (WRONG ROLE — too operational for digital transformation)
-- Narrative: Promoted from plant floor IT. Strong execution, weak on vision. iFACTORY transformation stalling.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('30000000-0000-0000-0000-000000000005', 'Stefan Krause', NULL, 'internal_current', 16, 14, 'bachelors', ARRAY['automotive','manufacturing_it'], ARRAY['Munich'], 0.15);

-- L06: Anna Bergmann — HR Director Plant Munich (SOLID)
-- Narrative: Key works council liaison, deep institutional knowledge, manages 7,800-person workforce.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('30000000-0000-0000-0000-000000000006', 'Anna Bergmann', NULL, 'internal_current', 17, 13, 'masters', ARRAY['automotive','hr_consulting'], ARRAY['Munich'], 0.10);

-- L07: Jürgen Mayer — Head of Production Logistics (STRUGGLING)
-- Narrative: Promoted too fast after predecessor left suddenly. Drowning in complexity. Team attrition rising.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('30000000-0000-0000-0000-000000000007', 'Jürgen Mayer', NULL, 'internal_current', 12, 10, 'masters', ARRAY['automotive'], ARRAY['Munich'], 0.20);

-- L08: James Carter — VP Production Spartanburg (DECENT but mismatched for EV transition)
-- Narrative: Excellent for ICE X-model production. Zero EV experience. Spartanburg transitioning to EV by 2028.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('30000000-0000-0000-0000-000000000008', 'James Carter', NULL, 'internal_current', 23, 15, 'mba', ARRAY['automotive','manufacturing'], ARRAY['Spartanburg','Greer'], 0.18);


-- === INTERNAL CANDIDATES (6) ===

-- IC01: Dr. Felix Hartmann — Deputy VP Production Munich
-- Narrative: "Internal favorite" — everyone expects he'll replace Richter. But genome shows he's a steady-state operator, not a transformation leader. Demonstrates system's value by flagging this.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('31000000-0000-0000-0000-000000000001', 'Dr. Felix Hartmann', NULL, 'internal_candidate', 18, 15, 'phd', ARRAY['automotive','manufacturing'], ARRAY['Munich'], 0.35);

-- IC02: Lisa Weber — Senior Manager, Neue Klasse Program
-- Narrative: Hidden potential. Led battery integration workstream. Cross-functional superstar but junior title. Ready in 6 months with coaching.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('31000000-0000-0000-0000-000000000002', 'Lisa Weber', NULL, 'internal_candidate', 14, 9, 'masters', ARRAY['automotive','ev_systems','consulting'], ARRAY['Munich','Debrecen'], 0.25);

-- IC03: Michael Schneider — Plant Manager, Dingolfing Sub-Assembly
-- Narrative: Solid operational leader managing 2,200 people. Ready in 12 months. Low risk, moderate upside.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('31000000-0000-0000-0000-000000000003', 'Michael Schneider', NULL, 'internal_candidate', 20, 16, 'masters', ARRAY['automotive','manufacturing'], ARRAY['Dingolfing','Munich'], 0.15);

-- IC04: Dr. Aisha Patel — Head of Battery Cell Engineering, R&D FIZ
-- Narrative: Deep EV battery expertise. Ready now for Head of EV Battery Systems. Came from CATL 4 years ago.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('31000000-0000-0000-0000-000000000004', 'Dr. Aisha Patel', NULL, 'internal_candidate', 16, 4, 'phd', ARRAY['battery_technology','automotive','chemical_engineering'], ARRAY['Munich'], 0.40);

-- IC05: Tobias Krüger — Senior Manager Quality, Spartanburg
-- Narrative: Quality specialist with international experience. Ready in 24 months. Strong cultural sensitivity.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('31000000-0000-0000-0000-000000000005', 'Tobias Krüger', NULL, 'internal_candidate', 13, 8, 'masters', ARRAY['automotive','quality_management'], ARRAY['Spartanburg','Munich'], 0.20);

-- IC06: Sandra Voss — Deputy Head of Supply Chain EMEA
-- Narrative: Dr. Hoffmann's #2. If Hoffmann leaves (high flight risk), Voss is the succession plan. Ready in 6 months.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('31000000-0000-0000-0000-000000000006', 'Sandra Voss', NULL, 'internal_candidate', 15, 7, 'mba', ARRAY['automotive','logistics','supply_chain'], ARRAY['Munich'], 0.18);


-- === EXTERNAL CANDIDATES (10) ===

-- EC01: Dr. Klaus Reimann — VP Manufacturing, Mercedes-Benz
-- Narrative: Automotive veteran. Ran Mercedes EQ production line. Strong but expensive.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000001', 'Dr. Klaus Reimann', NULL, 'external_candidate', 25, 0, 'phd', ARRAY['automotive','manufacturing','ev_systems'], ARRAY['Stuttgart','Munich'], NULL);

-- EC02: Sarah Chen — Director of Operations, Tesla Gigafactory Berlin
-- Narrative: EV-native manufacturing leader. Radical pace, unconventional methods. Culture clash risk at BMW.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000002', 'Sarah Chen', NULL, 'external_candidate', 15, 0, 'mba', ARRAY['ev_manufacturing','tech','battery_systems'], ARRAY['Berlin','Munich'], NULL);

-- EC03: Marcus Williams — Partner, McKinsey Operations Practice
-- Narrative: Consulting superstar. Brilliant strategy, zero production floor experience. High risk.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000003', 'Marcus Williams', NULL, 'external_candidate', 18, 0, 'mba', ARRAY['consulting','automotive_advisory','transformation'], ARRAY['Munich','London'], NULL);

-- EC04: Dr. Raj Mehta — VP Battery Systems, CATL Europe
-- Narrative: Deep battery expertise. Critical for EV Battery Systems role. Limited general management experience.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000004', 'Dr. Raj Mehta', NULL, 'external_candidate', 20, 0, 'phd', ARRAY['battery_technology','chemical_engineering','ev_systems'], ARRAY['Munich','Erfurt'], NULL);

-- EC05: Claudia Fischer — SVP Production, Volkswagen Group
-- Narrative: Ran VW Zwickau EV transformation. Proven at scale. Non-compete concerns.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000005', 'Claudia Fischer', NULL, 'external_candidate', 24, 0, 'masters', ARRAY['automotive','ev_manufacturing','manufacturing'], ARRAY['Wolfsburg','Munich','Debrecen'], NULL);

-- EC06: David Park — Director of Manufacturing, Amazon Robotics
-- Narrative: THE "UNICORN" — perfect on paper (tech + operations + scale). Poor team chemistry with BMW's collaborative culture. Too individualistic, impatient with consensus.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000006', 'David Park', NULL, 'external_candidate', 17, 0, 'mba', ARRAY['tech','robotics','manufacturing','logistics'], ARRAY['Seattle','Munich','Berlin'], NULL);

-- EC07: Dr. Elena Voronova — Head of Plant Transformation, Bosch
-- Narrative: THE "HIDDEN GEM" — imperfect CV (no OEM experience), but outstanding genome match. Led Bosch Reutlingen plant through Industry 4.0 transformation. Exceptional change management + works council skills.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000007', 'Dr. Elena Voronova', NULL, 'external_candidate', 19, 0, 'phd', ARRAY['tier1_supplier','manufacturing','transformation','industry_4_0'], ARRAY['Reutlingen','Munich','Debrecen'], NULL);

-- EC08: Pierre Dubois — VP Supply Chain, Stellantis
-- Narrative: Supply chain expert with European-wide network. Relevant for Supply Chain EMEA role.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000008', 'Pierre Dubois', NULL, 'external_candidate', 22, 0, 'masters', ARRAY['automotive','supply_chain','logistics'], ARRAY['Paris','Munich'], NULL);

-- EC09: Dr. Yuki Tanaka — Director of AI Manufacturing, Siemens
-- Narrative: Digital manufacturing specialist. Strong for Head of Digital/iFACTORY if Krause is moved.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000009', 'Dr. Yuki Tanaka', NULL, 'external_candidate', 16, 0, 'phd', ARRAY['industrial_automation','ai_manufacturing','digital_twin'], ARRAY['Munich','Erlangen'], NULL);

-- EC10: Robert Schwarz — VP Operations, BMW Motorrad
-- Narrative: Internal-adjacent. Knows BMW culture. Ran Motorrad Berlin plant. Limited EV exposure but strong culture fit.
INSERT INTO leaders (id, full_name, current_role_id, leader_type, years_experience, years_at_bmw, education_level, industry_background, location_preference, flight_risk) VALUES
('32000000-0000-0000-0000-000000000010', 'Robert Schwarz', NULL, 'external_candidate', 20, 12, 'masters', ARRAY['automotive','motorcycle_manufacturing','manufacturing'], ARRAY['Berlin','Munich'], NULL);


-- ============================================================================
-- STEP 2: Insert Roles
-- ============================================================================

INSERT INTO roles (id, title, role_level, org_unit_id, is_filled, current_holder_id, reports_to_role_id, criticality) VALUES

-- R01: Plant Director — Munich (filled by Dr. Katharina Weiss)
('20000000-0000-0000-0000-000000000001', 'Plant Director — Munich',          'SVP',      '10000000-0000-0000-0000-000000000002', TRUE,  '30000000-0000-0000-0000-000000000001', NULL,                                          'critical'),

-- R02: VP Production — Munich (filled by Thomas Richter — RETIRING)
('20000000-0000-0000-0000-000000000002', 'VP Production — Munich',           'VP',       '10000000-0000-0000-0000-000000000002', TRUE,  '30000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', 'critical'),

-- R03: VP Quality — Munich (filled by Markus Brenner)
('20000000-0000-0000-0000-000000000003', 'VP Quality — Munich',              'VP',       '10000000-0000-0000-0000-000000000002', TRUE,  '30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000001', 'critical'),

-- R04: Head of Supply Chain — EMEA (filled by Dr. Lena Hoffmann — FLIGHT RISK)
('20000000-0000-0000-0000-000000000004', 'Head of Supply Chain — EMEA',      'Director', '10000000-0000-0000-0000-000000000007', TRUE,  '30000000-0000-0000-0000-000000000004', NULL,                                          'critical'),

-- R05: Head of EV Battery Systems (VACANT — primary demo trigger)
('20000000-0000-0000-0000-000000000005', 'Head of EV Battery Systems',       'Director', '10000000-0000-0000-0000-000000000011', FALSE, NULL,                                          NULL,                                          'critical'),

-- R06: Head of Digital / iFACTORY (filled by Stefan Krause — WRONG ROLE)
('20000000-0000-0000-0000-000000000006', 'Head of Digital / iFACTORY',       'Director', '10000000-0000-0000-0000-000000000008', TRUE,  '30000000-0000-0000-0000-000000000005', NULL,                                          'high'),

-- R07: HR Director — Plant Munich (filled by Anna Bergmann)
('20000000-0000-0000-0000-000000000007', 'HR Director — Plant Munich',       'Director', '10000000-0000-0000-0000-000000000009', TRUE,  '30000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000001', 'high'),

-- R08: Head of Production Logistics (filled by Jürgen Mayer — STRUGGLING)
('20000000-0000-0000-0000-000000000008', 'Head of Production Logistics',     'Director', '10000000-0000-0000-0000-000000000002', TRUE,  '30000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000002', 'high'),

-- R09: Plant Director — Debrecen (VACANT — secondary demo trigger, greenfield Neue Klasse plant)
('20000000-0000-0000-0000-000000000009', 'Plant Director — Debrecen',        'SVP',      '10000000-0000-0000-0000-000000000005', FALSE, NULL,                                          NULL,                                          'critical'),

-- R10: VP Production — Spartanburg (filled by James Carter)
('20000000-0000-0000-0000-000000000010', 'VP Production — Spartanburg',      'VP',       '10000000-0000-0000-0000-000000000004', TRUE,  '30000000-0000-0000-0000-000000000008', NULL,                                          'high');


-- ============================================================================
-- STEP 3: Update leaders with their current_role_id
-- ============================================================================

UPDATE leaders SET current_role_id = '20000000-0000-0000-0000-000000000001' WHERE id = '30000000-0000-0000-0000-000000000001';
UPDATE leaders SET current_role_id = '20000000-0000-0000-0000-000000000002' WHERE id = '30000000-0000-0000-0000-000000000002';
UPDATE leaders SET current_role_id = '20000000-0000-0000-0000-000000000003' WHERE id = '30000000-0000-0000-0000-000000000003';
UPDATE leaders SET current_role_id = '20000000-0000-0000-0000-000000000004' WHERE id = '30000000-0000-0000-0000-000000000004';
UPDATE leaders SET current_role_id = '20000000-0000-0000-0000-000000000006' WHERE id = '30000000-0000-0000-0000-000000000005';
UPDATE leaders SET current_role_id = '20000000-0000-0000-0000-000000000007' WHERE id = '30000000-0000-0000-0000-000000000006';
UPDATE leaders SET current_role_id = '20000000-0000-0000-0000-000000000008' WHERE id = '30000000-0000-0000-0000-000000000007';
UPDATE leaders SET current_role_id = '20000000-0000-0000-0000-000000000010' WHERE id = '30000000-0000-0000-0000-000000000008';
