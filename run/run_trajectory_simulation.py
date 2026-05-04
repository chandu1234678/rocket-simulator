"""
Trajectory Simulation
Simulate your rocket's flight path with given parameters
"""

print("="*80)
print("ROCKET TRAJECTORY SIMULATION")
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
    'diameter': 0.1,             # Body diameter in meters (m)
    'nose_cone_length': 0.3,     # Nose cone length in meters (m)
    'body_length': 1.0,          # Body tube length in meters (m)
    'drag_coefficient': 0.35,    # Drag coefficient (Cd)
}

# ============================================================================
# RUNNING SIMULATION
# ============================================================================

print("Simulating rocket trajectory...")
print()
print("Configuration:")
print(f"  Thrust: {ROCKET_CONFIG['thrust']} N")
print(f"  Burn Time: {ROCKET_CONFIG['burn_time']} s")
print(f"  Specific Impulse: {ROCKET_CONFIG['specific_impulse']} s")
print(f"  Initial Mass: {ROCKET_CONFIG['mass_initial']} kg")
print(f"  Dry Mass: {ROCKET_CONFIG['mass_dry']} kg")
print(f"  Diameter: {ROCKET_CONFIG['diameter']} m ({ROCKET_CONFIG['diameter']*100:.1f} cm)")
print(f"  Nose Cone Length: {ROCKET_CONFIG['nose_cone_length']} m")
print(f"  Body Length: {ROCKET_CONFIG['body_length']} m")
print(f"  Total Length: {ROCKET_CONFIG['nose_cone_length'] + ROCKET_CONFIG['body_length']} m")
print(f"  Drag Coefficient: {ROCKET_CONFIG['drag_coefficient']}")
print()

from src.core.simulation import Simulation
from src.core.config import Config

config = Config(
    thrust=ROCKET_CONFIG['thrust'],
    burn_time=ROCKET_CONFIG['burn_time'],
    specific_impulse=ROCKET_CONFIG['specific_impulse'],
    mass_initial=ROCKET_CONFIG['mass_initial'],
    mass_dry=ROCKET_CONFIG['mass_dry'],
    diameter=ROCKET_CONFIG['diameter'],
    nose_cone_length=ROCKET_CONFIG['nose_cone_length'],
    body_length=ROCKET_CONFIG['body_length'],
    drag_coefficient=ROCKET_CONFIG['drag_coefficient']
)

sim = Simulation(config)
result = sim.run()

print("="*80)
print("SIMULATION RESULTS")
print("="*80)
print()

print("Flight Performance:")
print(f"  Maximum Altitude: {result['max_altitude']:.2f} m")
print(f"  Maximum Velocity: {result['max_velocity']:.2f} m/s")
print(f"  Maximum Acceleration: {result['max_acceleration']:.2f} m/s²")
print(f"  Maximum Mach Number: {result['max_mach']:.3f}")
print()

print("Key Events:")
print(f"  Burnout Time: {ROCKET_CONFIG['burn_time']:.2f} s")
print(f"  Time to Apogee: {result['time_to_apogee']:.2f} s")
print(f"  Total Flight Time: {result['total_time']:.2f} s")
print()

print("Burnout Conditions:")
print(f"  Altitude at Burnout: {result['burnout_altitude']:.2f} m")
print(f"  Velocity at Burnout: {result['burnout_velocity']:.2f} m/s")
print()

if result['max_mach'] >= 1.2:
    print("WARNING: Rocket goes supersonic!")
    print(f"  Maximum Mach: {result['max_mach']:.3f}")
    print("  This is dangerous for amateur rockets!")
    print("  Consider reducing thrust or increasing drag.")
elif result['max_mach'] >= 0.8:
    print("CAUTION: Rocket approaches transonic speeds")
    print(f"  Maximum Mach: {result['max_mach']:.3f}")
    print("  Design should account for transonic effects.")
else:
    print("SAFE: Rocket remains subsonic")
    print(f"  Maximum Mach: {result['max_mach']:.3f}")

print()
print("="*80)
print("TRAJECTORY DATA")
print("="*80)
print()

trajectory = result['trajectory']
print(f"Total data points: {len(trajectory)}")
print()
print("Sample trajectory (every 10th point):")
print(f"{'Time (s)':<10} {'Altitude (m)':<15} {'Velocity (m/s)':<15} {'Mach':<10}")
print("-"*50)

for i in range(0, len(trajectory), max(1, len(trajectory)//10)):
    point = trajectory[i]
    print(f"{point.t:<10.2f} {point.h:<15.2f} {point.v:<15.2f} {point.M:<10.3f}")

print()
print("="*80)
print("Simulation complete!")
print("="*80)
