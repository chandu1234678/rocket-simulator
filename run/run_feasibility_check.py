"""
Feasibility Check Only
Quick check to see if your rocket design is safe and can reach target altitude
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*80)
print("ROCKET FEASIBILITY CHECK")
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

# ============================================================================
# RUNNING FEASIBILITY CHECK
# ============================================================================

print("Checking your rocket design...")
print()
print("Configuration:")
print(f"  Thrust: {ROCKET_CONFIG['thrust']} N")
print(f"  Burn Time: {ROCKET_CONFIG['burn_time']} s")
print(f"  Specific Impulse: {ROCKET_CONFIG['specific_impulse']} s")
print(f"  Initial Mass: {ROCKET_CONFIG['mass_initial']} kg")
print(f"  Dry Mass: {ROCKET_CONFIG['mass_dry']} kg")
print(f"  Target Apogee: {TARGET_APOGEE} m")
print()

from src.optimization.feasibility_checker import FeasibilityChecker

checker = FeasibilityChecker(supersonic_limit=1.2)
result = checker.check_feasibility(
    thrust=ROCKET_CONFIG['thrust'],
    burn_time=ROCKET_CONFIG['burn_time'],
    specific_impulse=ROCKET_CONFIG['specific_impulse'],
    mass_initial=ROCKET_CONFIG['mass_initial'],
    mass_dry=ROCKET_CONFIG['mass_dry'],
    target_apogee=TARGET_APOGEE
)

print("="*80)
print("RESULTS")
print("="*80)
print()

if result.can_proceed:
    print("STATUS: FEASIBLE")
    print()
    print("Your rocket design is safe and can reach the target!")
    print()
    print("Details:")
    print(f"  Target Altitude: {TARGET_APOGEE:.0f} m")
    print(f"  Ideal Maximum Altitude: {result.ideal_apogee:.0f} m")
    print(f"  Maximum Mach Number: {result.max_mach_ideal:.2f}")
    print(f"  Supersonic Limit: 1.2")
    print()
    print("You can proceed with optimization.")
    
else:
    print("STATUS: NOT FEASIBLE")
    print()
    print(f"Problem: {result.reason}")
    print()
    
    if result.is_supersonic:
        print("DANGER: Your rocket will go supersonic!")
        print("Supersonic flight is dangerous for amateur rockets.")
        print()
        print(f"Your rocket will reach Mach {result.max_mach_ideal:.2f}")
        print(f"Safe limit is Mach 1.2")
        print()
        print("To fix this, you must REDUCE one of the following:")
        print()
        
        for key, option in result.suggestions['options'].items():
            print(f"  {option['message']}")
            
    else:
        print("Your rocket cannot reach the target altitude.")
        print()
        print(f"Your rocket can reach: {result.ideal_apogee:.0f} m")
        print(f"Target altitude: {TARGET_APOGEE:.0f} m")
        print(f"Shortfall: {TARGET_APOGEE - result.ideal_apogee:.0f} m")
        print()
        print("To fix this, you must INCREASE one of the following:")
        print()
        
        for key, option in result.suggestions['options'].items():
            print(f"  {option['message']}")
    
    print()
    print("Modify your parameters above and run this script again.")

print()
print("="*80)
