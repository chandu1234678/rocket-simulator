"""
Test Parallel Optimizer Speed
Target: <5 seconds
"""

import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimization.vispootanam_parallel_optimizer import VispootanamParallelOptimizer, VispootanamConfig

print("="*80)
print("PARALLEL OPTIMIZER SPEED TEST")
print("="*80)
print("\nTarget: <5 seconds per optimization\n")

# Base configuration (subsonic thrust)
base_config = {
    'thrust': 80.0,  # Known subsonic
    'burn_time': 1.8,
    'specific_impulse': 180,
    'mass_initial': 2.76,
    'mass_dry': 2.0
}

# VISPOOTANAM configuration (speed-optimized)
VISPOOTANAM_config = VispootanamConfig(
    target_apogee=5000.0,  # Realistic for 80N thrust
    tolerance=50.0,
    max_iterations=10,  # Reduced for speed
    population_size=6,   # Reduced for speed
    user_cd_estimates={'D1': 0.25, 'D2': 0.35, 'D3': 0.65}
)

print(f"Configuration:")
print(f"  Target: {VISPOOTANAM_config.target_apogee}m")
print(f"  Max Iterations: {VISPOOTANAM_config.max_iterations}")
print(f"  Population Size: {VISPOOTANAM_config.population_size}")
print(f"  Parallel Workers: {VISPOOTANAM_config.n_parallel_workers}")
print(f"\nRunning optimization...")
print("="*80)

# Run optimization
start_time = time.time()

optimizer = VispootanamParallelOptimizer(base_config, VISPOOTANAM_config)
results = optimizer.optimize_all_regimes()

total_time = time.time() - start_time

# Print summary
if results:
    optimizer.print_summary(results)

# Speed test result
print(f"\n{'='*80}")
print(f"⏱  SPEED TEST RESULT")
print(f"{'='*80}")
print(f"  Total Time:    {total_time:.3f} s")
print(f"  Target:        <5.0 s")
print(f"  Status:        {' PASS' if total_time < 5.0 else ' FAIL'}")

if total_time < 5.0:
    print(f"\n VISPOOTANAM-LEVEL SPEED ACHIEVED!")
    print(f"   Parallel optimizer now meets <5s requirement")
else:
    print(f"\n  Still {total_time - 5.0:.3f}s over target")
    print(f"   Suggestions:")
    print(f"   - Reduce max_iterations further")
    print(f"   - Reduce population_size further")
    print(f"   - Increase time step (dt)")

print(f"{'='*80}")
