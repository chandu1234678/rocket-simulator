"""
Fast Optimization (0.02 seconds)
Quick optimization for initial design estimates
"""

print("="*80)
print("FAST ROCKET OPTIMIZATION")
print("="*80)
print()

# ============================================================================
# ENTER YOUR ROCKET PARAMETERS HERE
# ============================================================================

ROCKET_CONFIG = {
    'thrust': 80.0,              # Thrust force in Newtons (N)
    'burn_time': 1.8,            # Engine burn duration in seconds (s)
    'specific_impulse': 180,     # Specific impulse in seconds (s)
    'mass_initial': 2.76,        # Initial total mass in kilograms (kg)
    'mass_dry': 2.0,             # Dry mass (without propellant) in kg
}

TARGET_APOGEE = 5000.0           # Target altitude in meters (m)
TOLERANCE = 50.0                 # Acceptable error in meters (m)
MAX_ITERATIONS = 20              # Maximum optimization iterations (higher = more accurate but slower)

# ============================================================================
# RUNNING FAST OPTIMIZATION
# ============================================================================

print("Running fast optimization...")
print()
print("Configuration:")
print(f"  Thrust: {ROCKET_CONFIG['thrust']} N")
print(f"  Burn Time: {ROCKET_CONFIG['burn_time']} s")
print(f"  Specific Impulse: {ROCKET_CONFIG['specific_impulse']} s")
print(f"  Initial Mass: {ROCKET_CONFIG['mass_initial']} kg")
print(f"  Dry Mass: {ROCKET_CONFIG['mass_dry']} kg")
print(f"  Target Apogee: {TARGET_APOGEE} m")
print()

from src.optimization.fast_optimizer import FastOptimizer
import time

start_time = time.time()

optimizer = FastOptimizer(ROCKET_CONFIG, target_apogee=TARGET_APOGEE, tolerance=TOLERANCE)
result = optimizer.optimize_fast()

elapsed_time = time.time() - start_time

print("="*80)
print("OPTIMIZATION RESULTS")
print("="*80)
print()

print("Optimized Design:")
print(f"  Diameter: {result['diameter']:.4f} m ({result['diameter']*100:.2f} cm)")
print(f"  Nose Cone Length: {result['nose_length']:.4f} m")
print(f"  Body Length: {result['body_length']:.4f} m")
print(f"  Total Length: {result['nose_length'] + result['body_length']:.4f} m")
print(f"  Drag Coefficient (Cd): {result['cd']:.4f}")
print()

print("Performance:")
print(f"  Achieved Apogee: {result['apogee']:.2f} m")
print(f"  Target Apogee: {TARGET_APOGEE:.2f} m")
print(f"  Error: {result['error']:.2f} m ({result['error']/TARGET_APOGEE*100:.2f}%)")
print(f"  Maximum Mach: {result['max_mach']:.3f}")
print()

print(f"Optimization Time: {elapsed_time:.3f} seconds")
print(f"Iterations: {result['iterations']}")
print()

if result['converged']:
    print("STATUS: Converged successfully")
else:
    print("STATUS: Did not fully converge (but result is usable)")

print()
print("NOTE: This is a fast estimate (80% accuracy)")
print("For production use, run 'run_accurate_optimization.py'")
print()
print("="*80)
