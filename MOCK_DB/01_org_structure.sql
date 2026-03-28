-- ============================================================================
-- NEXUS Seed Data: 01 — Organizational Structure
-- 13 org units reflecting BMW Group's real structure
-- ============================================================================

INSERT INTO org_units (id, name, unit_type, parent_id, location_city, location_country, employee_count, strategic_priority) VALUES

-- Level 0: Group
('10000000-0000-0000-0000-000000000001', 'BMW Group Headquarters',         'group',      NULL,                                          'Munich',       'DEU', 159000, 'transformation'),

-- Level 1: Divisions / Plants
('10000000-0000-0000-0000-000000000002', 'BMW Group Plant Munich',          'plant',      '10000000-0000-0000-0000-000000000001', 'Munich',       'DEU', 7800,   'transformation'),
('10000000-0000-0000-0000-000000000003', 'BMW Group Plant Dingolfing',      'plant',      '10000000-0000-0000-0000-000000000001', 'Dingolfing',   'DEU', 18000,  'steady_state'),
('10000000-0000-0000-0000-000000000004', 'BMW Manufacturing Co. Spartanburg','plant',     '10000000-0000-0000-0000-000000000001', 'Spartanburg',  'USA', 11000,  'steady_state'),
('10000000-0000-0000-0000-000000000005', 'BMW Group Plant Debrecen',        'plant',      '10000000-0000-0000-0000-000000000001', 'Debrecen',     'HUN', 1500,   'ramp_up'),
('10000000-0000-0000-0000-000000000006', 'Neue Klasse Program Office',      'division',   '10000000-0000-0000-0000-000000000001', 'Munich',       'DEU', 850,    'transformation'),
('10000000-0000-0000-0000-000000000007', 'Supply Chain Management EMEA',    'division',   '10000000-0000-0000-0000-000000000001', 'Munich',       'DEU', 3200,   'transformation'),
('10000000-0000-0000-0000-000000000008', 'IT & Digital / iFACTORY',         'division',   '10000000-0000-0000-0000-000000000001', 'Munich',       'DEU', 2400,   'transformation'),
('10000000-0000-0000-0000-000000000009', 'HR Central',                      'division',   '10000000-0000-0000-0000-000000000001', 'Munich',       'DEU', 1100,   'steady_state'),
('10000000-0000-0000-0000-000000000010', 'Quality Management Central',      'division',   '10000000-0000-0000-0000-000000000001', 'Munich',       'DEU', 1800,   'steady_state'),
('10000000-0000-0000-0000-000000000011', 'EV Battery Systems',              'division',   '10000000-0000-0000-0000-000000000006', 'Munich',       'DEU', 620,    'ramp_up'),
('10000000-0000-0000-0000-000000000012', 'R&D FIZ (Forschungs- und Innovationszentrum)', 'division', '10000000-0000-0000-0000-000000000001', 'Munich', 'DEU', 9500, 'transformation'),
('10000000-0000-0000-0000-000000000013', 'BMW Motorrad',                    'division',   '10000000-0000-0000-0000-000000000001', 'Berlin',       'DEU', 3400,   'steady_state');


-- ============================================================================
-- Org Dependencies (for cascade modeling)
-- These define how failures propagate through the organization
-- ============================================================================

INSERT INTO org_dependencies (id, upstream_unit_id, downstream_unit_id, dependency_type, coupling_strength, description) VALUES

-- Neue Klasse Program → Plant Debrecen (program defines what the plant builds)
('11000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000005', 'production_flow', 0.95, 'Neue Klasse program specifications drive Debrecen plant production. Delay in program = delay in plant ramp-up.'),

-- EV Battery Systems → Neue Klasse Program (batteries are critical path for Neue Klasse)
('11000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000006', 'supply_chain', 0.90, 'Battery cell integration is on the critical path for Neue Klasse. Any battery systems leadership gap directly delays the program.'),

-- Supply Chain EMEA → Plant Munich (supply feeds production)
('11000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000002', 'supply_chain', 0.80, 'Munich plant receives 36M+ parts/day through EMEA supply chain. Disruption cascades to production within 48 hours (JIT).'),

-- Supply Chain EMEA → Plant Dingolfing
('11000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000003', 'supply_chain', 0.80, 'Dingolfing 7-series and 5-series production dependent on EMEA supply chain continuity.'),

-- Quality Central → Plant Munich (quality gates)
('11000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000002', 'quality_gate', 0.70, 'Quality Central defines standards and audit cadence for Munich. Leadership gap weakens quality enforcement.'),

-- Quality Central → Plant Spartanburg
('11000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000004', 'quality_gate', 0.70, 'Quality Central standards apply to Spartanburg X-model production.'),

-- IT & Digital → Plant Munich (iFACTORY digitalization)
('11000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000002', 'shared_resource', 0.55, 'iFACTORY digital twin and IoT infrastructure is managed by IT & Digital. Transformation stalls without digital leadership.'),

-- IT & Digital → Plant Debrecen (greenfield digital factory)
('11000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000005', 'shared_resource', 0.85, 'Debrecen is a greenfield digital-first plant. IT & Digital leadership is critical path for factory systems.'),

-- R&D FIZ → Neue Klasse Program (R&D feeds product development)
('11000000-0000-0000-0000-000000000009', '10000000-0000-0000-0000-000000000012', '10000000-0000-0000-0000-000000000006', 'production_flow', 0.75, 'FIZ research outputs (battery chemistry, SDV architecture) feed directly into Neue Klasse specifications.'),

-- Plant Munich → Quality Central (reporting dependency)
('11000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000010', 'reporting', 0.40, 'Munich plant quality data feeds central reporting. Gap in plant leadership degrades data quality.'),

-- EV Battery Systems → Plant Munich (Munich will produce some EV models)
('11000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000002', 'supply_chain', 0.65, 'Munich plant EV line depends on battery systems integration readiness.'),

-- Supply Chain EMEA → Plant Debrecen (new supply lines for greenfield)
('11000000-0000-0000-0000-000000000012', '10000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000005', 'supply_chain', 0.85, 'Debrecen requires entirely new supplier network. Supply chain leadership critical for ramp-up timeline.');
