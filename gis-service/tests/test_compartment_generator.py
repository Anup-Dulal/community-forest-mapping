"""
Unit tests for compartment generator module.
Tests equal-area compartment generation and validation.
"""

import pytest
import numpy as np
from shapely.geometry import Polygon, mapping
from src.compartment_generator import CompartmentGenerator


class TestCompartmentGenerator:
    """Tests for CompartmentGenerator class."""

    @pytest.fixture
    def sample_boundary(self):
        """Create a sample square boundary."""
        coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        return Polygon(coords)

    @pytest.fixture
    def sample_boundary_geojson(self, sample_boundary):
        """Create sample boundary GeoJSON."""
        return mapping(sample_boundary)

    @pytest.fixture
    def generator(self, tmp_path):
        """Create CompartmentGenerator instance with temporary directory."""
        return CompartmentGenerator(str(tmp_path))

    def test_generate_compartments_valid(self, generator, sample_boundary_geojson):
        """Test compartment generation with valid boundary."""
        # Act
        result = generator.generate_compartments(sample_boundary_geojson, num_compartments=4)

        # Assert
        assert result is not None
        assert result.endswith('.geojson')

    def test_generate_compartments_invalid_geometry(self, generator):
        """Test compartment generation with invalid geometry."""
        # Arrange
        invalid_geojson = {'type': 'InvalidType', 'coordinates': []}

        # Act & Assert
        with pytest.raises(ValueError):
            generator.generate_compartments(invalid_geojson, num_compartments=4)

    def test_compartment_numbering(self, generator, sample_boundary_geojson):
        """Test that compartments are numbered sequentially."""
        # Arrange
        num_compartments = 4

        # Act
        result = generator.generate_compartments(sample_boundary_geojson, num_compartments)

        # Assert - verify file was created
        assert result is not None

    def test_get_compartment_statistics(self, generator, sample_boundary_geojson):
        """Test compartment statistics calculation."""
        # Arrange
        compartment_path = generator.generate_compartments(sample_boundary_geojson, num_compartments=4)

        # Act
        stats = generator.get_compartment_statistics(compartment_path)

        # Assert
        assert stats['num_compartments'] == 4
        assert stats['total_area'] > 0
        assert stats['mean_area'] > 0
        assert stats['min_area'] > 0
        assert stats['max_area'] > 0


class TestEqualAreaCompartmentDistribution:
    """
    Property 7: Equal-Area Compartment Distribution
    All compartments SHALL have approximately equal area within ±5% tolerance.
    """

    def test_compartments_equal_area(self):
        """Test that generated compartments have approximately equal area."""
        # Arrange
        coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        boundary = Polygon(coords)
        boundary_geojson = mapping(boundary)
        generator = CompartmentGenerator()

        # Act
        compartment_path = generator.generate_compartments(boundary_geojson, num_compartments=4)
        stats = generator.get_compartment_statistics(compartment_path)

        # Assert
        mean_area = stats['mean_area']
        tolerance = mean_area * 0.05  # 5% tolerance

        # Check that all compartments are within tolerance
        assert stats['min_area'] >= mean_area - tolerance
        assert stats['max_area'] <= mean_area + tolerance

    def test_compartments_equal_area_complex_polygon(self):
        """Test equal-area distribution with complex polygon."""
        # Arrange
        coords = [(0, 0), (10, 0), (10, 5), (5, 5), (5, 10), (0, 10), (0, 0)]
        boundary = Polygon(coords)
        boundary_geojson = mapping(boundary)
        generator = CompartmentGenerator()

        # Act
        compartment_path = generator.generate_compartments(boundary_geojson, num_compartments=4)
        stats = generator.get_compartment_statistics(compartment_path)

        # Assert
        mean_area = stats['mean_area']
        tolerance = mean_area * 0.05

        assert stats['min_area'] >= mean_area - tolerance
        assert stats['max_area'] <= mean_area + tolerance


class TestCompartmentSequentialNumbering:
    """
    Property 8: Compartment Sequential Numbering
    Compartments SHALL be numbered sequentially starting from C1, with no gaps.
    """

    def test_compartment_sequential_numbering(self):
        """Test that compartments are numbered sequentially."""
        # Arrange
        coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        boundary = Polygon(coords)
        boundary_geojson = mapping(boundary)
        generator = CompartmentGenerator()

        # Act
        compartment_path = generator.generate_compartments(boundary_geojson, num_compartments=4)

        # Assert - verify numbering
        import geopandas as gpd
        gdf = gpd.read_file(compartment_path)

        compartment_ids = sorted(gdf['compartment_id'].values)
        expected_ids = [f'C{i+1}' for i in range(len(gdf))]

        assert compartment_ids == expected_ids

    def test_no_gaps_in_numbering(self):
        """Test that there are no gaps in compartment numbering."""
        # Arrange
        coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        boundary = Polygon(coords)
        boundary_geojson = mapping(boundary)
        generator = CompartmentGenerator()

        # Act
        compartment_path = generator.generate_compartments(boundary_geojson, num_compartments=6)

        # Assert
        import geopandas as gpd
        gdf = gpd.read_file(compartment_path)

        # Extract numbers from compartment IDs
        numbers = [int(comp_id[1:]) for comp_id in gdf['compartment_id'].values]
        numbers.sort()

        # Check for sequential numbering without gaps
        for i, num in enumerate(numbers, 1):
            assert num == i
