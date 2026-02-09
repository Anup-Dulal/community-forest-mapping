-- Shapefile table
CREATE TABLE IF NOT EXISTS shapefiles (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    filename VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geometry TEXT,
    bounding_box TEXT,
    projection VARCHAR(50),
    status VARCHAR(50) DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shapefiles_user_id ON shapefiles(user_id);
CREATE INDEX IF NOT EXISTS idx_shapefiles_status ON shapefiles(status);

-- DEM table
CREATE TABLE IF NOT EXISTS dems (
    id TEXT PRIMARY KEY,
    shapefile_id TEXT NOT NULL REFERENCES shapefiles(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL,
    downloaded_at TIMESTAMP,
    raster_path VARCHAR(500),
    clipped_raster_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'downloading',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dems_shapefile_id ON dems(shapefile_id);
CREATE INDEX IF NOT EXISTS idx_dems_status ON dems(status);

-- Analysis Result table
CREATE TABLE IF NOT EXISTS analysis_results (
    id TEXT PRIMARY KEY,
    shapefile_id TEXT NOT NULL REFERENCES shapefiles(id) ON DELETE CASCADE,
    dem_id TEXT REFERENCES dems(id) ON DELETE SET NULL,
    slope_raster_path VARCHAR(500),
    aspect_raster_path VARCHAR(500),
    compartment_geometry_path VARCHAR(500),
    sample_plot_geometry_path VARCHAR(500),
    generated_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analysis_results_shapefile_id ON analysis_results(shapefile_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_dem_id ON analysis_results(dem_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_status ON analysis_results(status);

-- Compartment table
CREATE TABLE IF NOT EXISTS compartments (
    id TEXT PRIMARY KEY,
    analysis_result_id TEXT NOT NULL REFERENCES analysis_results(id) ON DELETE CASCADE,
    compartment_id VARCHAR(50) NOT NULL,
    area NUMERIC(15, 2),
    geometry TEXT,
    sample_plot_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_compartments_analysis_result_id ON compartments(analysis_result_id);
CREATE INDEX IF NOT EXISTS idx_compartments_compartment_id ON compartments(compartment_id);

-- Sample Plot table
CREATE TABLE IF NOT EXISTS sample_plots (
    id TEXT PRIMARY KEY,
    analysis_result_id TEXT NOT NULL REFERENCES analysis_results(id) ON DELETE CASCADE,
    compartment_id TEXT NOT NULL REFERENCES compartments(id) ON DELETE CASCADE,
    plot_id VARCHAR(50) NOT NULL,
    easting NUMERIC(15, 2),
    northing NUMERIC(15, 2),
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6),
    geometry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sample_plots_analysis_result_id ON sample_plots(analysis_result_id);
CREATE INDEX IF NOT EXISTS idx_sample_plots_compartment_id ON sample_plots(compartment_id);
CREATE INDEX IF NOT EXISTS idx_sample_plots_plot_id ON sample_plots(plot_id);

-- Session table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    shapefile_id TEXT REFERENCES shapefiles(id) ON DELETE SET NULL,
    analysis_result_id TEXT REFERENCES analysis_results(id) ON DELETE SET NULL,
    session_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_shapefile_id ON sessions(shapefile_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    action VARCHAR(255),
    entity_type VARCHAR(100),
    entity_id TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
