"""
Atmospheric model for rocket simulation.
Implements exponential density model and ISA standard atmosphere.
Optimized with Numba JIT compilation (optional).
"""
import numpy as np
from src.utils.numba_utils import jit
from typing import Tuple


# Physical constants
R_AIR = 287.05  # J/(kg·K) - Specific gas constant for air
GAMMA = 1.4  # Ratio of specific heats for air
G0 = 9.80665  # m/s² - Standard gravity


@jit(nopython=True, cache=True)
def exponential_density(h: float, rho0: float = 1.225, H: float = 8500.0) -> float:
    """
    Exponential atmosphere model (fast approximation).
    
    ρ(h) = ρ₀ * exp(-h / H)
    
    Args:
        h: Altitude (m)
        rho0: Sea level density (kg/m³)
        H: Scale height (m)
        
    Returns:
        Air density (kg/m³)
    """
    return rho0 * np.exp(-h / H)


@jit(nopython=True, cache=True)
def temperature_lapse(h: float, T0: float = 288.15, L: float = 0.0065) -> float:
    """
    Temperature with linear lapse rate (up to 11 km).
    
    T(h) = T₀ - L * h
    
    Args:
        h: Altitude (m)
        T0: Sea level temperature (K)
        L: Lapse rate (K/m)
        
    Returns:
        Temperature (K)
    """
    if h < 11000:
        return T0 - L * h
    else:
        return 216.65  # Stratosphere constant temperature


@jit(nopython=True, cache=True)
def speed_of_sound(T: float) -> float:
    """
    Speed of sound in air.
    
    a = √(γ * R * T)
    
    Args:
        T: Temperature (K)
        
    Returns:
        Speed of sound (m/s)
    """
    return np.sqrt(GAMMA * R_AIR * T)


@jit(nopython=True, cache=True)
def pressure_from_density(rho: float, T: float) -> float:
    """
    Pressure from ideal gas law.
    
    P = ρ * R * T
    
    Args:
        rho: Density (kg/m³)
        T: Temperature (K)
        
    Returns:
        Pressure (Pa)
    """
    return rho * R_AIR * T


@jit(nopython=True, cache=True)
def get_atmosphere_properties(
    h: float,
    h0: float = 0.0,
    T0: float = 288.15,
    P0: float = 101325.0,
    rho0: float = 1.225
) -> Tuple[float, float, float, float]:
    """
    Get all atmosphere properties at given altitude.
    Optimized for speed with Numba.
    
    Args:
        h: Altitude above ground (m)
        h0: Ground altitude ASL (m)
        T0: Ground temperature (K)
        P0: Ground pressure (Pa)
        rho0: Ground density (kg/m³)
        
    Returns:
        (density, temperature, pressure, speed_of_sound) tuple
    """
    h_asl = h + h0  # Altitude above sea level
    
    # Temperature
    T = temperature_lapse(h_asl, T0)
    
    # Density (exponential model)
    rho = exponential_density(h_asl, rho0)
    
    # Pressure
    P = pressure_from_density(rho, T)
    
    # Speed of sound
    a = speed_of_sound(T)
    
    return rho, T, P, a


class Atmosphere:
    """
    Atmosphere model for rocket simulation.
    Provides air properties as function of altitude.
    """
    
    def __init__(
        self,
        h0: float = 0.0,
        T0: float = 288.15,
        P0: float = 101325.0,
        rho0: float = 1.225
    ):
        """
        Initialize atmosphere model.
        
        Args:
            h0: Ground altitude ASL (m)
            T0: Ground temperature (K)
            P0: Ground pressure (Pa)
            rho0: Ground density (kg/m³)
        """
        self.h0 = h0
        self.T0 = T0
        self.P0 = P0
        self.rho0 = rho0
    
    def get_density(self, h: float) -> float:
        """Get air density at altitude."""
        rho, _, _, _ = get_atmosphere_properties(h, self.h0, self.T0, self.P0, self.rho0)
        return rho
    
    def get_temperature(self, h: float) -> float:
        """Get temperature at altitude."""
        _, T, _, _ = get_atmosphere_properties(h, self.h0, self.T0, self.P0, self.rho0)
        return T
    
    def get_pressure(self, h: float) -> float:
        """Get pressure at altitude."""
        _, _, P, _ = get_atmosphere_properties(h, self.h0, self.T0, self.P0, self.rho0)
        return P
    
    def get_speed_of_sound(self, h: float) -> float:
        """Get speed of sound at altitude."""
        _, _, _, a = get_atmosphere_properties(h, self.h0, self.T0, self.P0, self.rho0)
        return a
    
    def get_all_properties(self, h: float) -> Tuple[float, float, float, float]:
        """
        Get all atmosphere properties at once (most efficient).
        
        Returns:
            (density, temperature, pressure, speed_of_sound)
        """
        return get_atmosphere_properties(h, self.h0, self.T0, self.P0, self.rho0)
