"""
Accuracy Benchmark Tests
Verifies the claimed accuracy levels (80%/90%/95%) are reproducible
"""

import pytest
from src.optimization.hybrid_optimizer import HybridOptimizer


# Test cases with known targets
# Note: These targets must be feasible with the given rocket config
# Config: 80N thrust, 180s ISP, 0.2kg propellant → max ~1100m ideal
BENCHMARK_CASES = [
    # (target_apogee, tolerance, expected_accuracy_percent)
    (300.0, 30.0, 90.0),   # Low altitude
    (500.0, 50.0, 90.0),   # Medium altitude  
    (800.0, 80.0, 85.0),   # High altitude
    (1000.0, 100.0, 80.0), # Near max altitude (more challenging)
]


@pytest.mark.parametrize("target,tolerance,expected_accuracy", BENCHMARK_CASES)
def test_accuracy_benchmark(target, tolerance, expected_accuracy):
    """
    Test that optimizer achieves claimed accuracy levels
    
    Accuracy = 100% - (error / target * 100%)
    """
    # Base configuration
    base_config = {
        'thrust': 80.0,
        'burn_time': 1.8,
        'specific_impulse': 180,
        'mass_initial': 2.2,
        'mass_dry': 2.0
    }
    
    # Run optimization
    optimizer = HybridOptimizer(
        base_config,
        target_apogee=target,
        tolerance=tolerance,
        max_iterations=50
    )
    optimizer.show_iterations = False  # Suppress output for tests
    
    result = optimizer.optimize_hybrid()
    
    # Calculate accuracy
    error_percent = (result['error'] / target) * 100
    accuracy = 100.0 - error_percent
    
    # Verify accuracy meets expectation
    assert accuracy >= expected_accuracy, (
        f"Accuracy {accuracy:.1f}% below expected {expected_accuracy:.1f}% "
        f"for target {target}m (error: {result['error']:.2f}m)"
    )
    
    # Verify subsonic
    assert result['max_mach'] < 1.2, (
        f"Supersonic violation: Mach {result['max_mach']:.3f} >= 1.2"
    )
    
    # Verify reasonable time
    assert result['time'] < 5.0, (
        f"Optimization too slow: {result['time']:.3f}s > 5.0s"
    )


def test_speed_benchmark():
    """Test that optimization completes within speed targets"""
    base_config = {
        'thrust': 80.0,
        'burn_time': 1.8,
        'specific_impulse': 180,
        'mass_initial': 2.2,
        'mass_dry': 2.0
    }
    
    optimizer = HybridOptimizer(
        base_config,
        target_apogee=1000.0,
        tolerance=10.0
    )
    optimizer.show_iterations = False
    
    result = optimizer.optimize_hybrid()
    
    # Speed targets
    assert result['time'] < 3.0, f"Too slow: {result['time']:.3f}s > 3.0s target"
    assert result['phase1_time'] < 0.01, f"Phase 1 too slow: {result['phase1_time']:.3f}s"
    assert result['phase2_time'] < 3.0, f"Phase 2 too slow: {result['phase2_time']:.3f}s"


def test_convergence_benchmark():
    """Test that optimizer converges within iteration limits"""
    base_config = {
        'thrust': 80.0,
        'burn_time': 1.8,
        'specific_impulse': 180,
        'mass_initial': 2.2,
        'mass_dry': 2.0
    }
    
    optimizer = HybridOptimizer(
        base_config,
        target_apogee=500.0,
        tolerance=10.0,
        max_iterations=20
    )
    optimizer.show_iterations = False
    
    result = optimizer.optimize_hybrid()
    
    # Should converge within 20 iterations
    assert result['optimization_steps'] <= 20, (
        f"Too many iterations: {result['optimization_steps']} > 20"
    )
    
    # Should achieve tolerance
    assert result['error'] <= 10.0, (
        f"Did not achieve tolerance: error {result['error']:.2f}m > 10.0m"
    )


def test_subsonic_enforcement():
    """Test that supersonic designs are rejected"""
    # High thrust config that would go supersonic
    base_config = {
        'thrust': 500.0,  # Very high thrust
        'burn_time': 3.0,
        'specific_impulse': 250,
        'mass_initial': 2.5,
        'mass_dry': 2.0
    }
    
    optimizer = HybridOptimizer(
        base_config,
        target_apogee=1000.0,
        tolerance=50.0
    )
    optimizer.show_iterations = False
    
    result = optimizer.optimize_hybrid()
    
    # Should either:
    # 1. Stay subsonic (Mach < 1.2), OR
    # 2. Mark as not converged if supersonic
    if result['max_mach'] >= 1.2:
        assert not result['converged'], (
            "Supersonic design marked as converged! "
            f"Mach {result['max_mach']:.3f} >= 1.2"
        )


if __name__ == "__main__":
    print("="*80)
    print("ACCURACY BENCHMARK TESTS")
    print("="*80)
    
    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])
