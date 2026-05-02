"""
Tests for ideal trajectory analyzer (zero-drag)
"""

import pytest
import numpy as np
from src.models.ideal_trajectory import IdealTrajectoryAnalyzer, quick_feasibility_check


class TestIdealTrajectoryAnalyzer:
    """Test ideal trajectory calculations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = IdealTrajectoryAnalyzer()
    
    def test_basic_trajectory(self):
        """Test basic trajectory calculation"""
        result = self.analyzer.analyze(
            thrust=747.1,
            burn_time=1.8,
            specific_impulse=180,
            mass_initial=2.76,
            mass_dry=2.0,
            target_apogee=500.0
        )
        
        assert result.max_apogee > 0
        assert result.max_velocity > 0
        assert result.max_acceleration > 0
        assert result.burnout_altitude > 0
        assert result.time_to_apogee > 1.8  # Should be greater than burn time
    
    def test_feasibility_check(self):
        """Test feasibility checking"""
        # Should be feasible (ideal apogee >> target)
        result = self.analyzer.analyze(
            thrust=747.1,
            burn_time=1.8,
            specific_impulse=180,
            mass_initial=2.76,
            mass_dry=2.0,
            target_apogee=500.0
        )
        
        assert result.is_feasible == True
        assert result.margin > 0
    
    def test_infeasible_target(self):
        """Test infeasible target detection"""
        # Very high target with low thrust
        result = self.analyzer.analyze(
            thrust=100.0,
            burn_time=1.0,
            specific_impulse=100,
            mass_initial=2.76,
            mass_dry=2.0,
            target_apogee=10000.0
        )
        
        assert result.is_feasible == False
        assert result.margin < 0
    
    def test_mach_calculation(self):
        """Test Mach number calculation"""
        result = self.analyzer.analyze(
            thrust=747.1,
            burn_time=1.8,
            specific_impulse=180,
            mass_initial=2.76,
            mass_dry=2.0,
            temperature=287.0
        )
        
        # Mach should be positive and reasonable
        assert result.max_mach > 0
        assert result.max_mach < 10  # Sanity check
    
    def test_zero_thrust_fails(self):
        """Test that zero thrust raises error"""
        with pytest.raises(ValueError):
            self.analyzer.analyze(
                thrust=0.0,
                burn_time=1.8,
                specific_impulse=180,
                mass_initial=2.76,
                mass_dry=2.0
            )
    
    def test_invalid_mass_fails(self):
        """Test that invalid mass raises error"""
        with pytest.raises(ValueError):
            self.analyzer.analyze(
                thrust=747.1,
                burn_time=1.8,
                specific_impulse=180,
                mass_initial=2.0,
                mass_dry=2.76  # Dry mass > initial mass
            )
    
    def test_quick_feasibility_function(self):
        """Test quick feasibility check function"""
        is_feasible = quick_feasibility_check(
            thrust=747.1,
            burn_time=1.8,
            specific_impulse=180,
            mass_initial=2.76,
            mass_dry=2.0,
            target_apogee=500.0
        )
        
        assert isinstance(is_feasible, (bool, np.bool_))
    
    def test_suggestions_for_infeasible(self):
        """Test suggestion generation"""
        result = self.analyzer.analyze(
            thrust=100.0,
            burn_time=1.0,
            specific_impulse=100,
            mass_initial=2.76,
            mass_dry=2.0,
            target_apogee=5000.0
        )
        
        suggestions = self.analyzer.suggest_improvements(
            result, 5000.0, 100.0, 1.0, 2.76, 2.0, 100
        )
        
        assert suggestions['feasible'] == False
        assert 'suggestions' in suggestions
        assert 'thrust' in suggestions['suggestions']
        assert 'burn_time' in suggestions['suggestions']
        assert 'mass' in suggestions['suggestions']
