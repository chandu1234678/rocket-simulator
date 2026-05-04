"""
Physics Utility Functions
Helper functions for common physics calculations
"""

import numpy as np
from src.models.constants import (
    G0_SEA_LEVEL,
    EARTH_RADIUS,
    RHO_SEA_LEVEL,
    T_SEA_LEVEL,
    SCALE_HEIGHT,
    LAPSE_RATE,
    GAMMA_AIR,
    R_SPECIFIC_AIR,
)


def gravity_at_altitude(altitude: float, use_altitude_correction: bool = False) -> float:
    """
    Calculate gravitational acceleration at altitude
    
    Args:
        altitude: Altitude above sea level (m)
        use_altitude_correction: If True, use altitude-dependent gravity
                                If False, use constant g0 (default for model rockets)
    
    Returns:
        Gravitational acceleration (m/s²)
    
    Note:
        For model rockets (<10km), the difference is <0.2%, so constant g0 is typically used.
        Enable altitude correction for high-altitude rockets or scientific accuracy.
    """
    if not use_altitude_correction or altitude < 0:
        return G0_SEA_LEVEL
    
    return G0_SEA_LEVEL * (EARTH_RADIUS / (EARTH_RADIUS + altitude)) ** 2


def atmospheric_density(altitude: float) -> float:
    """
    Calculate atmospheric density at altitude using exponential model
    
    Args:
        altitude: Altitude above sea level (m)
    
    Returns:
        Air density (kg/m³)
    
    Formula: ρ = ρ₀ × exp(-h / H)
    where H is the scale height (~8500m)
    """
    if altitude < 0:
        return RHO_SEA_LEVEL
    
    return RHO_SEA_LEVEL * np.exp(-altitude / SCALE_HEIGHT)


def atmospheric_temperature(altitude: float) -> float:
    """
    Calculate atmospheric temperature at altitude using ISA model
    
    Args:
        altitude: Altitude above sea level (m)
    
    Returns:
        Temperature (K)
    
    Formula: T = T₀ - L × h
    where L is the lapse rate (0.0065 K/m)
    
    Valid up to 11km (troposphere)
    """
    if altitude < 0:
        return T_SEA_LEVEL
    
    # Troposphere model (valid up to 11km)
    if altitude <= 11000:
        return T_SEA_LEVEL - LAPSE_RATE * altitude
    
    # Stratosphere (constant temperature above 11km)
    return T_SEA_LEVEL - LAPSE_RATE * 11000


def speed_of_sound(altitude: float) -> float:
    """
    Calculate speed of sound at altitude
    
    Args:
        altitude: Altitude above sea level (m)
    
    Returns:
        Speed of sound (m/s)
    
    Formula: c = sqrt(γ × R × T)
    """
    temperature = atmospheric_temperature(altitude)
    return np.sqrt(GAMMA_AIR * R_SPECIFIC_AIR * temperature)


def mach_number(velocity: float, altitude: float) -> float:
    """
    Calculate Mach number at given velocity and altitude
    
    Args:
        velocity: Velocity (m/s)
        altitude: Altitude (m)
    
    Returns:
        Mach number (dimensionless)
    """
    c = speed_of_sound(altitude)
    return abs(velocity) / c if c > 0 else 0.0


def dynamic_pressure(velocity: float, altitude: float) -> float:
    """
    Calculate dynamic pressure (q)
    
    Args:
        velocity: Velocity (m/s)
        altitude: Altitude (m)
    
    Returns:
        Dynamic pressure (Pa)
    
    Formula: q = 0.5 × ρ × v²
    """
    rho = atmospheric_density(altitude)
    return 0.5 * rho * velocity ** 2


# Example usage and tests
if __name__ == "__main__":
    print("="*60)
    print("PHYSICS UTILITIES DEMONSTRATION")
    print("="*60)
    
    altitudes = [0, 1000, 5000, 10000]
    
    print("\nAtmospheric Properties vs Altitude:")
    print(f"{'Alt (m)':<10} {'ρ (kg/m³)':<12} {'T (K)':<10} {'c (m/s)':<10} {'g (m/s²)':<10}")
    print("-" * 60)
    
    for h in altitudes:
        rho = atmospheric_density(h)
        temp = atmospheric_temperature(h)
        c = speed_of_sound(h)
        g_const = gravity_at_altitude(h, use_altitude_correction=False)
        g_var = gravity_at_altitude(h, use_altitude_correction=True)
        
        print(f"{h:<10} {rho:<12.4f} {temp:<10.2f} {c:<10.2f} {g_var:<10.5f}")
    
    print("\nGravity Variation:")
    print(f"{'Altitude':<15} {'g (const)':<15} {'g (variable)':<15} {'Difference':<15}")
    print("-" * 60)
    
    for h in [0, 5000, 10000, 50000, 100000]:
        g_const = gravity_at_altitude(h, use_altitude_correction=False)
        g_var = gravity_at_altitude(h, use_altitude_correction=True)
        diff_percent = ((g_const - g_var) / g_const) * 100
        
        print(f"{h:<15} {g_const:<15.5f} {g_var:<15.5f} {diff_percent:<15.3f}%")
    
    print("\nMach Number Examples:")
    print(f"{'Velocity (m/s)':<15} {'Altitude (m)':<15} {'Mach':<10}")
    print("-" * 40)
    
    test_cases = [
        (100, 0),
        (200, 0),
        (343, 0),  # Speed of sound at sea level
        (200, 5000),
        (300, 10000),
    ]
    
    for v, h in test_cases:
        mach = mach_number(v, h)
        print(f"{v:<15} {h:<15} {mach:<10.3f}")
    
    print("\n" + "="*60)
    print("Note: For model rockets (<10km), constant gravity is sufficient.")
    print("Gravity variation is <0.2% below 10km altitude.")
    print("="*60)
