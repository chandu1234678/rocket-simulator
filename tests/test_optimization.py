"""
Tests for optimization module
"""

import pytest
import numpy as np
from src.optimization import (
    OptimizationConfig,
    ParallelRocketOptimizer,
    RocketDesignOptimizer
)


def test_optimization_config_defaults():
    """Test OptimizationConfig with default values"""
    config = OptimizationConfig(
        target_apogee=200.0,
        tolerance=5.0
    )
    
    assert config.target_apogee == 200.0
    assert config.tolerance == 5.0
    assert config.diameter_min == 0.05
    assert config.diameter_max == 0.5
    assert config.methods is not None
    assert len(config.methods) > 0


def test_optimization_config_custom():
    """Test OptimizationConfig with custom values"""
    config = OptimizationConfig(
        target_apogee=300.0,
        tolerance=10.0,
        diameter_min=0.1,
        diameter_max=0.3,
        nose_length_min=0.2,
        nose_length_max=0.8,
        body_length_min=1.0,
        body_length_max=2.5,
        max_iterations=50,
        methods=['nelder-mead', 'powell']
    )
    
    assert config.target_apogee == 300.0
    assert config.tolerance == 10.0
    assert config.diameter_min == 0.1
    assert config.diameter_max == 0.3
    assert config.max_iterations == 50
    assert len(config.methods) == 2


def test_parallel_optimizer_constraint_checking():
    """Test constraint checking in optimizer"""
    
    def dummy_simulation(d, n, b):
        return 200.0  # Always return 200m apogee
    
    config = OptimizationConfig(
        target_apogee=200.0,
        tolerance=5.0,
        length_to_diameter_ratio_min=5.0,
        length_to_diameter_ratio_max=20.0,
        nose_to_body_ratio_min=0.1,
        nose_to_body_ratio_max=0.5
    )
    
    optimizer = ParallelRocketOptimizer(dummy_simulation, config)
    
    # Valid design
    assert optimizer._check_constraints(0.2, 0.3, 1.7) == True  # L/D = 10, N/B = 0.176
    
    # Invalid: L/D too small
    assert optimizer._check_constraints(0.5, 0.3, 1.7) == False  # L/D = 4
    
    # Invalid: L/D too large
    assert optimizer._check_constraints(0.05, 0.3, 1.7) == False  # L/D = 40
    
    # Invalid: N/B too small
    assert optimizer._check_constraints(0.2, 0.1, 2.0) == False  # N/B = 0.05
    
    # Invalid: N/B too large
    assert optimizer._check_constraints(0.2, 1.0, 1.0) == False  # N/B = 1.0


def test_parallel_optimizer_objective_function():
    """Test objective function calculation"""
    
    def dummy_simulation(d, n, b):
        # Simple model: apogee increases with total length
        return 100.0 * (n + b)
    
    config = OptimizationConfig(
        target_apogee=200.0,
        tolerance=5.0
    )
    
    optimizer = ParallelRocketOptimizer(dummy_simulation, config)
    
    # Test objective function
    x = np.array([0.2, 0.5, 1.5])  # d, n, b
    error = optimizer._objective_function(x)
    
    # Expected apogee = 100 * (0.5 + 1.5) = 200
    # Error should be close to 0
    assert error < 1.0


def test_optimization_result_structure():
    """Test that optimization returns proper result structure"""
    from src.optimization.parallel_optimizer import OptimizationResult
    
    result = OptimizationResult(
        diameter=0.2,
        nose_cone_length=0.4,
        body_length=1.6,
        apogee=205.0,
        error=5.0,
        iterations=50,
        success=True,
        method='nelder-mead',
        computation_time=2.5
    )
    
    assert result.diameter == 0.2
    assert result.nose_cone_length == 0.4
    assert result.body_length == 1.6
    assert result.apogee == 205.0
    assert result.error == 5.0
    assert result.success == True
    assert result.method == 'nelder-mead'


def _simple_simulation_for_test(d, n, b):
    """Simple quadratic function with known minimum - module level for pickling"""
    # Target: d=0.2, n=0.5, b=1.5 gives apogee=200
    target_d, target_n, target_b = 0.2, 0.5, 1.5
    
    # Quadratic penalty from target
    penalty = (d - target_d)**2 + (n - target_n)**2 + (b - target_b)**2
    
    # Apogee decreases with distance from target
    return 200.0 - 100.0 * penalty


def test_simple_optimization():
    """Test simple optimization with quadratic function"""
    
    config = OptimizationConfig(
        target_apogee=200.0,
        tolerance=5.0,
        diameter_min=0.1,
        diameter_max=0.3,
        nose_length_min=0.3,
        nose_length_max=0.7,
        body_length_min=1.0,
        body_length_max=2.0,
        max_iterations=50,
        methods=['nelder-mead']  # Use single fast method for testing
    )
    
    optimizer = ParallelRocketOptimizer(_simple_simulation_for_test, config)
    results = optimizer.optimize_parallel()
    
    assert len(results) > 0
    best = results[0]
    
    # Check that optimization found something close to target
    assert abs(best.diameter - 0.2) < 0.05
    assert abs(best.nose_cone_length - 0.5) < 0.1
    assert abs(best.body_length - 1.5) < 0.1
    assert abs(best.apogee - 200.0) < 10.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
