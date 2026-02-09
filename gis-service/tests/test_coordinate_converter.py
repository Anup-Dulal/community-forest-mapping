"""
Property-based tests for coordinate conversion.
Tests correctness properties for lat/lon to UTM/UPS conversions.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import math
from src.coordinate_converter import CoordinateConverter


class TestCoordinateConverter:
    """Test suite for coordinate conversion."""

    @pytest.fixture
    def converter(self):
        """Create a coordinate converter instance."""
        return CoordinateConverter()

    # Property 13: Coordinate Conversion Round Trip
    @given(
        latitude=st.floats(min_value=-85, max_value=85),
        longitude=st.floats(min_value=-180, max_value=180)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_coordinate_conversion_round_trip(self, converter, latitude, longitude):
        """
        Property 13: Coordinate Conversion Round Trip
        For any sample plot with latitude/longitude coordinates, converting to UTM/UPS
        and back SHALL produce coordinates within 1 meter of the original coordinates.
        Validates: Requirements 8.1
        """
        # Convert to UTM
        utm_result = converter.lat_lon_to_utm(latitude, longitude)

        # Convert back to lat/lon
        latlon_result = converter.utm_to_lat_lon(
            utm_result['easting'],
            utm_result['northing'],
            utm_result['utm_zone'],
            is_southern=(latitude < 0)
        )

        # Calculate error in meters
        lat_error = abs(latlon_result['latitude'] - latitude)
        lon_error = abs(latlon_result['longitude'] - longitude)

        # Convert degree error to meters (approximate)
        # 1 degree ≈ 111 km at equator
        lat_error_m = lat_error * 111000
        lon_error_m = lon_error * 111000 * abs(math.cos(math.radians(latitude)))

        max_error_m = max(lat_error_m, lon_error_m)

        # Should be within 1 meter
        assert max_error_m <= 1.0, \
            f"Round trip error too large: {max_error_m}m for ({latitude}, {longitude})"

    @given(
        latitude=st.floats(min_value=-85, max_value=85),
        longitude=st.floats(min_value=-180, max_value=180)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_lat_lon_to_utm_conversion(self, converter, latitude, longitude):
        """Test lat/lon to UTM conversion produces valid results."""
        result = converter.lat_lon_to_utm(latitude, longitude)

        assert 'easting' in result
        assert 'northing' in result
        assert 'utm_zone' in result
        assert 'crs' in result

        # Validate UTM zone
        assert 1 <= result['utm_zone'] <= 60

        # Validate easting (should be between 167,000 and 833,000 meters)
        assert 167000 <= result['easting'] <= 833000, \
            f"Invalid easting: {result['easting']}"

        # Validate northing (should be positive)
        assert result['northing'] > 0, \
            f"Invalid northing: {result['northing']}"

    @given(
        utm_zone=st.integers(min_value=1, max_value=60),
        easting=st.floats(min_value=200000, max_value=800000),
        northing=st.floats(min_value=0, max_value=10000000),
        is_southern=st.booleans()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_utm_to_lat_lon_conversion(self, converter, utm_zone, easting, northing, is_southern):
        """Test UTM to lat/lon conversion produces valid results."""
        try:
            result = converter.utm_to_lat_lon(easting, northing, utm_zone, is_southern)

            assert 'latitude' in result
            assert 'longitude' in result

            # Validate latitude
            assert -90 <= result['latitude'] <= 90, \
                f"Invalid latitude: {result['latitude']}"

            # Validate longitude
            assert -180 <= result['longitude'] <= 180, \
                f"Invalid longitude: {result['longitude']}"

        except ValueError:
            # Some combinations may be invalid (e.g., northing too large)
            pass

    def test_lat_lon_to_utm_equator(self, converter):
        """Test conversion at equator."""
        result = converter.lat_lon_to_utm(0, 0)

        assert result['latitude'] == 0
        assert result['longitude'] == 0
        assert result['utm_zone'] == 31  # Zone 31 covers 0° longitude

    def test_lat_lon_to_utm_north_pole(self, converter):
        """Test conversion near north pole."""
        result = converter.lat_lon_to_utm(84, 0)

        assert result['latitude'] == 84
        assert result['longitude'] == 0
        assert 1 <= result['utm_zone'] <= 60

    def test_lat_lon_to_utm_south_pole(self, converter):
        """Test conversion near south pole."""
        result = converter.lat_lon_to_utm(-80, 0)

        assert result['latitude'] == -80
        assert result['longitude'] == 0
        assert 1 <= result['utm_zone'] <= 60

    def test_utm_to_lat_lon_equator(self, converter):
        """Test conversion from UTM at equator."""
        # Zone 31 at equator
        result = converter.utm_to_lat_lon(500000, 0, 31, is_southern=False)

        # Should be close to equator
        assert abs(result['latitude']) < 1
        assert abs(result['longitude']) < 1

    def test_invalid_latitude(self, converter):
        """Test that invalid latitude raises error."""
        with pytest.raises(ValueError):
            converter.lat_lon_to_utm(91, 0)

        with pytest.raises(ValueError):
            converter.lat_lon_to_utm(-91, 0)

    def test_invalid_longitude(self, converter):
        """Test that invalid longitude raises error."""
        with pytest.raises(ValueError):
            converter.lat_lon_to_utm(0, 181)

        with pytest.raises(ValueError):
            converter.lat_lon_to_utm(0, -181)

    def test_invalid_utm_zone(self, converter):
        """Test that invalid UTM zone raises error."""
        with pytest.raises(ValueError):
            converter.utm_to_lat_lon(500000, 5000000, 0, is_southern=False)

        with pytest.raises(ValueError):
            converter.utm_to_lat_lon(500000, 5000000, 61, is_southern=False)

    def test_validate_round_trip_success(self, converter):
        """Test successful round trip validation."""
        result = converter.validate_round_trip(45.5, -122.5, tolerance_meters=1.0)

        assert result['is_valid'] is True
        assert result['error_meters'] <= 1.0

    def test_validate_round_trip_with_tolerance(self, converter):
        """Test round trip validation with custom tolerance."""
        result = converter.validate_round_trip(45.5, -122.5, tolerance_meters=10.0)

        assert result['is_valid'] is True
        assert result['error_meters'] <= 10.0

    def test_batch_convert_lat_lon_to_utm(self, converter):
        """Test batch conversion of multiple coordinates."""
        coordinates = [
            (45.5, -122.5),
            (40.7, -74.0),
            (51.5, -0.1)
        ]

        results = converter.batch_convert_lat_lon_to_utm(coordinates)

        assert len(results) == 3
        for result in results:
            if 'error' not in result:
                assert 'easting' in result
                assert 'northing' in result
                assert 'utm_zone' in result

    def test_utm_zone_calculation_norway(self, converter):
        """Test UTM zone calculation for Norway exception."""
        # Norway exception: zone 32 for 56-64°N, 3-12°E
        zone = converter._calculate_utm_zone(6, 60)
        assert zone == 32

    def test_utm_zone_calculation_svalbard(self, converter):
        """Test UTM zone calculation for Svalbard exceptions."""
        # Svalbard: 72-84°N
        zone = converter._calculate_utm_zone(5, 75)
        assert zone == 31

    def test_utm_zone_calculation_standard(self, converter):
        """Test standard UTM zone calculation."""
        # Standard calculation: zone = (lon + 180) / 6 + 1
        zone = converter._calculate_utm_zone(0, 0)
        assert zone == 31

        zone = converter._calculate_utm_zone(6, 0)
        assert zone == 32

        zone = converter._calculate_utm_zone(-6, 0)
        assert zone == 30

    def test_epsg_code_northern_hemisphere(self, converter):
        """Test EPSG code for northern hemisphere."""
        epsg = converter._get_utm_epsg(31, 45)
        assert epsg == 32631  # 32600 + 31

    def test_epsg_code_southern_hemisphere(self, converter):
        """Test EPSG code for southern hemisphere."""
        epsg = converter._get_utm_epsg(31, -45)
        assert epsg == 32731  # 32700 + 31

    def test_epsg_code_from_zone_northern(self, converter):
        """Test EPSG code from zone for northern hemisphere."""
        epsg = converter._get_utm_epsg_from_zone(31, is_southern=False)
        assert epsg == 32631

    def test_epsg_code_from_zone_southern(self, converter):
        """Test EPSG code from zone for southern hemisphere."""
        epsg = converter._get_utm_epsg_from_zone(31, is_southern=True)
        assert epsg == 32731
