"""
Utility functions for logging, plotting, data export, and physics calculations.
"""

__all__ = []

# Optional physics utilities - only available if dependencies are installed
try:
    from src.utils.physics_utils import (
        gravity_at_altitude,
        atmospheric_density,
        atmospheric_temperature,
        speed_of_sound,
        mach_number,
        dynamic_pressure,
    )
    
    __all__.extend([
        'gravity_at_altitude',
        'atmospheric_density',
        'atmospheric_temperature',
        'speed_of_sound',
        'mach_number',
        'dynamic_pressure',
    ])
except ImportError:
    # Physics utilities not available - dependencies may not be installed
    pass

