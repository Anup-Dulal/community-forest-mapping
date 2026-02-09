"""
Unit tests for slope calculator module.
Tests slope calculation and classification.
"""

import pytest
import numpy as np
from src.slope_calculator import SlopeCalculator


class TestSlopeCalculator:
    """Tests for SlopeCalculator class."""

    @pytest.fixture
    def calculator(self, tmp_path):
        """Create SlopeCalculator instance with temporary directory."""
        return SlopeCalculator(str(tmp_path))

    def test_classify_slope_data_gentle(self, calculator):
        """Test classification of gentle slopes (0-20 degrees)."""
        # Arrange
        slope_data = np.array([[5, 10, 15], [8, 12, 18], [3, 7, 19]])

        # Act
        classified = calculator._classify_slope_data(slope_data)

        # Assert
        assert np.all(classified == 1)  # All should be classified as gentle (1)

    def test_classify_slope_data_moderate(self, calculator):
        """Test classification of moderate slopes (20-30 degrees)."""
        # Arrange
        slope_data = np.array([[20, 25, 29], [21, 27, 28], [22, 26, 30]])

        # Act
        classified = calculator._classify_slope_data(slope_data)

        # Assert
        # Values 20-29 should be 2, 30 should be 3
        assert classified[0, 0] == 2  # 20 degrees
        assert classified[0, 1] == 2  # 25 degrees
        assert classified[0, 2] == 2  # 29 degrees
        assert classified[2, 2] == 3  # 30 degrees

    def test_classify_slope_data_steep(self, calculator):
        """Test classification of steep slopes (>30 degrees)."""
        # Arrange
        slope_data = np.array([[31, 45, 60], [35, 50, 75], [40, 55, 89]])

        # Act
        classified = calculator._classify_slope_data(slope_data)

        # Assert
        assert np.all(classified == 3)  # All should be classified as steep (3)

    def test_classify_slope_data_mixed(self, calculator):
        """Test classification with mixed slope values."""
        # Arrange
        slope_data = np.array([[5, 25, 45], [15, 30, 60], [10, 20, 35]])

        # Act
        classified = calculator._classify_slope_data(slope_data)

        # Assert
        assert classified[0, 0] == 1  # 5 degrees - gentle
        assert classified[0, 1] == 2  # 25 degrees - moderate
        assert classified[0, 2] == 3  # 45 degrees - steep
        assert classified[1, 1] == 3  # 30 degrees - steep
        assert classified[2, 1] == 2  # 20 degrees - moderate


class TestSlopeClassificationCompleteness:
    """
    Property 5: Slope Classification Completeness
    For any slope value in degrees, it SHALL be classified into exactly 
    one of the three categories: 0–20°, 20–30°, or >30°.
    """

    def test_all_slopes_classified(self):
        """Test that all slope values are classified into exactly one category."""
        # Arrange
        calculator = SlopeCalculator()
        slope_data = np.random.uniform(0, 90, (100, 100))

        # Act
        classified = calculator._classify_slope_data(slope_data)

        # Assert
        # All values should be 1, 2, or 3
        assert np.all((classified >= 1) & (classified <= 3))

        # Check that each slope value is in exactly one category
        for i in range(slope_data.shape[0]):
            for j in range(slope_data.shape[1]):
                slope_val = slope_data[i, j]
                class_val = classified[i, j]

                if 0 <= slope_val < 20:
                    assert class_val == 1
                elif 20 <= slope_val < 30:
                    assert class_val == 2
                else:
                    assert class_val == 3

    def test_boundary_values(self):
        """Test classification at boundary values."""
        # Arrange
        calculator = SlopeCalculator()
        boundary_slopes = np.array([[0, 19.9, 20, 29.9, 30, 89.9]])

        # Act
        classified = calculator._classify_slope_data(boundary_slopes)

        # Assert
        assert classified[0, 0] == 1  # 0 degrees
        assert classified[0, 1] == 1  # 19.9 degrees
        assert classified[0, 2] == 2  # 20 degrees
        assert classified[0, 3] == 2  # 29.9 degrees
        assert classified[0, 4] == 3  # 30 degrees
        assert classified[0, 5] == 3  # 89.9 degrees
