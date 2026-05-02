"""
Complete Rocket Analysis - Full Workflow
For aerospace students - just modify the values below and run!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*80)
print("ROCKET TRAJECTORY ANALYSIS - COMPLETE WORKFLOW")
print("="*80)
print()

# ============================================================================
# STEP 1: ENTER YOUR ROCKET PARAMETERS HERE
# ============================================================================

print("Step 1: Loading rocket configuration...")

ROCKET_CONFIG = {
    'thrust': 80.0,              # Thrust force in Newtons (N)
    'burn_time': 1.8,            # Engine burn duration in seconds (s)
    'specific_impulse': 180,     # Specific impulse in seconds (s)
    'mass_initial': 2.76,        # Initial total mass in kilograms (kg)
    'mass_dry': 2.0,             # Dry mass (without propellant) in kg
}

# Rocket Geometry Ratios (used to estimate dimensions from optimized diameter)
NOSE_TO_DIAMETER_RATIO = 3.0     # Nose cone length = 3 × Diameter (typical for model rockets)
BODY_TO_DIAMETER_RATIO = 10.0    # Body tube length = 10 × Diameter (typical for model rockets)

TARGET_APOGEE = 5000.0           # Target altitude in meters (m)
TOLERANCE = 50.0                 # Acceptable error in meters (m)
MAX_ITERATIONS = 100             # Maximum optimization iterations (higher = more accurate but slower)

print(f"  Thrust: {ROCKET_CONFIG['thrust']} N")
print(f"  Burn Time: {ROCKET_CONFIG['burn_time']} s")
print(f"  Specific Impulse: {ROCKET_CONFIG['specific_impulse']} s")
print(f"  Initial Mass: {ROCKET_CONFIG['mass_initial']} kg")
print(f"  Dry Mass: {ROCKET_CONFIG['mass_dry']} kg")
print(f"  Target Apogee: {TARGET_APOGEE} m")
print()

# ============================================================================
# STEP 2: FEASIBILITY CHECK
# ============================================================================

print("="*80)
print("Step 2: Pre-Flight Feasibility Check")
print("="*80)
print("Checking if your rocket can reach the target altitude safely...")
print()

from src.optimization.feasibility_checker import FeasibilityChecker

checker = FeasibilityChecker(supersonic_limit=1.2)
feasibility = checker.check_feasibility(
    thrust=ROCKET_CONFIG['thrust'],
    burn_time=ROCKET_CONFIG['burn_time'],
    specific_impulse=ROCKET_CONFIG['specific_impulse'],
    mass_initial=ROCKET_CONFIG['mass_initial'],
    mass_dry=ROCKET_CONFIG['mass_dry'],
    target_apogee=TARGET_APOGEE
)

if feasibility.can_proceed:
    print("RESULT: FEASIBLE")
    print(f"  Your rocket can reach {TARGET_APOGEE} m")
    print(f"  Maximum Mach number: {feasibility.max_mach_ideal:.2f}")
    print(f"  Ideal maximum altitude: {feasibility.ideal_apogee:.0f} m")
    print()
else:
    print("RESULT: NOT FEASIBLE")
    print(f"  Reason: {feasibility.reason}")
    print()
    
    if feasibility.is_supersonic:
        print("WARNING: Your rocket will go supersonic (Mach > 1.2)")
        print("This is dangerous! You must reduce:")
        print()
        for key, option in feasibility.suggestions['options'].items():
            print(f"  Option: {option['message']}")
    else:
        print("Your rocket cannot reach the target altitude.")
        print("You must increase:")
        print()
        for key, option in feasibility.suggestions['options'].items():
            print(f"  Option: {option['message']}")
    
    print()
    print("Please modify your rocket parameters above and run again.")
    print("="*80)
    exit()

# ============================================================================
# STEP 3: OPTIMIZATION
# ============================================================================

print("="*80)
print("Step 3: Optimizing Rocket Design")
print("="*80)
print("Finding the best diameter and drag coefficient...")
print()

from src.optimization.hybrid_optimizer import HybridOptimizer

optimizer = HybridOptimizer(
    ROCKET_CONFIG, 
    target_apogee=TARGET_APOGEE, 
    tolerance=TOLERANCE,
    max_iterations=MAX_ITERATIONS,
    nose_ratio=NOSE_TO_DIAMETER_RATIO,
    body_ratio=BODY_TO_DIAMETER_RATIO
)
result = optimizer.optimize_hybrid()

print("OPTIMIZATION COMPLETE")
print()
print("Optimized Design:")
print(f"  Body Diameter: {result['diameter']:.4f} m ({result['diameter']*100:.2f} cm)")
print(f"  Nose Cone Length (estimated): {result.get('nose_length', 0.3):.4f} m  # {NOSE_TO_DIAMETER_RATIO}×D ratio")
print(f"  Body Length (estimated):      {result.get('body_length', 1.0):.4f} m  # {BODY_TO_DIAMETER_RATIO}×D ratio")
print(f"  Total Length:                 {result.get('nose_length', 0.3) + result.get('body_length', 1.0):.4f} m")
print(f"  Drag Coefficient (Cd): {result['cd']:.4f}")
print()
print("Performance:")
print(f"  Achieved Apogee: {result['apogee']:.2f} m")
print(f"  Target Apogee: {TARGET_APOGEE:.2f} m")
print(f"  Error: {result['error']:.2f} m ({result['error']/TARGET_APOGEE*100:.2f}%)")
print(f"  Maximum Mach: {result['max_mach']:.3f}")
print()
print(f"Optimization Time: {result['time']:.3f} seconds")
print(f"Optimization Steps: {result.get('optimization_steps', result['iterations'])} iterations")
print()

# ============================================================================
# STEP 4: SUMMARY
# ============================================================================

print("="*80)
print("FINAL SUMMARY")
print("="*80)
print()
print("Your Rocket Configuration:")
print(f"  Thrust: {ROCKET_CONFIG['thrust']} N")
print(f"  Burn Time: {ROCKET_CONFIG['burn_time']} s")
print(f"  Specific Impulse: {ROCKET_CONFIG['specific_impulse']} s")
print(f"  Initial Mass: {ROCKET_CONFIG['mass_initial']} kg")
print(f"  Dry Mass: {ROCKET_CONFIG['mass_dry']} kg")
print()
print("Optimized Design:")
print(f"  Body Diameter: {result['diameter']:.4f} m ({result['diameter']*100:.2f} cm)")
print(f"  Nose Cone Length (estimated): {result.get('nose_length', 0.3):.4f} m  # {NOSE_TO_DIAMETER_RATIO}×D ratio")
print(f"  Body Length (estimated):      {result.get('body_length', 1.0):.4f} m  # {BODY_TO_DIAMETER_RATIO}×D ratio")
print(f"  Total Rocket Length:          {result.get('nose_length', 0.3) + result.get('body_length', 1.0):.4f} m")
print(f"  Drag Coefficient: {result['cd']:.4f}")
print()
print("Expected Performance:")
print(f"  Maximum Altitude: {result['apogee']:.2f} m")
print(f"  Maximum Mach Number: {result['max_mach']:.3f}")
print()

if result['converged']:
    print("STATUS: SUCCESS - Design meets requirements!")
else:
    print("STATUS: CLOSE - Design is close but may need refinement")

print()
print("="*80)
print("Analysis complete! You can now build your rocket with these specifications.")
print("="*80)
