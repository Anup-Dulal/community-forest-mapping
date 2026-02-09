"""
Unit tests for aspect calculator module.
Tests aspect calculation and classification.
"""

import pytest
import numpy as np
from src.aspect_calculator import AspectCalculator


class TestAspectCalculator:
    """Tests for AspectCalculator class."""

    @pytest.fixture
    def calculator(self, tmp_path):
        """Create AspectCalculator instance with temporary directory."""
        return AspectCalculator(str(tmp_path))

    def test_classify_aspect_north(self, calculator):
        """Test classification of North-facing slopes."""
        # Arrange - North: 337.5-22.5 (wraps around 0)
        aspect_data = np.array([[0, 10, 22.4], [350, 355, 359]])

        # Act
        classified = calculator._classify_aspect_data(aspect_data)

        # Assert
        assert np.all(classified == 1)  # All should be North (1)

    def test_classify_aspect_northeast(self, calculator):
        """Test classification of North-East facing slopes."""
        # Arrange - NE: 22.5-67.5
        aspect_data = np.array([[22.5, 45, 67.4], [30, 50, 60]])

        # Act
        classified = calculator._classify_aspect_data(aspect_data)

        # Assert
        assert np.all(classified == 2)  # All should be NE (2)

    def test_classify_aspect_all_directions(self, calculator):
        """Test classification of all 8 cardinal directions."""
        # Arrange
        aspect_data = np.array([
            [0, 45, 90, 135, 180, 225, 270, 315],  # Center of each direction
        ])

        # Act
        classified = calculator._classify_aspect_data(aspect_data)

        # Assert
        assert classified[0, 0] == 1  # 0 - North
        assert classified[0, 1] == 2  # 45 - NE
        assert classified[0, 2] == 3  # 90 - East
        assert classified[0, 3] == 4  # 135 - SE
        assert classified[0, 4] == 5  # 180 - South
        assert classified[0, 5] == 6  # 225 - SW
        assert classified[0, 6] == 7  # 270 - West
        assert classified[0, 7] == 8  # 315 - NW

    def test_get_direction_name(self, calculator):
        """Test direction name retrieval."""
        # Act & Assert
        assert calculator.get_direction_name(1) == 'N'
        assert calculator.get_direction_name(2) == 'NE'
        assert calculator.get_direction_name(3) == 'E'
        assert calculator.get_direction_name(4) == 'SE'
        assert calculator.get_direction_name(5) == 'S'
        assert calculator.get_direction_name(6) == 'SW'
        assert calculator.get_direction_name(7) == 'W'
        assert calculator.get_direction_name(8) == 'NW'
        assert calculator.get_direction_name(99) == 'Unknown'


class TestAspectClassificationCompleteness:
    """
    Property 6: Aspect Classification Completeness
    For any aspect value in degrees, it SHALL be classified into exactly 
    one of the eight cardinal directions: N, NE, E, SE, S, SW, W, NW.
    """

    def test_all_aspects_classified(self):
        """Test that all aspect values are classified into exactly one direction."""
        # Arrange
        calculator = AspectCalculator()
        aspect_data = np.random.uniform(0, 360, (100, 100))

        # Act
        classified = calculator._classify_aspect_data(aspect_data)

        # Assert
        # All values should be 1-8
        assert np.all((classified >= 1) & (classified <= 8))

        # Check that each aspect value is in exactly one category
        for i in range(aspect_data.shape[0]):
            for j in range(aspect_data.shape[1]):
                aspect_val = aspect_data[i, j]
                class_val = classified[i, j]

                if (aspect_val >= 337.5) or (aspect_val < 22.5):
                    assert class_val == 1  # N
                elif 22.5 <= aspect_val < 67.5:
                    assert class_val == 2  # NE
                elif 67.5 <= aspect_val < 112.5:
                    assert class_val == 3  # E
                elif 112.5 <= aspect_val < 157.5:
                    assert class_val == 4  # SE
                elif 157.5 <= aspect_val < 202.5:
                    assert class_val == 5  # S
                elif 202.5 <= aspect_val < 247.5:
                    assert class_val == 6  # SW
                elif 247.5 <= aspect_val < 292.5:
                    assert class_val == 7  # W
                elif 292.5 <= aspect_val < 337.5:
                    assert class_val == 8  # NW

    def test_boundary_values(self):
        """Test classification at boundary values."""
        # Arrange
        calculator = AspectCalculator()
        boundary_aspects = np.array([[
            0, 22.4, 22.5, 67.4, 67.5, 112.4, 112.5, 157.4, 157.5,
            202.4, 202.5, 247.4, 247.5, 292.4, 292.5, 337.4, 337.5, 359.9
        ]])

        # Act
        classified = calculator._classify_aspect_data(boundary_aspects)

        # Assert
        assert classified[0, 0] == 1   # 0 - N
        assert classified[0, 1] == 1   # 22.4 - N
        assert classified[0, 2] == 2   # 22.5 - NE
        assert classified[0, 3] == 2   # 67.4 - NE
        assert classified[0, 4] == 3   # 67.5 - E
        assert classified[0, 5] == 3   # 112.4 - E
        assert classified[0, 6] == 4   # 112.5 - SE
        assert classified[0, 7] == 4   # 157.4 - SE
        assert classified[0, 8] == 5   # 157.5 - S
        assert classified[0, 9] == 5   # 202.4 - S
        assert classified[0, 10] == 6  # 202.5 - SW
        assert classified[0, 11] == 6  # 247.4 - SW
        assert classified[0, 12] == 7  # 247.5 - W
        assert classified[0, 13] == 7  # 292.4 - W
        assert classified[0, 14] == 8  # 292.5 - NW
        assert classified[0, 15] == 8  # 337.4 - NW
        assert classified[0, 16] == 1  # 337.5 - N (wraps)
        assert classified[0, 17] == 1  # 359.9 - N
