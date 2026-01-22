-- Cin7 Docket Receiver Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Uploads table
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_uploads_user_id ON uploads(user_id);
CREATE INDEX idx_uploads_created_at ON uploads(created_at);

-- Extractions table
CREATE TABLE IF NOT EXISTS extractions (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL REFERENCES uploads(id) ON DELETE CASCADE,
    raw_text TEXT,
    parsed_json JSONB,
    confidence NUMERIC(5,2),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_extractions_upload_id ON extractions(upload_id);
CREATE INDEX idx_extractions_parsed_json ON extractions USING GIN(parsed_json);

-- Receipts table
CREATE TABLE IF NOT EXISTS receipts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cin7_po_id VARCHAR(100),
    cin7_po_reference VARCHAR(255),
    docket_number VARCHAR(255),
    supplier_name VARCHAR(255),
    delivery_date DATE,
    receipt_payload_json JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'duplicate'))
);

CREATE INDEX idx_receipts_user_id ON receipts(user_id);
CREATE INDEX idx_receipts_cin7_po_reference ON receipts(cin7_po_reference);
CREATE INDEX idx_receipts_docket_number ON receipts(docket_number);
CREATE INDEX idx_receipts_status ON receipts(status);
CREATE INDEX idx_receipts_created_at ON receipts(created_at);
CREATE UNIQUE INDEX idx_receipts_duplicate_check ON receipts(supplier_name, docket_number)
    WHERE status = 'completed';

-- Receipt lines table
CREATE TABLE IF NOT EXISTS receipt_lines (
    id SERIAL PRIMARY KEY,
    receipt_id INTEGER NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    sku VARCHAR(255),
    description TEXT,
    qty_delivered NUMERIC(10,2) NOT NULL,
    qty_receipted NUMERIC(10,2),
    unit VARCHAR(50),
    match_type VARCHAR(50) NOT NULL,
    cin7_line_id VARCHAR(100),
    cin7_product_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_match_type CHECK (match_type IN ('exact', 'fuzzy', 'manual', 'unmatched'))
);

CREATE INDEX idx_receipt_lines_receipt_id ON receipt_lines(receipt_id);
CREATE INDEX idx_receipt_lines_sku ON receipt_lines(sku);
CREATE INDEX idx_receipt_lines_match_type ON receipt_lines(match_type);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_receipts_updated_at BEFORE UPDATE ON receipts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
