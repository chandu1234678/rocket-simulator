"""
Unit tests for aerodynamics model.
"""
import pytest
import numpy as np
from src.models.aerodynamics import (
    Aerodynamics,
    compute_mach_number,
    drag_coefficient_simple,
    drag_coefficient_advanced,
    compute_drag_force
)


def test_mach_number():
    """Test Mach number calculation."""
    M = compute_mach_number(340.0, 340.0)
    assert abs(M - 1.0) < 0.001
    
    M = compute_mach_number(170.0, 340.0)
    assert abs(M - 0.5) < 0.001


def test_drag_coefficient_simple():
    """Test simple constant Cd model."""
    Cd = drag_coefficient_simple(0.5, Cd_base=0.366)
    assert abs(Cd - 0.366) < 0.001


def test_drag_coefficient_transonic_spike():
    """Test transonic drag spike."""
    # At M=1.0, should have spike
    Cd_1 = drag_coefficient_advanced(1.0, Cd_base=0.366, k_spike=0.5)
    
    # At M=0.5, should be lower
    Cd_05 = drag_coefficient_advanced(0.5, Cd_base=0.366, k_spike=0.5)
    
    # Transonic should be higher
    assert Cd_1 > Cd_05


def test_drag_force_zero_velocity():
    """Test drag is zero at zero velocity."""
    D = compute_drag_force(0.0, 1.225, 0.366, 0.0366)
    assert D == 0.0


def test_drag_force_increases_with_velocity():
    """Test drag increases with velocity squared."""
    D_10 = compute_drag_force(10.0, 1.225, 0.366, 0.0366)
    D_20 = compute_drag_force(20.0, 1.225, 0.366, 0.0366)
    
    # Should be roughly 4x (v² relationship)
    assert D_20 / D_10 > 3.9
    assert D_20 / D_10 < 4.1


def test_aerodynamics_class():
    """Test Aerodynamics class."""
    aero = Aerodynamics(A_ref=0.0366, Cd_base=0.366, use_advanced=False)
    
    M, Cd, D = aero.compute_all(v=50.0, rho=1.225, a=340.0)
    
    assert M > 0
    assert Cd > 0
    assert D > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
