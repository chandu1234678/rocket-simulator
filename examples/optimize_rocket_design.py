"""
Example: Optimize Rocket Design for Target Apogee

This script demonstrates parallel optimization of rocket design parameters
(diameter, nose cone length, body length) to achieve a target apogee altitude.

Multiple optimization algorithms run simultaneously to find the best design.
"""

from src.core.config import load_config
from src.optimization import RocketDesignOptimizer
import time


def main():
    """Run rocket design optimization"""
    
    print("\n" + "="*80)
    print("ROCKET DESIGN OPTIMIZATION")
    print("="*80)
    
    # Load base configuration
    print("\nLoading base configuration...")
    config = load_config("data/config.json")
    
    print(f"Base rocket configuration:")
    print(f"  Diameter: {config.rocket.diameter:.3f} m")
    print(f"  Nose Length: {config.rocket.nose_cone_length:.3f} m")
    print(f"  Body Length: {config.rocket.body_length:.3f} m")
    print(f"  Total Length: {config.rocket.length:.3f} m")
    
    # Create optimizer
    optimizer = RocketDesignOptimizer(config)
    
    # Define optimization parameters
    TARGET_APOGEE = 300.0  # meters
    TOLERANCE = 5.0        # meters
    
    print(f"\nOptimization Target:")
    print(f"  Target Apogee: {TARGET_APOGEE:.1f} m")
    print(f"  Tolerance: ±{TOLERANCE:.1f} m")
    print(f"  Acceptable Range: {TARGET_APOGEE - TOLERANCE:.1f} - {TARGET_APOGEE + TOLERANCE:.1f} m")
    
    # Run optimization
    print("\nStarting parallel optimization...")
    start_time = time.time()
    
    result = optimizer.optimize(
        target_apogee=TARGET_APOGEE,
        tolerance=TOLERANCE,
        diameter_range=(0.10, 0.30),      # 10-30 cm diameter
        nose_length_range=(0.20, 0.80),   # 20-80 cm nose
        body_length_range=(0.80, 2.50),   # 80-250 cm body
        max_iterations=100,
        methods=['differential_evolution', 'nelder-mead', 'powell', 'slsqp']
    )
    
    total_time = time.time() - start_time
    
    # Display final results
    print("\n" + "="*80)
    print("FINAL OPTIMIZED DESIGN")
    print("="*80)
    
    print(f"\nGeometry:")
    print(f"  Diameter:         {result['diameter']:.4f} m ({result['diameter']*100:.2f} cm)")
    print(f"  Nose Cone Length: {result['nose_cone_length']:.4f} m ({result['nose_cone_length']*100:.2f} cm)")
    print(f"  Body Length:      {result['body_length']:.4f} m ({result['body_length']*100:.2f} cm)")
    print(f"  Total Length:     {result['total_length']:.4f} m ({result['total_length']*100:.2f} cm)")
    
    print(f"\nRatios:")
    print(f"  Length/Diameter:  {result['total_length']/result['diameter']:.2f}")
    print(f"  Nose/Body:        {result['nose_cone_length']/result['body_length']:.3f}")
    
    print(f"\nPerformance:")
    print(f"  Target Apogee:    {result['target_apogee']:.2f} m")
    print(f"  Achieved Apogee:  {result['apogee']:.2f} m")
    print(f"  Error:            {result['error']:.2f} m ({result['error_percent']:.2f}%)")
    print(f"  Within Tolerance: {'YES ✓' if result['success'] else 'NO ✗'}")
    
    print(f"\nOptimization Details:")
    print(f"  Best Method:      {result['method']}")
    print(f"  Iterations:       {result['iterations']}")
    print(f"  Computation Time: {result['computation_time']:.2f} s")
    print(f"  Total Time:       {total_time:.2f} s")
    
    print("\n" + "="*80)
    
    # Show comparison with all methods
    print("\nCOMPARISON OF ALL METHODS:")
    print("-"*80)
    all_results = result['all_results']
    for i, r in enumerate(all_results, 1):
        status = "✓" if r.success else "✗"
        print(f"{i}. {status} {r.method:20s} | "
              f"D={r.diameter:.4f}m | "
              f"Nose={r.nose_cone_length:.4f}m | "
              f"Body={r.body_length:.4f}m | "
              f"Apogee={r.apogee:.2f}m | "
              f"Error={r.error:.2f}m")
    
    print("\n" + "="*80)
    print("Results saved to: optimization_results.json")
    print("="*80 + "\n")
    
    return result


if __name__ == "__main__":
    result = main()
