"""
Property-based tests for sample plot generation.
Tests correctness properties for sample plot constraints and distribution.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import geopandas as gpd
from shapely.geometry import Polygon, Point, box
import tempfile
import os
import json
from src.sample_plot_generator import SamplePlotGenerator


class TestSamplePlotGenerator:
    """Test suite for sample plot generation."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_compartment_file(self, temp_dir):
        """Create a sample compartment GeoJSON file for testing."""
        # Create 4 equal compartments
        compartments = [
            {
                'type': 'Feature',
                'properties': {'compartment_id': 'C1'},
                'geometry': box(0, 0, 50, 50).__geo_interface__
            },
            {
                'type': 'Feature',
                'properties': {'compartment_id': 'C2'},
                'geometry': box(50, 0, 100, 50).__geo_interface__
            },
            {
                'type': 'Feature',
                'properties': {'compartment_id': 'C3'},
                'geometry': box(0, 50, 50, 100).__geo_interface__
            },
            {
                'type': 'Feature',
                'properties': {'compartment_id': 'C4'},
                'geometry': box(50, 50, 100, 100).__geo_interface__
            }
        ]

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(compartments, crs='EPSG:4326')

        # Save to file
        filepath = os.path.join(temp_dir, 'compartments.geojson')
        gdf.to_file(filepath, driver='GeoJSON')

        return filepath

    # Property 9: Sample Plot Minimum Constraint
    @given(
        num_compartments=st.integers(min_value=1, max_value=10),
        compartment_size=st.integers(min_value=1000, max_value=100000)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_sample_plot_minimum_constraint(self, temp_dir, num_compartments, compartment_size):
        """
        Property 9: Sample Plot Minimum Constraint
        For any compartment, the number of generated sample plots SHALL be at least 5.
        Validates: Requirements 7.3
        """
        # Create compartments
        compartments = []
        for i in range(num_compartments):
            x_offset = i * (compartment_size ** 0.5)
            compartments.append({
                'type': 'Feature',
                'properties': {'compartment_id': f'C{i+1}'},
                'geometry': box(x_offset, 0, x_offset + (compartment_size ** 0.5), compartment_size ** 0.5).__geo_interface__
            })

        gdf = gpd.GeoDataFrame.from_features(compartments, crs='EPSG:4326')
        filepath = os.path.join(temp_dir, f'compartments_{num_compartments}.geojson')
        gdf.to_file(filepath, driver='GeoJSON')

        # Generate sample plots
        generator = SamplePlotGenerator(temp_dir)
        sample_plot_path = generator.generate_sample_plots(
            filepath,
            sampling_intensity=0.02,
            min_plots_per_compartment=5,
            distribution_method='systematic'
        )

        # Verify minimum constraint
        gdf_plots = gpd.read_file(sample_plot_path)
        plots_per_compartment = gdf_plots.groupby('compartment_id').size()

        # Each compartment should have at least 5 plots
        assert all(plots_per_compartment >= 5), \
            f"Some compartments have fewer than 5 plots: {plots_per_compartment.to_dict()}"

    # Property 10: Sample Plot Sampling Intensity
    @given(
        compartment_area=st.integers(min_value=10000, max_value=1000000),
        sampling_intensity=st.floats(min_value=0.01, max_value=0.05)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_sample_plot_sampling_intensity(self, temp_dir, compartment_area, sampling_intensity):
        """
        Property 10: Sample Plot Sampling Intensity
        For any compartment with area A, the number of generated sample plots SHALL be
        approximately equal to max(5, A × 0.02), where 0.02 represents 2% sampling intensity.
        Validates: Requirements 7.2
        """
        # Create a single compartment with specified area
        side_length = int(compartment_area ** 0.5)
        compartment = {
            'type': 'Feature',
            'properties': {'compartment_id': 'C1'},
            'geometry': box(0, 0, side_length, side_length).__geo_interface__
        }

        gdf = gpd.GeoDataFrame.from_features([compartment], crs='EPSG:4326')
        filepath = os.path.join(temp_dir, 'compartment_intensity.geojson')
        gdf.to_file(filepath, driver='GeoJSON')

        # Generate sample plots
        generator = SamplePlotGenerator(temp_dir)
        sample_plot_path = generator.generate_sample_plots(
            filepath,
            sampling_intensity=sampling_intensity,
            min_plots_per_compartment=5,
            distribution_method='systematic'
        )

        # Verify sampling intensity
        gdf_plots = gpd.read_file(sample_plot_path)
        actual_plots = len(gdf_plots)

        # Expected plots = max(5, area_hectares * sampling_intensity)
        area_hectares = compartment_area / 10000
        expected_plots = max(5, int(round(area_hectares * sampling_intensity)))

        # Allow 20% tolerance
        tolerance = max(1, int(expected_plots * 0.2))
        assert abs(actual_plots - expected_plots) <= tolerance, \
            f"Sampling intensity mismatch: expected ~{expected_plots}, got {actual_plots}"

    # Property 11: Sample Plot Boundary Constraint
    @given(
        num_compartments=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_sample_plot_boundary_constraint(self, temp_dir, num_compartments):
        """
        Property 11: Sample Plot Boundary Constraint
        For any sample plot, its location SHALL be within the boundary of its assigned compartment.
        Validates: Requirements 7.4
        """
        # Create compartments
        compartments = []
        for i in range(num_compartments):
            x_offset = i * 100
            compartments.append({
                'type': 'Feature',
                'properties': {'compartment_id': f'C{i+1}'},
                'geometry': box(x_offset, 0, x_offset + 100, 100).__geo_interface__
            })

        gdf_compartments = gpd.GeoDataFrame.from_features(compartments, crs='EPSG:4326')
        filepath = os.path.join(temp_dir, f'compartments_boundary_{num_compartments}.geojson')
        gdf_compartments.to_file(filepath, driver='GeoJSON')

        # Generate sample plots
        generator = SamplePlotGenerator(temp_dir)
        sample_plot_path = generator.generate_sample_plots(
            filepath,
            sampling_intensity=0.02,
            min_plots_per_compartment=5,
            distribution_method='systematic'
        )

        # Verify boundary constraint
        gdf_plots = gpd.read_file(sample_plot_path)

        for idx, plot in gdf_plots.iterrows():
            compartment_id = plot['compartment_id']
            plot_geometry = plot.geometry

            # Find corresponding compartment
            compartment = gdf_compartments[gdf_compartments['compartment_id'] == compartment_id].iloc[0]
            compartment_geometry = compartment.geometry

            # Verify plot is within compartment
            assert compartment_geometry.contains(plot_geometry), \
                f"Plot {plot['plot_id']} is outside its compartment {compartment_id}"

    # Property 12: Sample Plot Unique Labeling
    @given(
        num_compartments=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_sample_plot_unique_labeling(self, temp_dir, num_compartments):
        """
        Property 12: Sample Plot Unique Labeling
        For any set of generated sample plots, each plot SHALL have a unique sequential
        identifier (SP-01, SP-02, etc.) with no gaps or duplicates.
        Validates: Requirements 7.5
        """
        # Create compartments
        compartments = []
        for i in range(num_compartments):
            x_offset = i * 100
            compartments.append({
                'type': 'Feature',
                'properties': {'compartment_id': f'C{i+1}'},
                'geometry': box(x_offset, 0, x_offset + 100, 100).__geo_interface__
            })

        gdf = gpd.GeoDataFrame.from_features(compartments, crs='EPSG:4326')
        filepath = os.path.join(temp_dir, f'compartments_labeling_{num_compartments}.geojson')
        gdf.to_file(filepath, driver='GeoJSON')

        # Generate sample plots
        generator = SamplePlotGenerator(temp_dir)
        sample_plot_path = generator.generate_sample_plots(
            filepath,
            sampling_intensity=0.02,
            min_plots_per_compartment=5,
            distribution_method='systematic'
        )

        # Verify unique labeling
        gdf_plots = gpd.read_file(sample_plot_path)
        plot_ids = gdf_plots['plot_id'].tolist()

        # Check for duplicates
        assert len(plot_ids) == len(set(plot_ids)), \
            f"Duplicate plot IDs found: {plot_ids}"

        # Check for sequential numbering (SP-01, SP-02, etc.)
        expected_ids = [f"SP-{i:02d}" for i in range(1, len(plot_ids) + 1)]
        assert plot_ids == expected_ids, \
            f"Plot IDs are not sequential. Expected {expected_ids}, got {plot_ids}"

    def test_sample_plot_generation_basic(self, temp_dir, sample_compartment_file):
        """Basic test for sample plot generation."""
        generator = SamplePlotGenerator(temp_dir)
        sample_plot_path = generator.generate_sample_plots(
            sample_compartment_file,
            sampling_intensity=0.02,
            min_plots_per_compartment=5,
            distribution_method='systematic'
        )

        assert os.path.exists(sample_plot_path)
        gdf = gpd.read_file(sample_plot_path)
        assert len(gdf) > 0
        assert 'plot_id' in gdf.columns
        assert 'compartment_id' in gdf.columns

    def test_sample_plot_statistics(self, temp_dir, sample_compartment_file):
        """Test sample plot statistics calculation."""
        generator = SamplePlotGenerator(temp_dir)
        sample_plot_path = generator.generate_sample_plots(
            sample_compartment_file,
            sampling_intensity=0.02,
            min_plots_per_compartment=5,
            distribution_method='systematic'
        )

        stats = generator.get_sample_plot_statistics(sample_plot_path)

        assert 'total_plots' in stats
        assert 'plots_per_compartment' in stats
        assert 'min_plots' in stats
        assert 'max_plots' in stats
        assert 'avg_plots' in stats
        assert stats['total_plots'] > 0
        assert stats['min_plots'] >= 5

    def test_random_distribution(self, temp_dir, sample_compartment_file):
        """Test random distribution method."""
        generator = SamplePlotGenerator(temp_dir)
        sample_plot_path = generator.generate_sample_plots(
            sample_compartment_file,
            sampling_intensity=0.02,
            min_plots_per_compartment=5,
            distribution_method='random'
        )

        assert os.path.exists(sample_plot_path)
        gdf = gpd.read_file(sample_plot_path)
        assert len(gdf) > 0
