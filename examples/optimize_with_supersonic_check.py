"""
Example: Rocket Design Optimization with Supersonic Flight Checking

This script demonstrates optimization with automatic supersonic flight detection.
If the rocket goes supersonic (Mach > 1.2), the optimization stops and provides
recommendations for propulsion system modifications.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import load_config
from src.optimization import RocketDesignOptimizer
import time


def main():
    """Run rocket design optimization with supersonic checking"""
    
    print("\n" + "="*80)
    print("ROCKET DESIGN OPTIMIZATION WITH SUPERSONIC FLIGHT CHECKING")
    print("="*80)
    
    # Load base configuration
    print("\nLoading base configuration...")
    config = load_config("data/config.json")
    
    print(f"Base rocket configuration:")
    print(f"  Diameter: {config.rocket.diameter:.3f} m")
    print(f"  Nose Length: {config.rocket.nose_cone_length:.3f} m")
    print(f"  Body Length: {config.rocket.body_length:.3f} m")
    print(f"  Total Length: {config.rocket.length:.3f} m")
    print(f"  Thrust: {config.propulsion.thrust_max:.1f} N")
    print(f"  Burn Time: {config.propulsion.burn_time:.1f} s")
    
    # Create optimizer with supersonic checking ENABLED
    optimizer = RocketDesignOptimizer(config, check_supersonic=True)
    
    # Define optimization parameters
    TARGET_APOGEE = 300.0  # meters
    TOLERANCE = 5.0        # meters
    
    print(f"\nOptimization Target:")
    print(f"  Target Apogee: {TARGET_APOGEE:.1f} m")
    print(f"  Tolerance: ±{TOLERANCE:.1f} m")
    print(f"  Acceptable Range: {TARGET_APOGEE - TOLERANCE:.1f} - {TARGET_APOGEE + TOLERANCE:.1f} m")
    
    # Run optimization
    print("\nStarting optimization with supersonic checking...")
    start_time = time.time()
    
    result = optimizer.optimize(
        target_apogee=TARGET_APOGEE,
        tolerance=TOLERANCE,
        diameter_range=(0.10, 0.30),      # 10-30 cm diameter
        nose_length_range=(0.20, 0.80),   # 20-80 cm nose
        body_length_range=(0.80, 2.50),   # 80-250 cm body
        max_iterations=100,
        methods=['differential_evolution', 'nelder-mead', 'powell']
    )
    
    total_time = time.time() - start_time
    
    # Check result status
    print("\n" + "="*80)
    print("OPTIMIZATION RESULT")
    print("="*80)
    
    if result['status'] == 'SUPERSONIC_DETECTED':
        print("\n⚠️  SUPERSONIC FLIGHT DETECTED!")
        print("="*80)
        
        if result.get('optimization_skipped'):
            print("\nOptimization was SKIPPED because the base configuration")
            print("already goes supersonic.")
        else:
            print("\nOptimization completed, but the optimized design")
            print("goes supersonic.")
            
            opt_design = result['optimized_design']
            print(f"\nOptimized Design (SUPERSONIC):")
            print(f"  Diameter: {opt_design['diameter']:.4f} m")
            print(f"  Nose Length: {opt_design['nose_cone_length']:.4f} m")
            print(f"  Body Length: {opt_design['body_length']:.4f} m")
            print(f"  Apogee: {opt_design['apogee']:.2f} m")
        
        # Flight analysis was already printed by the analyzer
        print("\n" + "="*80)
        print("RECOMMENDATION: Modify propulsion system before proceeding.")
        print("See recommendations above for specific modifications.")
        print("="*80)
        
    elif result['status'] == 'SUCCESS':
        print("\n✓ OPTIMIZATION SUCCESSFUL (SUBSONIC FLIGHT)")
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
        
        # Print flight analysis if available
        if result.get('flight_analysis'):
            analysis = result['flight_analysis']
            print(f"\nFlight Regime Analysis:")
            print(f"  Max Mach Number:  {analysis.max_mach:.3f}")
            print(f"  Max Velocity:     {analysis.max_velocity:.2f} m/s")
            print(f"  Flight Regime:    {'SUBSONIC ✓' if analysis.is_subsonic else 'TRANSONIC ⚠️' if analysis.is_transonic else 'SUPERSONIC ✗'}")
        
        print(f"\nOptimization Details:")
        print(f"  Best Method:      {result['method']}")
        print(f"  Iterations:       {result['iterations']}")
        print(f"  Computation Time: {result['computation_time']:.2f} s")
        print(f"  Total Time:       {total_time:.2f} s")
        
        print("\n" + "="*80)
        print("Results saved to: optimization_results.json")
        print("="*80)
    
    print("\n")
    return result


def example_high_thrust_supersonic():
    """
    Example that intentionally creates a supersonic configuration
    to demonstrate the supersonic checking feature
    """
    print("\n" + "="*80)
    print("EXAMPLE: HIGH-THRUST SUPERSONIC CONFIGURATION")
    print("="*80)
    print("This example intentionally uses high thrust to demonstrate")
    print("supersonic flight detection and recommendations.")
    print("="*80 + "\n")
    
    # Load config and modify to be supersonic
    config = load_config("data/config.json")
    
    # Increase thrust significantly to go supersonic
    config.propulsion.thrust_max = 2000.0  # Very high thrust
    config.propulsion.burn_time = 3.0
    
    print(f"Modified Configuration (High Thrust):")
    print(f"  Thrust: {config.propulsion.thrust_max:.1f} N")
    print(f"  Burn Time: {config.propulsion.burn_time:.1f} s")
    print(f"  Total Impulse: {config.propulsion.thrust_max * config.propulsion.burn_time:.1f} N·s")
    
    # Create optimizer
    optimizer = RocketDesignOptimizer(config, check_supersonic=True)
    
    # Try to optimize
    result = optimizer.optimize(
        target_apogee=500.0,
        tolerance=10.0,
        max_iterations=50,
        methods=['nelder-mead']  # Just one method for speed
    )
    
    return result


if __name__ == "__main__":
    # Run normal optimization
    result = main()
    
    # Uncomment to run supersonic example
    # print("\n\n")
    # result_supersonic = example_high_thrust_supersonic()
