"""
Flight Regime Analyzer
Analyzes flight conditions including supersonic regime detection
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FlightRegimeAnalysis:
    """Analysis of flight regime conditions"""
    max_apogee: float
    max_thrust: float
    max_velocity: float
    max_mach: float
    velocity_at_apogee: float
    
    # Zero-drag ideal conditions
    ideal_max_apogee: float
    ideal_max_velocity: float
    ideal_max_mach: float
    
    # Flight regime classification
    is_supersonic: bool  # Mach > 1.2
    is_transonic: bool   # 0.8 < Mach < 1.2
    is_subsonic: bool    # Mach < 0.8
    
    # Recommendations (if supersonic)
    recommendations: Optional[Dict[str, any]] = None
    
    def __str__(self):
        regime = "SUPERSONIC" if self.is_supersonic else "TRANSONIC" if self.is_transonic else "SUBSONIC"
        return f"Flight Regime: {regime}, Max Mach: {self.max_mach:.2f}"


class FlightRegimeAnalyzer:
    """
    Analyzes flight regime and provides recommendations
    """
    
    SUPERSONIC_THRESHOLD = 1.2
    TRANSONIC_LOWER = 0.8
    TRANSONIC_UPPER = 1.2
    
    def __init__(self, gamma: float = 1.4, R: float = 287.05):
        """
        Initialize analyzer
        
        Args:
            gamma: Specific heat ratio (default: 1.4 for air)
            R: Specific gas constant (J/kg·K, default: 287.05 for air)
        """
        self.gamma = gamma
        self.R = R
    
    def calculate_speed_of_sound(self, temperature: float) -> float:
        """
        Calculate speed of sound: a = sqrt(gamma * R * T)
        
        Args:
            temperature: Temperature in Kelvin
            
        Returns:
            Speed of sound in m/s
        """
        return np.sqrt(self.gamma * self.R * temperature)
    
    def calculate_mach_number(self, velocity: float, temperature: float) -> float:
        """
        Calculate Mach number: M = v / a
        
        Args:
            velocity: Velocity in m/s
            temperature: Temperature in Kelvin
            
        Returns:
            Mach number
        """
        a = self.calculate_speed_of_sound(temperature)
        return velocity / a if a > 0 else 0.0
    
    def simulate_zero_drag_trajectory(
        self,
        mass_initial: float,
        mass_dry: float,
        thrust: float,
        burn_time: float,
        altitude_initial: float = 0.0,
        temperature_initial: float = 288.15,
        dt: float = 0.01
    ) -> Dict[str, float]:
        """
        Simulate ideal trajectory with zero drag
        
        Args:
            mass_initial: Initial mass (kg)
            mass_dry: Dry mass after burnout (kg)
            thrust: Thrust force (N)
            burn_time: Burn time (s)
            altitude_initial: Initial altitude (m)
            temperature_initial: Initial temperature (K)
            dt: Time step (s)
            
        Returns:
            Dictionary with max apogee, velocity, and Mach number
        """
        g = 9.80665  # m/s²
        
        # Mass flow rate
        propellant_mass = mass_initial - mass_dry
        mdot = propellant_mass / burn_time if burn_time > 0 else 0
        
        # Initial conditions
        h = altitude_initial
        v = 0.0
        m = mass_initial
        t = 0.0
        
        max_velocity = 0.0
        max_mach = 0.0
        max_altitude = h
        
        # Simulation loop
        while h >= altitude_initial and t < 300.0:  # Max 5 minutes
            # Temperature at altitude (simple lapse rate)
            T = temperature_initial - 0.0065 * h
            T = max(T, 216.65)  # Minimum temperature
            
            # Thrust phase
            if t < burn_time:
                thrust_force = thrust
                mass_rate = -mdot
            else:
                thrust_force = 0.0
                mass_rate = 0.0
            
            # Acceleration (zero drag)
            a = (thrust_force / m) - g if m > 0 else -g
            
            # Update state
            v += a * dt
            h += v * dt
            m += mass_rate * dt
            t += dt
            
            # Ensure mass doesn't go below dry mass
            m = max(m, mass_dry)
            
            # Track maximums
            max_velocity = max(max_velocity, v)
            max_altitude = max(max_altitude, h)
            
            # Calculate Mach number
            mach = self.calculate_mach_number(v, T)
            max_mach = max(max_mach, mach)
            
            # Stop if descending below initial altitude
            if h < altitude_initial and t > burn_time:
                break
        
        return {
            'max_apogee': max_altitude,
            'max_velocity': max_velocity,
            'max_mach': max_mach
        }
    
    def analyze_trajectory(
        self,
        trajectory_data: Dict[str, np.ndarray],
        config: Dict[str, any]
    ) -> FlightRegimeAnalysis:
        """
        Analyze trajectory and determine flight regime
        
        Args:
            trajectory_data: Dictionary with 't', 'h', 'v', 'M', 'T' arrays
            config: Configuration dictionary with rocket parameters
            
        Returns:
            FlightRegimeAnalysis object
        """
        # Extract data
        altitudes = trajectory_data.get('h', np.array([]))
        velocities = trajectory_data.get('v', np.array([]))
        mach_numbers = trajectory_data.get('M', np.array([]))
        thrusts = trajectory_data.get('T', np.array([]))
        
        # Calculate maximums
        max_apogee = np.max(altitudes) if len(altitudes) > 0 else 0.0
        max_velocity = np.max(velocities) if len(velocities) > 0 else 0.0
        max_mach = np.max(mach_numbers) if len(mach_numbers) > 0 else 0.0
        max_thrust = np.max(thrusts) if len(thrusts) > 0 else 0.0
        
        # Velocity at apogee
        apogee_idx = np.argmax(altitudes) if len(altitudes) > 0 else 0
        velocity_at_apogee = velocities[apogee_idx] if len(velocities) > apogee_idx else 0.0
        
        # Simulate zero-drag conditions
        ideal_results = self.simulate_zero_drag_trajectory(
            mass_initial=config.get('mass_initial', 10.0),
            mass_dry=config.get('mass_dry', 8.0),
            thrust=config.get('thrust_max', 500.0),
            burn_time=config.get('burn_time', 2.0),
            altitude_initial=config.get('altitude_initial', 0.0),
            temperature_initial=config.get('temperature_initial', 288.15)
        )
        
        # Classify flight regime
        is_supersonic = max_mach > self.SUPERSONIC_THRESHOLD
        is_transonic = self.TRANSONIC_LOWER < max_mach <= self.TRANSONIC_UPPER
        is_subsonic = max_mach <= self.TRANSONIC_LOWER
        
        # Generate recommendations if supersonic
        recommendations = None
        if is_supersonic:
            recommendations = self._generate_recommendations(
                max_mach=max_mach,
                max_velocity=max_velocity,
                max_thrust=max_thrust,
                config=config
            )
        
        return FlightRegimeAnalysis(
            max_apogee=max_apogee,
            max_thrust=max_thrust,
            max_velocity=max_velocity,
            max_mach=max_mach,
            velocity_at_apogee=velocity_at_apogee,
            ideal_max_apogee=ideal_results['max_apogee'],
            ideal_max_velocity=ideal_results['max_velocity'],
            ideal_max_mach=ideal_results['max_mach'],
            is_supersonic=is_supersonic,
            is_transonic=is_transonic,
            is_subsonic=is_subsonic,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        max_mach: float,
        max_velocity: float,
        max_thrust: float,
        config: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Generate recommendations for supersonic flight
        
        Args:
            max_mach: Maximum Mach number achieved
            max_velocity: Maximum velocity (m/s)
            max_thrust: Maximum thrust (N)
            config: Configuration dictionary
            
        Returns:
            Dictionary with recommendations
        """
        current_thrust = config.get('thrust_max', 500.0)
        current_burn_time = config.get('burn_time', 2.0)
        current_isp = config.get('specific_impulse', 180.0)
        
        # Calculate reduction factors to stay subsonic
        # Target: Mach 0.7 (safely subsonic)
        target_mach = 0.7
        reduction_factor = target_mach / max_mach
        
        # Recommended thrust (reduce to stay subsonic)
        recommended_thrust = current_thrust * reduction_factor
        
        # Recommended burn time (can be increased to maintain total impulse)
        total_impulse = current_thrust * current_burn_time
        recommended_burn_time = total_impulse / recommended_thrust
        
        # Alternative: Reduce total impulse
        alternative_impulse = total_impulse * reduction_factor
        alternative_burn_time = current_burn_time * reduction_factor
        
        return {
            'status': 'SUPERSONIC_DETECTED',
            'max_mach_achieved': max_mach,
            'max_velocity_achieved': max_velocity,
            'recommendation_type': 'REDUCE_THRUST_OR_IMPULSE',
            
            'option_1': {
                'description': 'Reduce thrust, maintain total impulse',
                'recommended_thrust': recommended_thrust,
                'recommended_burn_time': recommended_burn_time,
                'recommended_specific_impulse': current_isp,
                'total_impulse': total_impulse,
                'reduction_factor': reduction_factor
            },
            
            'option_2': {
                'description': 'Reduce total impulse, maintain burn time',
                'recommended_thrust': recommended_thrust,
                'recommended_burn_time': current_burn_time,
                'recommended_specific_impulse': current_isp,
                'total_impulse': alternative_impulse,
                'reduction_factor': reduction_factor
            },
            
            'option_3': {
                'description': 'Reduce both thrust and burn time proportionally',
                'recommended_thrust': recommended_thrust,
                'recommended_burn_time': alternative_burn_time,
                'recommended_specific_impulse': current_isp,
                'total_impulse': alternative_impulse,
                'reduction_factor': reduction_factor
            },
            
            'warnings': [
                f'Rocket exceeded supersonic threshold (Mach {self.SUPERSONIC_THRESHOLD})',
                f'Maximum Mach number: {max_mach:.2f}',
                'Supersonic flight requires advanced aerodynamic design',
                'Consider structural reinforcement for high dynamic pressure',
                'Transonic drag spike may cause instability'
            ],
            
            'design_suggestions': [
                'Use a more streamlined nose cone (Von Karman or Haack series)',
                'Increase fin size for stability at high speeds',
                'Consider using a smaller diameter to reduce drag',
                'Add a boat tail to reduce base drag',
                'Use smoother surface finish to reduce skin friction'
            ]
        }
    
    def print_analysis(self, analysis: FlightRegimeAnalysis):
        """Print detailed analysis report"""
        print("\n" + "="*80)
        print("FLIGHT REGIME ANALYSIS")
        print("="*80)
        
        print(f"\nACTUAL FLIGHT CONDITIONS:")
        print(f"  Max Apogee:           {analysis.max_apogee:.2f} m")
        print(f"  Max Velocity:         {analysis.max_velocity:.2f} m/s")
        print(f"  Max Mach Number:      {analysis.max_mach:.3f}")
        print(f"  Max Thrust:           {analysis.max_thrust:.2f} N")
        print(f"  Velocity at Apogee:   {analysis.velocity_at_apogee:.2f} m/s")
        
        print(f"\nIDEAL CONDITIONS (ZERO DRAG):")
        print(f"  Max Apogee:           {analysis.ideal_max_apogee:.2f} m")
        print(f"  Max Velocity:         {analysis.ideal_max_velocity:.2f} m/s")
        print(f"  Max Mach Number:      {analysis.ideal_max_mach:.3f}")
        
        print(f"\nFLIGHT REGIME:")
        if analysis.is_supersonic:
            print(f"    SUPERSONIC (Mach > {self.SUPERSONIC_THRESHOLD})")
        elif analysis.is_transonic:
            print(f"    TRANSONIC ({self.TRANSONIC_LOWER} < Mach < {self.TRANSONIC_UPPER})")
        else:
            print(f"    SUBSONIC (Mach < {self.TRANSONIC_LOWER})")
        
        if analysis.recommendations:
            self._print_recommendations(analysis.recommendations)
        
        print("="*80 + "\n")
    
    def _print_recommendations(self, rec: Dict[str, any]):
        """Print recommendations"""
        print(f"\n{'='*80}")
        print("  SUPERSONIC FLIGHT DETECTED - RECOMMENDATIONS")
        print("="*80)
        
        print(f"\nSTATUS: {rec['status']}")
        print(f"Max Mach Achieved: {rec['max_mach_achieved']:.3f}")
        print(f"Max Velocity: {rec['max_velocity_achieved']:.2f} m/s")
        
        print(f"\n{'='*80}")
        print("RECOMMENDED PROPULSION MODIFICATIONS:")
        print("="*80)
        
        for i, option_key in enumerate(['option_1', 'option_2', 'option_3'], 1):
            opt = rec[option_key]
            print(f"\nOPTION {i}: {opt['description']}")
            print(f"  Thrust:          {opt['recommended_thrust']:.2f} N")
            print(f"  Burn Time:       {opt['recommended_burn_time']:.2f} s")
            print(f"  Total Impulse:   {opt['total_impulse']:.2f} N·s")
            print(f"  Specific Impulse: {opt['recommended_specific_impulse']:.1f} s")
            print(f"  Reduction:       {opt['reduction_factor']*100:.1f}% of original")
        
        print(f"\n{'='*80}")
        print("WARNINGS:")
        print("="*80)
        for warning in rec['warnings']:
            print(f"    {warning}")
        
        print(f"\n{'='*80}")
        print("DESIGN SUGGESTIONS:")
        print("="*80)
        for suggestion in rec['design_suggestions']:
            print(f"   {suggestion}")
        
        print(f"\n{'='*80}")
        print("RECOMMENDATION: Do not proceed with optimization.")
        print("Modify propulsion system or aerodynamic design first.")
        print("="*80)
