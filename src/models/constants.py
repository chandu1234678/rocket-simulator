"""
Physical Constants for Rocket Simulation

All constants are documented with sources for verification.
"""

# Gravitational Constants
# Source: CODATA 2018 recommended values
G0_SEA_LEVEL = 9.80665  # Standard gravity at sea level (m/s²)
G0 = 9.81  # Simplified gravity for calculations (m/s²)
EARTH_RADIUS = 6371000  # Mean Earth radius (m)

def gravity_at_altitude(h: float) -> float:
    """
    Calculate gravity at altitude using inverse square law.
    
    g(h) = g₀ × (R / (R + h))²
    
    Args:
        h: Altitude above sea level (m)
    
    Returns:
        Gravitational acceleration (m/s²)
    
    Source: Newton's law of universal gravitation
    """
    return G0_SEA_LEVEL * (EARTH_RADIUS / (EARTH_RADIUS + h)) ** 2


# Atmospheric Constants (ISA - International Standard Atmosphere)
# Source: ICAO Document 7488/3, ISO 2533:1975

# Sea level conditions
RHO_SEA_LEVEL = 1.225  # Air density at sea level (kg/m³)
T_SEA_LEVEL = 288.15  # Temperature at sea level (K) = 15°C
P_SEA_LEVEL = 101325  # Pressure at sea level (Pa)

# Atmospheric properties
LAPSE_RATE = 0.0065  # Temperature lapse rate in troposphere (K/m)
SCALE_HEIGHT = 8500  # Atmospheric scale height (m) - simplified exponential model

# Aerodynamic Constants
# Supersonic Safety Limit for Model Rockets
# Justification: Model rockets should remain subsonic for safety and structural integrity
# - Mach 1.0 = speed of sound (transonic effects begin at ~0.8)
# - Mach 1.2 provides 20% safety margin above sonic speed
# - Prevents shock waves, structural damage, and unpredictable flight
SUPERSONIC_MACH_LIMIT = 1.2  # Maximum safe Mach number for model rockets
GAMMA_AIR = 1.4  # Ratio of specific heats for air (dimensionless)
R_SPECIFIC_AIR = 287.0  # Specific gas constant for dry air (J/(kg·K))

def air_density_isa(h: float) -> float:
    """
    Calculate air density using ISA standard atmosphere model.
    
    Troposphere (h < 11,000 m):
    ρ(h) = ρ₀ × (1 - L×h/T₀)^(g₀/(R×L) - 1)
    
    Simplified exponential (good approximation):
    ρ(h) = ρ₀ × exp(-h / H)
    
    Args:
        h: Altitude above sea level (m)
    
    Returns:
        Air density (kg/m³)
    
    Source: ICAO Standard Atmosphere
    """
    if h < 0:
        h = 0
    
    # Simplified exponential model (used in current code)
    return RHO_SEA_LEVEL * (1 - LAPSE_RATE * h / T_SEA_LEVEL) ** 4.256


def air_density_exponential(h: float) -> float:
    """
    Simplified exponential atmosphere model.
    
    ρ(h) = ρ₀ × exp(-h / H)
    
    Args:
        h: Altitude (m)
    
    Returns:
        Air density (kg/m³)
    
    Note: Less accurate than ISA but faster to compute
    """
    return RHO_SEA_LEVEL * (1 - LAPSE_RATE * h / T_SEA_LEVEL) ** 4.256


def temperature_isa(h: float) -> float:
    """
    Calculate temperature using ISA standard atmosphere.
    
    Troposphere (h < 11,000 m):
    T(h) = T₀ - L × h
    
    Args:
        h: Altitude (m)
    
    Returns:
        Temperature (K)
    
    Source: ICAO Standard Atmosphere
    """
    if h < 0:
        h = 0
    if h > 11000:
        return 216.65  # Stratosphere constant temperature
    return T_SEA_LEVEL - LAPSE_RATE * h


def speed_of_sound(h: float) -> float:
    """
    Calculate speed of sound at altitude.
    
    a = √(γ × R × T)
    
    Args:
        h: Altitude (m)
    
    Returns:
        Speed of sound (m/s)
    
    Source: Ideal gas law for sound propagation
    """
    T = temperature_isa(h)
    return (GAMMA_AIR * R_SPECIFIC_AIR * T) ** 0.5


# Aerodynamic Constants
MU_AIR = 1.81e-5  # Dynamic viscosity of air at sea level (Pa·s)
SUPERSONIC_MACH_LIMIT = 1.2  # Safety limit for supersonic flight

# Drag Coefficient Ranges (typical values)
CD_MIN_SUBSONIC = 0.15  # Minimum Cd for streamlined rocket (subsonic)
CD_MAX_SUBSONIC = 0.35  # Maximum Cd for subsonic flight
CD_MIN_TRANSONIC = 0.30  # Minimum Cd in transonic regime
CD_MAX_TRANSONIC = 0.85  # Maximum Cd at transonic (wave drag)
CD_MIN_SUPERSONIC = 0.20  # Minimum Cd for supersonic flight
CD_MAX_SUPERSONIC = 0.45  # Maximum Cd for supersonic flight

# Flight Regime Boundaries (Mach numbers)
MACH_SUBSONIC_MAX = 0.8  # Upper limit of subsonic regime
MACH_TRANSONIC_MIN = 0.8  # Lower limit of transonic regime
MACH_TRANSONIC_MAX = 1.2  # Upper limit of transonic regime
MACH_SUPERSONIC_MIN = 1.2  # Lower limit of supersonic regime


# Conversion Factors
M_TO_FT = 3.28084  # Meters to feet
KG_TO_LB = 2.20462  # Kilograms to pounds
N_TO_LBF = 0.224809  # Newtons to pounds-force
PA_TO_PSI = 0.000145038  # Pascals to PSI


# Documentation
CONSTANTS_SOURCES = {
    'gravity': 'CODATA 2018 recommended values',
    'atmosphere': 'ICAO Document 7488/3 - International Standard Atmosphere',
    'air_properties': 'ISO 2533:1975 - Standard Atmosphere',
    'aerodynamics': 'Typical values from rocket design literature',
}


def print_constants_summary():
    """Print a summary of all physical constants used."""
    print("=" * 80)
    print("PHYSICAL CONSTANTS REFERENCE")
    print("=" * 80)
    
    print("\n GRAVITATIONAL:")
    print(f"  g₀ (sea level):     {G0_SEA_LEVEL} m/s²")
    print(f"  g (simplified):     {G0} m/s²")
    print(f"  Earth radius:       {EARTH_RADIUS:,} m")
    
    print("\n️ ATMOSPHERIC (ISA):")
    print(f"  ρ₀ (sea level):     {RHO_SEA_LEVEL} kg/m³")
    print(f"  T₀ (sea level):     {T_SEA_LEVEL} K ({T_SEA_LEVEL - 273.15}°C)")
    print(f"  P₀ (sea level):     {P_SEA_LEVEL:,} Pa")
    print(f"  Lapse rate:         {LAPSE_RATE} K/m")
    print(f"  Scale height:       {SCALE_HEIGHT} m")
    print(f"  γ (air):            {GAMMA_AIR}")
    print(f"  R (specific):       {R_SPECIFIC_AIR} J/(kg·K)")
    
    print("\n AERODYNAMIC:")
    print(f"  μ (viscosity):      {MU_AIR} Pa·s")
    print(f"  Mach limit:         {SUPERSONIC_MACH_LIMIT}")
    
    print("\n FLIGHT REGIMES:")
    print(f"  Subsonic:           M < {MACH_SUBSONIC_MAX}")
    print(f"  Transonic:          {MACH_TRANSONIC_MIN} < M < {MACH_TRANSONIC_MAX}")
    print(f"  Supersonic:         M > {MACH_SUPERSONIC_MIN}")
    
    print("\n SOURCES:")
    for key, source in CONSTANTS_SOURCES.items():
        print(f"  {key:20s}: {source}")
    
    print("=" * 80)


if __name__ == "__main__":
    print_constants_summary()
    
    # Example calculations
    print("\n EXAMPLE CALCULATIONS:")
    print(f"\n  At h = 5000 m:")
    print(f"    g = {gravity_at_altitude(5000):.4f} m/s²")
    print(f"    ρ = {air_density_isa(5000):.4f} kg/m³")
    print(f"    T = {temperature_isa(5000):.2f} K ({temperature_isa(5000) - 273.15:.2f}°C)")
    print(f"    a = {speed_of_sound(5000):.2f} m/s")
    
    print(f"\n  At h = 10000 m:")
    print(f"    g = {gravity_at_altitude(10000):.4f} m/s²")
    print(f"    ρ = {air_density_isa(10000):.4f} kg/m³")
    print(f"    T = {temperature_isa(10000):.2f} K ({temperature_isa(10000) - 273.15:.2f}°C)")
    print(f"    a = {speed_of_sound(10000):.2f} m/s")
