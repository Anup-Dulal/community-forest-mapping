"""
Unit tests for GoogleEarthEngineClient
Tests satellite imagery, elevation data, NDVI, and EVI fetching with fallback support
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.google_earth_engine_client import GoogleEarthEngineClient


@pytest.fixture
def sample_geometry():
    """Sample GeoJSON geometry for testing."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [0, 0],
                [1, 0],
                [1, 1],
                [0, 1],
                [0, 0]
            ]
        ]
    }


@pytest.fixture
def gee_client():
    """Create a GoogleEarthEngineClient instance for testing."""
    with patch('src.google_earth_engine_client.ee'):
        client = GoogleEarthEngineClient()
        client.ee_initialized = True
        return client


class TestGoogleEarthEngineClient:
    """Test suite for GoogleEarthEngineClient."""

    def test_initialization(self):
        """Test client initialization."""
        with patch('src.google_earth_engine_client.ee'):
            client = GoogleEarthEngineClient()
            assert client.rate_limit_delay == 0.1
            assert client.max_retries == 3
            assert client.retry_delay == 1.0

    def test_fetch_satellite_imagery_success(self, gee_client, sample_geometry):
        """Test successful satellite imagery fetch."""
        with patch('src.google_earth_engine_client.ee') as mock_ee:
            # Mock the EE API calls
            mock_image = MagicMock()
            mock_image.getInfo.return_value = {
                'properties': {'system:time_start': 1609459200000}
            }
            mock_image.getMapId.return_value = {
                'tile_fetcher': MagicMock(url_format='https://example.com/tiles/{z}/{x}/{y}')
            }

            mock_collection = MagicMock()
            mock_collection.first.return_value = mock_image

            mock_ee.ImageCollection.return_value.filterBounds.return_value.filterDate.return_value.filter.return_value = mock_collection
            mock_ee.Geometry.return_value = MagicMock()
            mock_ee.Image.return_value = mock_image

            gee_client.ee_initialized = True
            result = gee_client.fetch_satellite_imagery(sample_geometry)

            assert result is not None
            assert result['status'] == 'success'
            assert 'source' in result
            assert 'tile_url' in result

    def test_fetch_satellite_imagery_fallback(self, gee_client, sample_geometry):
        """Test satellite imagery fetch with fallback."""
        gee_client.ee_initialized = False
        result = gee_client.fetch_satellite_imagery(sample_geometry)

        assert result is not None
        assert result['status'] == 'fallback'
        assert 'source' in result

    def test_fetch_elevation_data_success(self, gee_client, sample_geometry):
        """Test successful elevation data fetch."""
        with patch('src.google_earth_engine_client.ee') as mock_ee:
            # Mock the EE API calls
            mock_dem = MagicMock()
            mock_dem.clip.return_value.reduceRegion.return_value.getInfo.return_value = {
                'elevation_min': 100,
                'elevation_max': 2000,
                'elevation_mean': 1000
            }

            mock_ee.Image.return_value = mock_dem
            mock_ee.Geometry.return_value = MagicMock()
            mock_ee.Reducer.minMax.return_value.combine.return_value = MagicMock()

            gee_client.ee_initialized = True
            result = gee_client.fetch_elevation_data(sample_geometry)

            assert result is not None
            assert result['status'] == 'success'
            assert 'min_elevation' in result
            assert 'max_elevation' in result
            assert 'mean_elevation' in result

    def test_fetch_elevation_data_fallback(self, gee_client, sample_geometry):
        """Test elevation data fetch with fallback."""
        gee_client.ee_initialized = False
        result = gee_client.fetch_elevation_data(sample_geometry)

        assert result is not None
        assert result['status'] == 'fallback'
        assert 'source' in result

    def test_calculate_ndvi_success(self, gee_client, sample_geometry):
        """Test successful NDVI calculation."""
        with patch('src.google_earth_engine_client.ee') as mock_ee:
            # Mock the EE API calls
            mock_image = MagicMock()
            mock_ndvi = MagicMock()
            mock_ndvi.clip.return_value.reduceRegion.return_value.getInfo.return_value = {
                'NDVI_min': -0.5,
                'NDVI_max': 0.8,
                'NDVI_mean': 0.4,
                'NDVI_stdDev': 0.2
            }
            mock_ndvi.getMapId.return_value = {
                'tile_fetcher': MagicMock(url_format='https://example.com/tiles/{z}/{x}/{y}')
            }

            mock_image.normalizedDifference.return_value = mock_ndvi
            mock_collection = MagicMock()
            mock_collection.first.return_value = mock_image

            mock_ee.ImageCollection.return_value.filterBounds.return_value.filterDate.return_value.filter.return_value = mock_collection
            mock_ee.Geometry.return_value = MagicMock()
            mock_ee.Image.return_value = mock_ndvi
            mock_ee.Reducer.minMax.return_value.combine.return_value = MagicMock()

            gee_client.ee_initialized = True
            result = gee_client.calculate_ndvi(sample_geometry)

            assert result is not None
            assert result['status'] == 'success'
            assert result['index'] == 'NDVI'
            assert 'min' in result
            assert 'max' in result
            assert 'mean' in result

    def test_calculate_ndvi_fallback(self, gee_client, sample_geometry):
        """Test NDVI calculation with fallback."""
        gee_client.ee_initialized = False
        result = gee_client.calculate_ndvi(sample_geometry)

        assert result is not None
        assert result['status'] == 'fallback'
        assert result['index'] == 'NDVI'

    def test_calculate_evi_success(self, gee_client, sample_geometry):
        """Test successful EVI calculation."""
        with patch('src.google_earth_engine_client.ee') as mock_ee:
            # Mock the EE API calls
            mock_image = MagicMock()
            mock_evi = MagicMock()
            mock_evi.clip.return_value.reduceRegion.return_value.getInfo.return_value = {
                'EVI_min': -0.5,
                'EVI_max': 0.8,
                'EVI_mean': 0.4,
                'EVI_stdDev': 0.2
            }
            mock_evi.getMapId.return_value = {
                'tile_fetcher': MagicMock(url_format='https://example.com/tiles/{z}/{x}/{y}')
            }

            mock_image.select.return_value.divide.return_value = MagicMock()
            mock_collection = MagicMock()
            mock_collection.first.return_value = mock_image

            mock_ee.ImageCollection.return_value.filterBounds.return_value.filterDate.return_value.filter.return_value = mock_collection
            mock_ee.Geometry.return_value = MagicMock()
            mock_ee.Image.return_value = mock_evi
            mock_ee.Reducer.minMax.return_value.combine.return_value = MagicMock()

            gee_client.ee_initialized = True
            result = gee_client.calculate_evi(sample_geometry)

            assert result is not None
            assert result['status'] == 'success'
            assert result['index'] == 'EVI'
            assert 'min' in result
            assert 'max' in result
            assert 'mean' in result

    def test_calculate_evi_fallback(self, gee_client, sample_geometry):
        """Test EVI calculation with fallback."""
        gee_client.ee_initialized = False
        result = gee_client.calculate_evi(sample_geometry)

        assert result is not None
        assert result['status'] == 'fallback'
        assert result['index'] == 'EVI'

    def test_rate_limiting(self, gee_client):
        """Test that rate limiting delay is applied."""
        assert gee_client.rate_limit_delay == 0.1
        assert gee_client.max_retries == 3
        assert gee_client.retry_delay == 1.0

    def test_fallback_satellite_imagery(self, gee_client, sample_geometry):
        """Test fallback satellite imagery."""
        result = gee_client._fallback_satellite_imagery(sample_geometry)

        assert result['status'] == 'fallback'
        assert 'source' in result
        assert 'tile_url' in result

    def test_fallback_elevation_data(self, gee_client, sample_geometry):
        """Test fallback elevation data."""
        result = gee_client._fallback_elevation_data(sample_geometry)

        assert result['status'] == 'fallback'
        assert 'source' in result

    def test_fallback_ndvi(self, gee_client, sample_geometry):
        """Test fallback NDVI."""
        result = gee_client._fallback_ndvi(sample_geometry)

        assert result['status'] == 'fallback'
        assert result['index'] == 'NDVI'
        assert 'min' in result
        assert 'max' in result

    def test_fallback_evi(self, gee_client, sample_geometry):
        """Test fallback EVI."""
        result = gee_client._fallback_evi(sample_geometry)

        assert result['status'] == 'fallback'
        assert result['index'] == 'EVI'
        assert 'min' in result
        assert 'max' in result
