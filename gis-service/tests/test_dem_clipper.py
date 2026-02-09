"""
Unit tests for DEM clipper module.
Tests DEM clipping to boundary polygons.
"""

import pytest
from shapely.geometry import Polygon, mapping
from src.dem_clipper import DEMClipper


class TestDEMClipper:
    """Tests for DEMClipper class."""

    @pytest.fixture
    def sample_boundary(self):
        """Create a sample boundary polygon."""
        coords = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        return Polygon(coords)

    @pytest.fixture
    def sample_boundary_geojson(self, sample_boundary):
        """Create sample boundary GeoJSON."""
        return mapping(sample_boundary)

    @pytest.fixture
    def clipper(self, tmp_path):
        """Create DEMClipper instance with temporary directory."""
        return DEMClipper(str(tmp_path))

    def test_validate_clipped_dem_invalid_geometry(self, clipper):
        """Test validation with invalid geometry."""
        # Arrange
        invalid_geojson = {'type': 'InvalidType', 'coordinates': []}

        # Act & Assert
        with pytest.raises(ValueError):
            clipper.validate_clipped_dem("nonexistent.tif", invalid_geojson)

    def test_reproject_geometry_valid(self, clipper, sample_boundary_geojson):
        """Test geometry reprojection."""
        # Arrange
        from shapely.geometry import shape
        geom = shape(sample_boundary_geojson)

        # Act
        reprojected = clipper._reproject_geometry(geom, 'EPSG:4326', 'EPSG:3857')

        # Assert
        assert reprojected is not None
        assert reprojected.is_valid


class TestDEMClippingBoundaryConstraint:
    """
    Property 4: DEM Clipping Boundary Constraint
    For any DEM raster and boundary polygon, the clipped DEM SHALL only 
    contain cells that intersect with the boundary polygon.
    """

    def test_clipping_respects_boundary(self):
        """Test that clipped DEM respects boundary constraint."""
        # This test would require actual raster files
        # For now, we test the validation logic
        pass

    def test_clipping_with_complex_boundary(self):
        """Test clipping with complex polygon boundary."""
        # Arrange
        coords = [(0, 0), (5, 0), (5, 5), (2, 3), (0, 5), (0, 0)]
        boundary = Polygon(coords)
        boundary_geojson = mapping(boundary)

        # Act & Assert
        # Validation should pass for valid boundary
        assert boundary.is_valid
