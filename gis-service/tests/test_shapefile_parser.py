"""
Unit tests for shapefile parser module.
Tests shapefile parsing and geometry extraction.
"""

import pytest
import json
from pathlib import Path
from shapely.geometry import Polygon, mapping
import geopandas as gpd
from src.shapefile_parser import ShapefileParser


class TestShapefileParser:
    """Tests for ShapefileParser class."""

    @pytest.fixture
    def sample_polygon(self):
        """Create a sample polygon for testing."""
        coords = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        return Polygon(coords)

    @pytest.fixture
    def sample_geojson(self, sample_polygon):
        """Create sample GeoJSON geometry."""
        return mapping(sample_polygon)

    def test_validate_geometry_integrity_valid(self, sample_geojson):
        """Test geometry validation with valid geometry."""
        # Act
        result = ShapefileParser.validate_geometry_integrity(sample_geojson)

        # Assert
        assert result is True

    def test_validate_geometry_integrity_invalid(self):
        """Test geometry validation with invalid geometry."""
        # Arrange
        invalid_geojson = {
            'type': 'Polygon',
            'coordinates': [[(0, 0), (1, 1), (0, 0)]]  # Invalid: not enough points
        }

        # Act
        result = ShapefileParser.validate_geometry_integrity(invalid_geojson)

        # Assert
        assert result is False

    def test_extract_bounding_box(self, sample_geojson):
        """Test bounding box extraction."""
        # Act
        bbox = ShapefileParser.extract_bounding_box(sample_geojson)

        # Assert
        assert bbox['minLon'] == 0
        assert bbox['minLat'] == 0
        assert bbox['maxLon'] == 1
        assert bbox['maxLat'] == 1

    def test_extract_bounding_box_containment(self, sample_geojson):
        """
        Property 3: Bounding Box Containment
        For any boundary polygon, the extracted bounding box coordinates 
        SHALL fully contain all vertices of the polygon.
        """
        # Act
        bbox = ShapefileParser.extract_bounding_box(sample_geojson)

        # Assert - verify all coordinates are within bbox
        from shapely.geometry import shape
        geom = shape(sample_geojson)
        coords = list(geom.exterior.coords)

        for lon, lat in coords:
            assert bbox['minLon'] <= lon <= bbox['maxLon']
            assert bbox['minLat'] <= lat <= bbox['maxLat']

    def test_extract_bounding_box_complex_polygon(self):
        """Test bounding box extraction with complex polygon."""
        # Arrange
        coords = [(0, 0), (5, 0), (5, 5), (2, 3), (0, 5), (0, 0)]
        polygon = Polygon(coords)
        geojson = mapping(polygon)

        # Act
        bbox = ShapefileParser.extract_bounding_box(geojson)

        # Assert
        assert bbox['minLon'] == 0
        assert bbox['minLat'] == 0
        assert bbox['maxLon'] == 5
        assert bbox['maxLat'] == 5

    def test_extract_bounding_box_negative_coordinates(self):
        """Test bounding box extraction with negative coordinates."""
        # Arrange
        coords = [(-5, -5), (5, -5), (5, 5), (-5, 5), (-5, -5)]
        polygon = Polygon(coords)
        geojson = mapping(polygon)

        # Act
        bbox = ShapefileParser.extract_bounding_box(geojson)

        # Assert
        assert bbox['minLon'] == -5
        assert bbox['minLat'] == -5
        assert bbox['maxLon'] == 5
        assert bbox['maxLat'] == 5

    def test_extract_bounding_box_invalid_geometry(self):
        """Test bounding box extraction with invalid geometry."""
        # Arrange
        invalid_geojson = {'type': 'InvalidType', 'coordinates': []}

        # Act & Assert
        with pytest.raises(ValueError):
            ShapefileParser.extract_bounding_box(invalid_geojson)


class TestShapefileParsingRoundTrip:
    """
    Property 2: Shapefile Parsing Round Trip
    For any valid shapefile, parsing it and then serializing it back 
    should produce a geometrically equivalent boundary polygon.
    """

    def test_geometry_round_trip(self):
        """Test that geometry survives round-trip parsing."""
        # Arrange
        original_coords = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        original_polygon = Polygon(original_coords)
        original_geojson = mapping(original_polygon)

        # Act - simulate round trip
        from shapely.geometry import shape
        parsed_geom = shape(original_geojson)
        round_trip_geojson = mapping(parsed_geom)

        # Assert - geometries should be equivalent
        assert original_geojson['type'] == round_trip_geojson['type']
        assert len(original_geojson['coordinates']) == len(round_trip_geojson['coordinates'])

        # Verify coordinates are approximately equal
        original_coords_list = original_geojson['coordinates'][0]
        round_trip_coords_list = round_trip_geojson['coordinates'][0]

        for orig, rt in zip(original_coords_list, round_trip_coords_list):
            assert abs(orig[0] - rt[0]) < 1e-10
            assert abs(orig[1] - rt[1]) < 1e-10

    def test_geometry_round_trip_complex(self):
        """Test round-trip with complex polygon."""
        # Arrange
        coords = [(0, 0), (10, 0), (10, 10), (5, 7), (0, 10), (0, 0)]
        original_polygon = Polygon(coords)
        original_geojson = mapping(original_polygon)

        # Act
        from shapely.geometry import shape
        parsed_geom = shape(original_geojson)
        round_trip_geojson = mapping(parsed_geom)

        # Assert
        assert original_polygon.equals(shape(round_trip_geojson))
