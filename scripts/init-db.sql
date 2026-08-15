-- Initialize database with required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- Create spatial index for better query performance
CREATE INDEX IF NOT EXISTS idx_projects_location ON projects USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_survey_points_geometry ON survey_points USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_parcels_geometry ON parcels USING GIST(geometry);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_organizations_active ON organizations(is_active);
CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_projects_organization_status ON projects(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_quotes_organization_status ON quotes(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_invoices_organization_status ON invoices(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_drone_flights_project ON drone_flights(project_id, flight_date DESC);

-- Create view for project summary statistics
CREATE OR REPLACE VIEW project_summary AS
SELECT
    p.id,
    p.organization_id,
    p.name,
    p.code,
    COUNT(DISTINCT sp.id) as survey_point_count,
    COUNT(DISTINCT par.id) as parcel_count,
    COUNT(DISTINCT df.id) as drone_flight_count,
    COALESCE(p.budget, 0) as budget,
    COALESCE(p.spent, 0) as spent
FROM projects p
LEFT JOIN survey_points sp ON p.id = sp.project_id
LEFT JOIN parcels par ON p.id = par.project_id
LEFT JOIN drone_flights df ON p.id = df.project_id
GROUP BY p.id, p.organization_id, p.name, p.code, p.budget, p.spent;

-- Log table for audit trail
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_organization ON (organization_id),
    INDEX idx_audit_created ON (created_at DESC)
);

-- Grant permissions if needed
GRANT USAGE ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
