"""
Unit tests for atmosphere model.
"""
import pytest
import numpy as np
from src.models.atmosphere import (
    Atmosphere,
    exponential_density,
    temperature_lapse,
    speed_of_sound
)


def test_sea_level_density():
    """Test sea level density is correct."""
    rho = exponential_density(0.0)
    assert abs(rho - 1.225) < 0.001


def test_density_decreases_with_altitude():
    """Test density decreases with altitude."""
    rho_0 = exponential_density(0.0)
    rho_1000 = exponential_density(1000.0)
    rho_5000 = exponential_density(5000.0)
    
    assert rho_0 > rho_1000 > rho_5000


def test_temperature_lapse():
    """Test temperature lapse rate."""
    T_0 = temperature_lapse(0.0, T0=288.15)
    T_1000 = temperature_lapse(1000.0, T0=288.15)
    
    assert T_0 > T_1000
    assert abs(T_0 - T_1000 - 6.5) < 0.1  # ~6.5K per 1000m


def test_speed_of_sound():
    """Test speed of sound calculation."""
    a = speed_of_sound(288.15)  # 15°C
    assert abs(a - 340.0) < 1.0  # ~340 m/s at sea level


def test_atmosphere_class():
    """Test Atmosphere class."""
    atm = Atmosphere(h0=0.0, T0=288.15, P0=101325.0, rho0=1.225)
    
    rho, T, P, a = atm.get_all_properties(0.0)
    
    assert abs(rho - 1.225) < 0.01
    assert abs(T - 288.15) < 0.1
    assert abs(a - 340.0) < 1.0


def test_atmosphere_at_altitude():
    """Test atmosphere at 1000m altitude."""
    atm = Atmosphere()
    
    rho_0 = atm.get_density(0.0)
    rho_1000 = atm.get_density(1000.0)
    
    assert rho_1000 < rho_0
    assert rho_1000 / rho_0 > 0.85  # Roughly 15% decrease


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
