"""Zero-drag ideal trajectory analyzer for feasibility checks."""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class IdealTrajectoryResult:
    """Results from ideal (zero-drag) trajectory analysis"""
    max_apogee: float           # Maximum altitude (m)
    max_velocity: float         # Maximum velocity (m/s)
    max_acceleration: float     # Maximum acceleration (m/s²)
    max_mach: float            # Maximum Mach number
    burnout_altitude: float    # Altitude at burnout (m)
    burnout_velocity: float    # Velocity at burnout (m/s)
    time_to_apogee: float      # Time to reach apogee (s)
    is_feasible: bool          # Can reach target (if provided)
    margin: float              # Altitude margin above target (m)


class IdealTrajectoryAnalyzer:
    """
    Analyzes rocket trajectory without atmospheric drag
    
    Purpose:
    - Quick feasibility check (100x faster than full simulation)
    - Upper bound on performance
    - Guidance for optimization
    
    Physics:
    - Thrust phase: dv/dt = T/m - g
    - Coast phase: dv/dt = -g
    - No drag, no atmosphere
    """
    
    def __init__(self, g: float = 9.80665):
        """
        Initialize analyzer
        
        Args:
            g: Gravitational acceleration (m/s²)
        """
        self.g = g
    
    def analyze(
        self,
        thrust: float,
        burn_time: float,
        specific_impulse: float,
        mass_initial: float,
        mass_dry: float,
        target_apogee: float = None,
        temperature: float = 287.0
    ) -> IdealTrajectoryResult:
        """
        Analyze ideal trajectory (no drag)
        
        Args:
            thrust: Thrust force (N)
            burn_time: Burn duration (s)
            specific_impulse: Specific impulse (s)
            mass_initial: Initial mass (kg)
            mass_dry: Dry mass after burnout (kg)
            target_apogee: Target altitude for feasibility check (m)
            temperature: Temperature for Mach calculation (K)
        
        Returns:
            IdealTrajectoryResult with all performance metrics
        """
        # Validate inputs
        if mass_initial <= mass_dry:
            raise ValueError("Initial mass must be greater than dry mass")
        if thrust <= 0 or burn_time <= 0:
            raise ValueError("Thrust and burn time must be positive")
        
        # Mass flow rate
        mdot = thrust / (specific_impulse * self.g)
        propellant_mass = mass_initial - mass_dry
        
        # Check if burn time is consistent with propellant mass
        required_propellant = mdot * burn_time
        if abs(required_propellant - propellant_mass) > 0.01:
            # Adjust burn time to match propellant mass
            burn_time = propellant_mass / mdot
        
        # Phase 1: Powered ascent (with thrust)
        v_burnout, h_burnout, a_max = self._powered_ascent(
            thrust, burn_time, mass_initial, mass_dry, mdot
        )
        
        # Phase 2: Coast to apogee (no thrust, no drag)
        h_apogee, t_coast = self._coast_to_apogee(v_burnout, h_burnout)
        
        # Total time to apogee
        t_apogee = burn_time + t_coast
        
        # Calculate max Mach number
        # Speed of sound: a = sqrt(gamma * R * T)
        # For air: gamma = 1.4, R = 287 J/(kg·K)
        speed_of_sound = np.sqrt(1.4 * 287.0 * temperature)
        max_mach = v_burnout / speed_of_sound
        
        # Feasibility check
        is_feasible = True
        margin = 0.0
        if target_apogee is not None:
            is_feasible = h_apogee >= target_apogee
            margin = h_apogee - target_apogee
        
        return IdealTrajectoryResult(
            max_apogee=h_apogee,
            max_velocity=v_burnout,
            max_acceleration=a_max,
            max_mach=max_mach,
            burnout_altitude=h_burnout,
            burnout_velocity=v_burnout,
            time_to_apogee=t_apogee,
            is_feasible=is_feasible,
            margin=margin
        )
    
    def _powered_ascent(
        self,
        thrust: float,
        burn_time: float,
        mass_initial: float,
        mass_dry: float,
        mdot: float
    ) -> Tuple[float, float, float]:
        """
        Simulate powered ascent phase
        
        Uses Tsiolkovsky rocket equation for velocity
        Integrates for altitude
        
        Returns:
            (burnout_velocity, burnout_altitude, max_acceleration)
        """
        # Tsiolkovsky rocket equation (ideal case)
        # Δv = v_e * ln(m0/mf) - g*t
        # where v_e = Isp * g
        
        v_exhaust = thrust / mdot  # Effective exhaust velocity
        mass_ratio = mass_initial / mass_dry
        
        # Velocity at burnout (accounting for gravity loss)
        v_burnout = v_exhaust * np.log(mass_ratio) - self.g * burn_time
        
        # Altitude at burnout (numerical integration)
        # Use average velocity approximation
        # More accurate: integrate v(t) = v_e*ln(m0/(m0-mdot*t)) - g*t
        
        dt = 0.01  # Small timestep for accuracy
        t = 0.0
        h = 0.0
        v = 0.0
        a_max = 0.0
        
        while t < burn_time:
            m = mass_initial - mdot * t
            a = thrust / m - self.g
            a_max = max(a_max, a)
            
            v += a * dt
            h += v * dt
            t += dt
        
        return v_burnout, h, a_max
    
    def _coast_to_apogee(self, v_initial: float, h_initial: float) -> Tuple[float, float]:
        """
        Simulate coast phase to apogee (no thrust, no drag)
        
        Simple kinematics:
        v² = v0² - 2*g*Δh
        At apogee: v = 0
        
        Returns:
            (apogee_altitude, coast_time)
        """
        # Height gained during coast
        delta_h = (v_initial ** 2) / (2 * self.g)
        
        # Total apogee
        h_apogee = h_initial + delta_h
        
        # Time to coast to apogee
        t_coast = v_initial / self.g
        
        return h_apogee, t_coast
    
    def suggest_improvements(
        self,
        current_result: IdealTrajectoryResult,
        target_apogee: float,
        current_thrust: float,
        current_burn_time: float,
        current_mass_initial: float,
        current_mass_dry: float,
        current_isp: float
    ) -> Dict[str, any]:
        """
        Suggest improvements to reach target apogee
        
        Returns dictionary with suggestions:
        - required_thrust: Thrust needed (keeping other params constant)
        - required_burn_time: Burn time needed
        - required_mass_reduction: Mass reduction needed
        """
        if current_result.is_feasible:
            return {
                'feasible': True,
                'message': f'Target {target_apogee:.0f}m is achievable (ideal: {current_result.max_apogee:.0f}m)'
            }
        
        deficit = target_apogee - current_result.max_apogee
        
        # Estimate required changes (simplified)
        # These are rough estimates based on rocket equation
        
        # Option 1: Increase thrust
        thrust_factor = 1.0 + (deficit / current_result.max_apogee) * 1.5
        required_thrust = current_thrust * thrust_factor
        
        # Option 2: Increase burn time
        burn_time_factor = 1.0 + (deficit / current_result.max_apogee) * 1.2
        required_burn_time = current_burn_time * burn_time_factor
        
        # Option 3: Reduce mass
        mass_factor = 1.0 - (deficit / current_result.max_apogee) * 0.8
        required_mass = current_mass_initial * mass_factor
        mass_reduction = current_mass_initial - required_mass
        
        return {
            'feasible': False,
            'deficit': deficit,
            'current_apogee': current_result.max_apogee,
            'target_apogee': target_apogee,
            'suggestions': {
                'thrust': {
                    'current': current_thrust,
                    'required': required_thrust,
                    'increase': required_thrust - current_thrust,
                    'factor': thrust_factor
                },
                'burn_time': {
                    'current': current_burn_time,
                    'required': required_burn_time,
                    'increase': required_burn_time - current_burn_time,
                    'factor': burn_time_factor
                },
                'mass': {
                    'current': current_mass_initial,
                    'required': required_mass,
                    'reduction': mass_reduction,
                    'factor': mass_factor
                }
            },
            'message': f'Target {target_apogee:.0f}m NOT achievable with current design (ideal max: {current_result.max_apogee:.0f}m)'
        }
    
    def print_analysis(self, result: IdealTrajectoryResult, target_apogee: float = None):
        """Print formatted analysis results"""
        print("\n" + "="*80)
        print("IDEAL TRAJECTORY ANALYSIS (Zero-Drag)")
        print("="*80)
        
        print(f"\n PERFORMANCE (Upper Bounds):")
        print(f"  Max Apogee:        {result.max_apogee:.2f} m")
        print(f"  Max Velocity:      {result.max_velocity:.2f} m/s")
        print(f"  Max Acceleration:  {result.max_acceleration:.2f} m/s²")
        print(f"  Max Mach:          {result.max_mach:.3f}")
        
        print(f"\n BURNOUT CONDITIONS:")
        print(f"  Altitude:          {result.burnout_altitude:.2f} m")
        print(f"  Velocity:          {result.burnout_velocity:.2f} m/s")
        
        print(f"\n⏱  TIMING:")
        print(f"  Time to Apogee:    {result.time_to_apogee:.2f} s")
        
        if target_apogee is not None:
            print(f"\n FEASIBILITY CHECK:")
            print(f"  Target Apogee:     {target_apogee:.2f} m")
            print(f"  Ideal Max Apogee:  {result.max_apogee:.2f} m")
            print(f"  Margin:            {result.margin:+.2f} m")
            
            if result.is_feasible:
                print(f"  Status:             FEASIBLE")
                print(f"\n  Note: Real apogee will be lower due to drag")
            else:
                print(f"  Status:             NOT FEASIBLE")
                print(f"\n  Even without drag, cannot reach target!")
                print(f"  Need to increase thrust, burn time, or reduce mass")
        
        print("\n" + "="*80)


def quick_feasibility_check(
    thrust: float,
    burn_time: float,
    specific_impulse: float,
    mass_initial: float,
    mass_dry: float,
    target_apogee: float
) -> bool:
    """
    Quick yes/no feasibility check
    
    Returns:
        True if target is theoretically achievable (without drag)
        False if impossible even in ideal conditions
    """
    analyzer = IdealTrajectoryAnalyzer()
    result = analyzer.analyze(
        thrust, burn_time, specific_impulse,
        mass_initial, mass_dry, target_apogee
    )
    return result.is_feasible


# Example usage
if __name__ == "__main__":
    # Test case
    analyzer = IdealTrajectoryAnalyzer()
    
    result = analyzer.analyze(
        thrust=747.1,
        burn_time=1.8,
        specific_impulse=180,
        mass_initial=2.76,
        mass_dry=2.0,
        target_apogee=500.0
    )
    
    analyzer.print_analysis(result, target_apogee=500.0)
    
    # Get suggestions if not feasible
    suggestions = analyzer.suggest_improvements(
        result, 500.0, 747.1, 1.8, 2.76, 2.0, 180
    )
    
    if not suggestions['feasible']:
        print("\n SUGGESTIONS:")
        print(f"  Option 1: Increase thrust to {suggestions['suggestions']['thrust']['required']:.1f}N")
        print(f"  Option 2: Increase burn time to {suggestions['suggestions']['burn_time']['required']:.1f}s")
        print(f"  Option 3: Reduce mass by {suggestions['suggestions']['mass']['reduction']:.2f}kg")
