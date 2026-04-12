-- Add hierarchical compartment support
-- This migration adds fields to support compartment/sub-compartment hierarchy

-- Add new columns to compartments table
ALTER TABLE compartments ADD COLUMN parent_compartment_id VARCHAR(255);
ALTER TABLE compartments ADD COLUMN level INTEGER DEFAULT 0;
ALTER TABLE compartments ADD COLUMN sub_compartment_number INTEGER;
ALTER TABLE compartments ADD COLUMN label VARCHAR(50);

-- Update existing compartments to have labels (C1, C2, C3, etc.)
-- This assumes compartments are ordered by creation
UPDATE compartments 
SET label = 'C' || ROW_NUMBER() OVER (PARTITION BY analysis_result_id ORDER BY id)
WHERE label IS NULL;

-- Make label NOT NULL after populating existing data
ALTER TABLE compartments ALTER COLUMN label SET NOT NULL;

-- Add indexes for performance
CREATE INDEX idx_compartment_parent ON compartments(parent_compartment_id);
CREATE INDEX idx_compartment_analysis_level ON compartments(analysis_result_id, level);
CREATE INDEX idx_compartment_label ON compartments(label);

-- Add sub-compartment reference to sample_plots
ALTER TABLE sample_plots ADD COLUMN sub_compartment_id VARCHAR(255);

-- Add foreign key constraints
-- Note: SQLite doesn't support adding foreign keys to existing tables
-- These would need to be added during table creation or via table recreation
-- For now, we'll add them as comments for documentation

-- FOREIGN KEY (parent_compartment_id) REFERENCES compartments(id) ON DELETE CASCADE
-- FOREIGN KEY (sub_compartment_id) REFERENCES compartments(id) ON DELETE SET NULL
