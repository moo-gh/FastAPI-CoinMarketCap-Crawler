-- Create api_tokens table
CREATE TABLE IF NOT EXISTS api_tokens (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on token for faster lookups
CREATE INDEX IF NOT EXISTS idx_api_tokens_token ON api_tokens(token);
CREATE INDEX IF NOT EXISTS idx_api_tokens_name ON api_tokens(name);

-- Insert some sample API tokens
INSERT INTO api_tokens (name, token) VALUES 
    ('admin', 'admin-token-123456'),
    ('mobile-app', 'mobile-app-secret-789'),
    ('web-dashboard', 'web-dashboard-token-abc'),
    ('monitoring-service', 'monitoring-service-xyz-999')
ON CONFLICT (name) DO NOTHING;