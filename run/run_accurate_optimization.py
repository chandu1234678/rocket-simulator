"""
Accurate Optimization (0.5 seconds)
Balanced optimization with 90% accuracy - recommended for most users
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


from data.default_rocket_config import get_config


print("="*80)
print("ACCURATE ROCKET OPTIMIZATION (HYBRID METHOD)")
print("="*80)
print()

# ============================================================================
# ENTER YOUR ROCKET PARAMETERS HERE
# ============================================================================

# Load default configuration
ROCKET_CONFIG = get_config('default')

# Override if needed
# ROCKET_CONFIG['thrust'] = 100.0

TARGET_APOGEE = 5000.0           # Target altitude in meters (m)
TOLERANCE = 50.0                 # Acceptable error in meters (m)
MAX_ITERATIONS = 20              # Maximum optimization iterations

# ============================================================================
# RUNNING ACCURATE OPTIMIZATION
# ============================================================================

print("Running accurate optimization (this takes about 0.5 seconds)...")
print()
print("Configuration:")
print(f"  Thrust: {ROCKET_CONFIG['thrust']} N")
print(f"  Burn Time: {ROCKET_CONFIG['burn_time']} s")
print(f"  Specific Impulse: {ROCKET_CONFIG['specific_impulse']} s")
print(f"  Initial Mass: {ROCKET_CONFIG['mass_initial']} kg")
print(f"  Dry Mass: {ROCKET_CONFIG['mass_dry']} kg")
print(f"  Target Apogee: {TARGET_APOGEE} m")
print()

from src.optimization.hybrid_optimizer import HybridOptimizer

optimizer = HybridOptimizer(
    ROCKET_CONFIG, 
    target_apogee=TARGET_APOGEE, 
    tolerance=TOLERANCE,
    max_iterations=MAX_ITERATIONS
)
result = optimizer.optimize_hybrid()

print("="*80)
print("OPTIMIZATION RESULTS")
print("="*80)
print()

print("Optimized Design:")
print(f"  Diameter: {result['diameter']:.4f} m ({result['diameter']*100:.2f} cm)")
print(f"  Drag Coefficient (Cd): {result['cd']:.4f}")
print()

print("Performance:")
print(f"  Achieved Apogee: {result['apogee']:.2f} m")
print(f"  Target Apogee: {TARGET_APOGEE:.2f} m")
print(f"  Error: {result['error']:.2f} m ({result['error']/TARGET_APOGEE*100:.2f}%)")
print(f"  Maximum Mach: {result['max_mach']:.3f}")
print()

print("Timing:")
print(f"  Phase 1 (Fast Guess): {result['phase1_time']:.3f} s")
print(f"  Phase 2 (Refinement): {result['phase2_time']:.3f} s")
print(f"  Total Time: {result['time']:.3f} s")
print()

print(f"Iterations: {result['iterations']}")
print()

if result['converged']:
    print("STATUS: Converged successfully")
    print("Accuracy: ~90% (suitable for most applications)")
else:
    print("STATUS: Did not fully converge")
    print("Result is still usable but may need refinement")

print()
print("="*80)
print("RECOMMENDATIONS")
print("="*80)
print()

if result['error'] < TOLERANCE:
    print("Your design meets the requirements!")
    print()
    print("Next steps:")
    print("  1. Build a prototype with these specifications")
    print("  2. Test in a controlled environment")
    print("  3. Adjust based on real-world results")
else:
    print("Design is close but not within tolerance.")
    print()
    print("Options:")
    print("  1. Accept this design (error is small)")
    print("  2. Adjust tolerance and re-run")
    print("  3. Run production optimization (run_production_optimization.py)")

print()
print("="*80)
