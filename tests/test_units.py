"""Tests for unit conversion utilities."""

import pytest
from soap_calc import units

class TestWeightConversions:
    def test_grams_to_ounces(self):
        assert abs(units.grams_to_ounces(28.3495) - 1.0) < 0.0001
        assert abs(units.grams_to_ounces(0) - 0.0) < 0.0001

    def test_ounces_to_grams(self):
        assert abs(units.ounces_to_grams(1.0) - 28.3495) < 0.0001
        assert abs(units.ounces_to_grams(0) - 0.0) < 0.0001

    def test_grams_to_pounds(self):
        assert abs(units.grams_to_pounds(453.592) - 1.0) < 0.0001

    def test_pounds_to_grams(self):
        assert abs(units.pounds_to_grams(1.0) - 453.592) < 0.0001

    def test_grams_to_kilograms(self):
        assert abs(units.grams_to_kilograms(1000.0) - 1.0) < 0.0001

    def test_kilograms_to_grams(self):
        assert abs(units.kilograms_to_grams(1.0) - 1000.0) < 0.0001

class TestVolumeConversions:
    def test_ml_to_floz(self):
        assert abs(units.ml_to_floz(29.5735) - 1.0) < 0.0001

    def test_floz_to_ml(self):
        assert abs(units.floz_to_ml(1.0) - 29.5735) < 0.0001

    def test_ml_to_cups(self):
        assert abs(units.ml_to_cups(236.588) - 1.0) < 0.0001

    def test_cups_to_ml(self):
        assert abs(units.cups_to_ml(1.0) - 236.588) < 0.0001

class TestTemperatureConversions:
    def test_celsius_to_fahrenheit(self):
        assert abs(units.celsius_to_fahrenheit(0) - 32.0) < 0.0001
        assert abs(units.celsius_to_fahrenheit(100) - 212.0) < 0.0001
        assert abs(units.celsius_to_fahrenheit(-40) - -40.0) < 0.0001

    def test_fahrenheit_to_celsius(self):
        assert abs(units.fahrenheit_to_celsius(32.0) - 0.0) < 0.0001
        assert abs(units.fahrenheit_to_celsius(212.0) - 100.0) < 0.0001
        assert abs(units.fahrenheit_to_celsius(-40.0) - -40.0) < 0.0001

class TestDimensionConversions:
    def test_cm_to_inches(self):
        assert abs(units.cm_to_inches(2.54) - 1.0) < 0.0001

    def test_inches_to_cm(self):
        assert abs(units.inches_to_cm(1.0) - 2.54) < 0.0001
