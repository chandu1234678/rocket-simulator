"""
Feasibility Checker for Rocket Optimization
Pre-flight analysis to prevent wasted optimization time
Includes supersonic prevention and design suggestions
"""

import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from src.models.ideal_trajectory import IdealTrajectoryAnalyzer, IdealTrajectoryResult
from src.models.constants import SUPERSONIC_MACH_LIMIT


@dataclass
class FeasibilityResult:
    """Results from feasibility check"""
    is_feasible: bool
    reason: str
    ideal_apogee: float
    target_apogee: float
    max_mach_ideal: float
    is_supersonic: bool
    suggestions: Dict
    can_proceed: bool  # True if optimization should proceed


class FeasibilityChecker:
    """
    Pre-optimization feasibility checker
    
    Checks:
    1. Can target apogee be reached? (zero-drag check)
    2. Will rocket go supersonic? (M > 1.2)
    3. What changes are needed?
    
    Purpose:
    - Save time (2 seconds vs 20 minutes)
    - Prevent supersonic flight
    - Guide user to feasible designs
    """
    
    def __init__(self, supersonic_limit: float = SUPERSONIC_MACH_LIMIT):
        """
        Initialize checker
        
        Args:
            supersonic_limit: Mach number limit (default: from constants.SUPERSONIC_MACH_LIMIT)
        """
        self.supersonic_limit = supersonic_limit
        self.ideal_analyzer = IdealTrajectoryAnalyzer()
    
    def check_feasibility(
        self,
        thrust: float,
        burn_time: float,
        specific_impulse: float,
        mass_initial: float,
        mass_dry: float,
        target_apogee: float
    ) -> FeasibilityResult:
        """
        Comprehensive feasibility check
        
        Args:
            thrust: Thrust force (N)
            burn_time: Burn duration (s)
            specific_impulse: Specific impulse (s)
            mass_initial: Initial mass (kg)
            mass_dry: Dry mass (kg)
            target_apogee: Target altitude (m)
        
        Returns:
            FeasibilityResult with complete analysis
        
        Note:
            Temperature is calculated at burnout altitude using ISA model
            for accurate Mach number calculation
        """
        # Run ideal trajectory analysis
        # Temperature will be calculated at burnout altitude inside analyzer
        ideal_result = self.ideal_analyzer.analyze(
            thrust=thrust,
            burn_time=burn_time,
            specific_impulse=specific_impulse,
            mass_initial=mass_initial,
            mass_dry=mass_dry,
            target_apogee=target_apogee
        )
        
        # Check 1: Supersonic prevention (CRITICAL)
        if ideal_result.max_mach > self.supersonic_limit:
            suggestions = self._suggest_subsonic_design(
                thrust, burn_time, specific_impulse,
                mass_initial, mass_dry, ideal_result.max_mach
            )
            
            return FeasibilityResult(
                is_feasible=False,
                reason=f"SUPERSONIC: Max Mach {ideal_result.max_mach:.2f} exceeds limit {self.supersonic_limit}",
                ideal_apogee=ideal_result.max_apogee,
                target_apogee=target_apogee,
                max_mach_ideal=ideal_result.max_mach,
                is_supersonic=True,
                suggestions=suggestions,
                can_proceed=False
            )
        
        # Check 2: Altitude feasibility
        if not ideal_result.is_feasible:
            suggestions = self._suggest_higher_apogee(
                thrust, burn_time, specific_impulse,
                mass_initial, mass_dry, target_apogee, ideal_result
            )
            
            return FeasibilityResult(
                is_feasible=False,
                reason=f"INSUFFICIENT ALTITUDE: Ideal max {ideal_result.max_apogee:.0f}m < target {target_apogee:.0f}m",
                ideal_apogee=ideal_result.max_apogee,
                target_apogee=target_apogee,
                max_mach_ideal=ideal_result.max_mach,
                is_supersonic=False,
                suggestions=suggestions,
                can_proceed=False
            )
        
        # All checks passed
        return FeasibilityResult(
            is_feasible=True,
            reason="FEASIBLE: Target reachable without going supersonic",
            ideal_apogee=ideal_result.max_apogee,
            target_apogee=target_apogee,
            max_mach_ideal=ideal_result.max_mach,
            is_supersonic=False,
            suggestions={},
            can_proceed=True
        )
    
    def _suggest_subsonic_design(
        self,
        thrust: float,
        burn_time: float,
        specific_impulse: float,
        mass_initial: float,
        mass_dry: float,
        current_mach: float
    ) -> Dict:
        """
        Suggest changes to prevent supersonic flight
        
        Strategy: Reduce thrust, burn time, or impulse
        """
        # Calculate reduction factor needed
        # Mach is roughly proportional to sqrt(thrust)
        mach_ratio = self.supersonic_limit / current_mach
        reduction_factor = mach_ratio ** 2  # Square because v ~ sqrt(T)
        
        # Option 1: Reduce thrust
        new_thrust = thrust * reduction_factor * 0.9  # 10% safety margin
        
        # Option 2: Reduce burn time
        new_burn_time = burn_time * reduction_factor * 0.9
        
        # Option 3: Reduce specific impulse (less efficient propellant)
        new_isp = specific_impulse * reduction_factor * 0.9
        
        # Option 4: Increase mass (more drag)
        mass_increase = mass_initial * (1.0 / reduction_factor - 1.0)
        
        return {
            'type': 'SUPERSONIC_PREVENTION',
            'current_mach': current_mach,
            'limit_mach': self.supersonic_limit,
            'reduction_needed': 1.0 - reduction_factor,
            'options': {
                'thrust': {
                    'current': thrust,
                    'suggested': new_thrust,
                    'reduction': thrust - new_thrust,
                    'message': f'Reduce thrust from {thrust:.1f}N to {new_thrust:.1f}N'
                },
                'burn_time': {
                    'current': burn_time,
                    'suggested': new_burn_time,
                    'reduction': burn_time - new_burn_time,
                    'message': f'Reduce burn time from {burn_time:.1f}s to {new_burn_time:.1f}s'
                },
                'specific_impulse': {
                    'current': specific_impulse,
                    'suggested': new_isp,
                    'reduction': specific_impulse - new_isp,
                    'message': f'Reduce Isp from {specific_impulse:.0f}s to {new_isp:.0f}s'
                },
                'mass': {
                    'current': mass_initial,
                    'suggested': mass_initial + mass_increase,
                    'increase': mass_increase,
                    'message': f'Increase mass by {mass_increase:.2f}kg (adds drag)'
                }
            }
        }
    
    def _suggest_higher_apogee(
        self,
        thrust: float,
        burn_time: float,
        specific_impulse: float,
        mass_initial: float,
        mass_dry: float,
        target_apogee: float,
        ideal_result: IdealTrajectoryResult
    ) -> Dict:
        """
        Suggest changes to reach higher apogee
        
        Strategy: Increase thrust, burn time, or reduce mass
        """
        deficit = target_apogee - ideal_result.max_apogee
        deficit_ratio = deficit / ideal_result.max_apogee
        
        # Option 1: Increase thrust
        thrust_factor = 1.0 + deficit_ratio * 1.5
        new_thrust = thrust * thrust_factor
        
        # Option 2: Increase burn time
        burn_time_factor = 1.0 + deficit_ratio * 1.2
        new_burn_time = burn_time * burn_time_factor
        
        # Option 3: Increase specific impulse
        isp_factor = 1.0 + deficit_ratio * 1.0
        new_isp = specific_impulse * isp_factor
        
        # Option 4: Reduce mass
        mass_factor = 1.0 - deficit_ratio * 0.5
        new_mass = mass_initial * mass_factor
        mass_reduction = mass_initial - new_mass
        
        return {
            'type': 'ALTITUDE_INCREASE',
            'current_apogee': ideal_result.max_apogee,
            'target_apogee': target_apogee,
            'deficit': deficit,
            'options': {
                'thrust': {
                    'current': thrust,
                    'suggested': new_thrust,
                    'increase': new_thrust - thrust,
                    'message': f'Increase thrust from {thrust:.1f}N to {new_thrust:.1f}N'
                },
                'burn_time': {
                    'current': burn_time,
                    'suggested': new_burn_time,
                    'increase': new_burn_time - burn_time,
                    'message': f'Increase burn time from {burn_time:.1f}s to {new_burn_time:.1f}s'
                },
                'specific_impulse': {
                    'current': specific_impulse,
                    'suggested': new_isp,
                    'increase': new_isp - specific_impulse,
                    'message': f'Increase Isp from {specific_impulse:.0f}s to {new_isp:.0f}s'
                },
                'mass': {
                    'current': mass_initial,
                    'suggested': new_mass,
                    'reduction': mass_reduction,
                    'message': f'Reduce mass by {mass_reduction:.2f}kg'
                }
            }
        }
    
    def print_feasibility(self, result: FeasibilityResult):
        """Print formatted feasibility results"""
        print("\n" + "="*80)
        print("PRE-FLIGHT FEASIBILITY CHECK")
        print("="*80)
        
        print(f"\n TARGET:")
        print(f"  Target Apogee:     {result.target_apogee:.2f} m")
        print(f"  Ideal Max Apogee:  {result.ideal_apogee:.2f} m")
        print(f"  Max Mach (ideal):  {result.max_mach_ideal:.3f}")
        print(f"  Supersonic Limit:  {self.supersonic_limit:.1f}")
        
        print(f"\n RESULT:")
        if result.can_proceed:
            print(f"  Status:             FEASIBLE")
            print(f"  Reason:            {result.reason}")
            print(f"\n   Can proceed with optimization")
            print(f"  Note: Real apogee will be ~70-80% of ideal due to drag")
        else:
            print(f"  Status:             NOT FEASIBLE")
            print(f"  Reason:            {result.reason}")
            print(f"\n   Cannot proceed - design changes required")
            
            if result.is_supersonic:
                print(f"\n  SUPERSONIC WARNING:")
                print(f"  Current Mach: {result.max_mach_ideal:.2f}")
                print(f"  Limit: {self.supersonic_limit:.1f}")
                print(f"  NEVER allow supersonic flight!")
            
            self._print_suggestions(result.suggestions)
        
        print("\n" + "="*80)
    
    def _print_suggestions(self, suggestions: Dict):
        """Print formatted suggestions"""
        if not suggestions:
            return
        
        print(f"\n SUGGESTIONS TO FIX:")
        
        if suggestions['type'] == 'SUPERSONIC_PREVENTION':
            print(f"\n  To prevent supersonic flight, choose ONE:")
            print(f"  (Reduce by {suggestions['reduction_needed']*100:.1f}%)")
        else:
            print(f"\n  To reach target altitude, choose ONE:")
        
        for i, (key, option) in enumerate(suggestions['options'].items(), 1):
            print(f"\n  Option {i}: {option['message']}")
            if 'reduction' in option:
                print(f"            Change: -{option['reduction']:.2f}")
            elif 'increase' in option:
                print(f"            Change: +{option['increase']:.2f}")


def quick_feasibility_check(
    thrust: float,
    burn_time: float,
    specific_impulse: float,
    mass_initial: float,
    mass_dry: float,
    target_apogee: float
) -> Tuple[bool, str]:
    """
    Quick feasibility check
    
    Returns:
        (can_proceed, reason)
    """
    checker = FeasibilityChecker()
    result = checker.check_feasibility(
        thrust, burn_time, specific_impulse,
        mass_initial, mass_dry, target_apogee
    )
    return result.can_proceed, result.reason


# Example usage
if __name__ == "__main__":
    checker = FeasibilityChecker()
    
    # Test case 1: Feasible design
    print("TEST 1: Feasible Design")
    result1 = checker.check_feasibility(
        thrust=747.1,
        burn_time=1.8,
        specific_impulse=180,
        mass_initial=2.76,
        mass_dry=2.0,
        target_apogee=500.0
    )
    checker.print_feasibility(result1)
    
    # Test case 2: Supersonic design
    print("\n\nTEST 2: Supersonic Design (should fail)")
    result2 = checker.check_feasibility(
        thrust=2000.0,  # Too much thrust
        burn_time=3.0,
        specific_impulse=250,
        mass_initial=2.76,
        mass_dry=2.0,
        target_apogee=1000.0
    )
    checker.print_feasibility(result2)
    
    # Test case 3: Insufficient altitude
    print("\n\nTEST 3: Insufficient Altitude (should fail)")
    result3 = checker.check_feasibility(
        thrust=300.0,  # Too little thrust
        burn_time=1.0,
        specific_impulse=150,
        mass_initial=2.76,
        mass_dry=2.0,
        target_apogee=2000.0
    )
    checker.print_feasibility(result3)
