"""
Tests for flight regime analyzer
"""

import pytest
import numpy as np
from src.optimization.flight_regime_analyzer import (
    FlightRegimeAnalyzer,
    FlightRegimeAnalysis
)


def test_speed_of_sound_calculation():
    """Test speed of sound calculation"""
    analyzer = FlightRegimeAnalyzer()
    
    # At sea level (288.15 K)
    a = analyzer.calculate_speed_of_sound(288.15)
    assert 340 < a < 342  # Should be around 340.3 m/s
    
    # At higher altitude (lower temperature)
    a_high = analyzer.calculate_speed_of_sound(250.0)
    assert a_high < a  # Speed of sound decreases with temperature


def test_mach_number_calculation():
    """Test Mach number calculation"""
    analyzer = FlightRegimeAnalyzer()
    
    # Subsonic
    mach = analyzer.calculate_mach_number(100.0, 288.15)
    assert 0.29 < mach < 0.30  # ~0.294
    
    # Transonic
    mach = analyzer.calculate_mach_number(340.0, 288.15)
    assert 0.99 < mach < 1.01  # ~1.0
    
    # Supersonic
    mach = analyzer.calculate_mach_number(500.0, 288.15)
    assert 1.46 < mach < 1.48  # ~1.47


def test_zero_drag_simulation():
    """Test zero-drag trajectory simulation"""
    analyzer = FlightRegimeAnalyzer()
    
    result = analyzer.simulate_zero_drag_trajectory(
        mass_initial=10.0,
        mass_dry=8.0,
        thrust=500.0,
        burn_time=2.0,
        altitude_initial=0.0,
        temperature_initial=288.15
    )
    
    assert 'max_apogee' in result
    assert 'max_velocity' in result
    assert 'max_mach' in result
    
    # Should achieve some altitude
    assert result['max_apogee'] > 0
    assert result['max_velocity'] > 0
    assert result['max_mach'] > 0


def test_flight_regime_classification():
    """Test flight regime classification"""
    analyzer = FlightRegimeAnalyzer()
    
    # Create mock trajectory data
    trajectory_subsonic = {
        'h': np.array([0, 50, 100, 150, 100, 50, 0]),
        'v': np.array([0, 50, 80, 100, 80, 50, 0]),
        'M': np.array([0, 0.15, 0.24, 0.30, 0.24, 0.15, 0]),
        'T': np.array([500, 500, 0, 0, 0, 0, 0])
    }
    
    config = {
        'mass_initial': 10.0,
        'mass_dry': 8.0,
        'thrust_max': 500.0,
        'burn_time': 2.0,
        'specific_impulse': 180.0,
        'altitude_initial': 0.0,
        'temperature_initial': 288.15
    }
    
    analysis = analyzer.analyze_trajectory(trajectory_subsonic, config)
    
    assert analysis.is_subsonic == True
    assert analysis.is_transonic == False
    assert analysis.is_supersonic == False
    assert analysis.max_mach < 0.8


def test_transonic_classification():
    """Test transonic flight classification"""
    analyzer = FlightRegimeAnalyzer()
    
    trajectory_transonic = {
        'h': np.array([0, 100, 200, 300, 200, 100, 0]),
        'v': np.array([0, 150, 250, 300, 250, 150, 0]),
        'M': np.array([0, 0.44, 0.74, 0.90, 0.74, 0.44, 0]),
        'T': np.array([800, 800, 0, 0, 0, 0, 0])
    }
    
    config = {
        'mass_initial': 10.0,
        'mass_dry': 8.0,
        'thrust_max': 800.0,
        'burn_time': 2.0,
        'specific_impulse': 180.0,
        'altitude_initial': 0.0,
        'temperature_initial': 288.15
    }
    
    analysis = analyzer.analyze_trajectory(trajectory_transonic, config)
    
    assert analysis.is_subsonic == False
    assert analysis.is_transonic == True
    assert analysis.is_supersonic == False
    assert 0.8 < analysis.max_mach <= 1.2


def test_supersonic_classification():
    """Test supersonic flight classification"""
    analyzer = FlightRegimeAnalyzer()
    
    trajectory_supersonic = {
        'h': np.array([0, 200, 400, 600, 400, 200, 0]),
        'v': np.array([0, 250, 400, 500, 400, 250, 0]),
        'M': np.array([0, 0.74, 1.18, 1.50, 1.18, 0.74, 0]),
        'T': np.array([1500, 1500, 0, 0, 0, 0, 0])
    }
    
    config = {
        'mass_initial': 10.0,
        'mass_dry': 8.0,
        'thrust_max': 1500.0,
        'burn_time': 2.0,
        'specific_impulse': 180.0,
        'altitude_initial': 0.0,
        'temperature_initial': 288.15
    }
    
    analysis = analyzer.analyze_trajectory(trajectory_supersonic, config)
    
    assert analysis.is_subsonic == False
    assert analysis.is_transonic == False
    assert analysis.is_supersonic == True
    assert analysis.max_mach > 1.2


def test_recommendations_generated_for_supersonic():
    """Test that recommendations are generated for supersonic flight"""
    analyzer = FlightRegimeAnalyzer()
    
    trajectory_supersonic = {
        'h': np.array([0, 200, 400, 600, 400, 200, 0]),
        'v': np.array([0, 250, 400, 500, 400, 250, 0]),
        'M': np.array([0, 0.74, 1.18, 1.50, 1.18, 0.74, 0]),
        'T': np.array([1500, 1500, 0, 0, 0, 0, 0])
    }
    
    config = {
        'mass_initial': 10.0,
        'mass_dry': 8.0,
        'thrust_max': 1500.0,
        'burn_time': 2.0,
        'specific_impulse': 180.0,
        'altitude_initial': 0.0,
        'temperature_initial': 288.15
    }
    
    analysis = analyzer.analyze_trajectory(trajectory_supersonic, config)
    
    assert analysis.recommendations is not None
    assert 'status' in analysis.recommendations
    assert analysis.recommendations['status'] == 'SUPERSONIC_DETECTED'
    assert 'option_1' in analysis.recommendations
    assert 'option_2' in analysis.recommendations
    assert 'option_3' in analysis.recommendations
    assert 'warnings' in analysis.recommendations
    assert 'design_suggestions' in analysis.recommendations


def test_no_recommendations_for_subsonic():
    """Test that no recommendations are generated for subsonic flight"""
    analyzer = FlightRegimeAnalyzer()
    
    trajectory_subsonic = {
        'h': np.array([0, 50, 100, 150, 100, 50, 0]),
        'v': np.array([0, 50, 80, 100, 80, 50, 0]),
        'M': np.array([0, 0.15, 0.24, 0.30, 0.24, 0.15, 0]),
        'T': np.array([500, 500, 0, 0, 0, 0, 0])
    }
    
    config = {
        'mass_initial': 10.0,
        'mass_dry': 8.0,
        'thrust_max': 500.0,
        'burn_time': 2.0,
        'specific_impulse': 180.0,
        'altitude_initial': 0.0,
        'temperature_initial': 288.15
    }
    
    analysis = analyzer.analyze_trajectory(trajectory_subsonic, config)
    
    assert analysis.recommendations is None


def test_recommendation_thrust_reduction():
    """Test that recommendations suggest appropriate thrust reduction"""
    analyzer = FlightRegimeAnalyzer()
    
    max_mach = 1.5
    max_velocity = 500.0
    max_thrust = 1500.0
    
    config = {
        'thrust_max': 1500.0,
        'burn_time': 2.0,
        'specific_impulse': 180.0
    }
    
    recommendations = analyzer._generate_recommendations(
        max_mach=max_mach,
        max_velocity=max_velocity,
        max_thrust=max_thrust,
        config=config
    )
    
    # Check that recommended thrust is reduced
    assert recommendations['option_1']['recommended_thrust'] < max_thrust
    assert recommendations['option_2']['recommended_thrust'] < max_thrust
    assert recommendations['option_3']['recommended_thrust'] < max_thrust
    
    # Check reduction factor
    target_mach = 0.7
    expected_reduction = target_mach / max_mach
    assert abs(recommendations['option_1']['reduction_factor'] - expected_reduction) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
