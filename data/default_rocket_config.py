"""
Default Rocket Configurations
Centralized configuration to avoid duplication across run scripts
"""

# Default rocket configuration for examples
# This represents a typical model rocket with solid propellant
DEFAULT_ROCKET_CONFIG = {
    'thrust': 80.0,              # Thrust force in Newtons (N)
    'burn_time': 1.8,            # Engine burn duration in seconds (s) - will be recalculated
    'specific_impulse': 180,     # Specific impulse in seconds (s)
    'mass_initial': 2.2,         # Initial total mass in kilograms (kg)
    'mass_dry': 2.0,             # Dry mass (without propellant) in kg
}

# Rocket geometry ratios (used to estimate dimensions from optimized diameter)
NOSE_TO_DIAMETER_RATIO = 3.0     # Nose cone length = 3 × Diameter
BODY_TO_DIAMETER_RATIO = 10.0    # Body tube length = 10 × Diameter

# Default optimization parameters
DEFAULT_TARGET_APOGEE = 500.0    # Target altitude in meters (m)
DEFAULT_TOLERANCE = 50.0         # Acceptable error in meters (m)
DEFAULT_MAX_ITERATIONS = 100     # Maximum optimization iterations

# Alternative configurations for different scenarios

# High-altitude configuration (more propellant)
HIGH_ALTITUDE_CONFIG = {
    'thrust': 120.0,
    'burn_time': 2.5,
    'specific_impulse': 200,
    'mass_initial': 3.5,
    'mass_dry': 2.5,
}

# Low-altitude configuration (less propellant, safer)
LOW_ALTITUDE_CONFIG = {
    'thrust': 50.0,
    'burn_time': 1.5,
    'specific_impulse': 160,
    'mass_initial': 1.8,
    'mass_dry': 1.5,
}

# Competition configuration (optimized for accuracy)
COMPETITION_CONFIG = {
    'thrust': 80.0,
    'burn_time': 1.8,
    'specific_impulse': 180,
    'mass_initial': 2.2,
    'mass_dry': 2.0,
}


def get_config(config_name: str = 'default') -> dict:
    """
    Get a rocket configuration by name
    
    Args:
        config_name: One of 'default', 'high_altitude', 'low_altitude', 'competition'
    
    Returns:
        Rocket configuration dictionary
    """
    configs = {
        'default': DEFAULT_ROCKET_CONFIG,
        'high_altitude': HIGH_ALTITUDE_CONFIG,
        'low_altitude': LOW_ALTITUDE_CONFIG,
        'competition': COMPETITION_CONFIG,
    }
    
    if config_name not in configs:
        raise ValueError(f"Unknown config: {config_name}. Available: {list(configs.keys())}")
    
    return configs[config_name].copy()


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("AVAILABLE ROCKET CONFIGURATIONS")
    print("="*60)
    
    for name in ['default', 'high_altitude', 'low_altitude', 'competition']:
        config = get_config(name)
        print(f"\n{name.upper().replace('_', ' ')}:")
        print(f"  Thrust: {config['thrust']}N")
        print(f"  Burn Time: {config['burn_time']}s")
        print(f"  ISP: {config['specific_impulse']}s")
        print(f"  Mass: {config['mass_initial']}kg")
        print(f"  Propellant: {config['mass_initial'] - config['mass_dry']}kg")
    
    print("\n" + "="*60)
    print("Usage in scripts:")
    print("  from data.default_rocket_config import get_config")
    print("  config = get_config('default')")
    print("="*60)
