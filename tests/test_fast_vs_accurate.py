"""
Test Fast vs Accurate Optimization
Compares FastOptimizer with HybridOptimizer
"""

from src.optimization.fast_optimizer import FastOptimizer
from src.optimization.hybrid_optimizer import HybridOptimizer


def test_fast_optimizer_speed():
    """Test that fast optimizer is actually fast"""
    base_config = {
        'thrust': 80.0,
        'burn_time': 1.8,
        'specific_impulse': 180,
        'mass_initial': 2.76,
        'mass_dry': 2.0
    }
    
    optimizer = FastOptimizer(base_config, target_apogee=500.0, tolerance=10.0)
    optimizer.show_iterations = False
    result = optimizer.optimize_fast()
    
    # Should be very fast
    assert result['time'] < 1.0, f"Fast optimizer too slow: {result['time']:.3f}s"
    assert result['diameter'] > 0, "Invalid diameter"
    assert result['cd'] > 0, "Invalid Cd"
    print(f"✓ Fast optimizer completed in {result['time']:.3f}s")


def test_hybrid_optimizer_accuracy():
    """Test that hybrid optimizer is accurate"""
    base_config = {
        'thrust': 80.0,
        'burn_time': 1.8,
        'specific_impulse': 180,
        'mass_initial': 2.76,
        'mass_dry': 2.0
    }
    
    # Use a more realistic target for this rocket (5000m instead of 500m)
    optimizer = HybridOptimizer(base_config, target_apogee=5000.0, tolerance=50.0, max_iterations=20)
    optimizer.show_iterations = False
    result = optimizer.optimize_hybrid()
    
    # Should be accurate
    assert result['error'] < 100.0, f"Error too large: {result['error']:.2f}m"
    assert result['time'] < 5.0, f"Hybrid optimizer too slow: {result['time']:.3f}s"
    print(f"✓ Hybrid optimizer: error={result['error']:.2f}m, time={result['time']:.3f}s")


def test_fast_simulation_consistency():
    """Test that fast simulation gives consistent results"""
    base_config = {
        'thrust': 80.0,
        'burn_time': 1.8,
        'specific_impulse': 180,
        'mass_initial': 2.76,
        'mass_dry': 2.0
    }
    
    optimizer = FastOptimizer(base_config, target_apogee=500.0)
    
    # Same inputs should give same outputs
    apogee1, mach1 = optimizer.fast_simulate(0.1, 0.35)
    apogee2, mach2 = optimizer.fast_simulate(0.1, 0.35)
    
    assert abs(apogee1 - apogee2) < 0.01, "Fast simulation not consistent"
    assert abs(mach1 - mach2) < 0.001, "Mach calculation not consistent"
    print(f"✓ Fast simulation consistent: apogee={apogee1:.2f}m, mach={mach1:.3f}")


if __name__ == "__main__":
    print("="*80)
    print("FAST vs ACCURATE OPTIMIZER TESTS")
    print("="*80)
    print()
    
    test_fast_optimizer_speed()
    test_hybrid_optimizer_accuracy()
    test_fast_simulation_consistency()
    
    print()
    print("="*80)
    print("ALL TESTS PASSED")
    print("="*80)
