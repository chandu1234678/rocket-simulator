"""
Propulsion model for rocket simulation.
Handles thrust and mass flow calculations.
Optimized with Numba JIT compilation.
"""
import numpy as np
from numba import jit
from typing import Tuple


# Physical constants
G0 = 9.80665  # m/s² - Standard gravity


@jit(nopython=True, cache=True)
def compute_thrust_constant(
    t: float,
    T_max: float,
    t_burn: float
) -> float:
    """
    Constant thrust model.
    
    T(t) = T_max  if t < t_burn
           0      if t ≥ t_burn
    
    Args:
        t: Current time (s)
        T_max: Maximum thrust (N)
        t_burn: Burn time (s)
        
    Returns:
        Thrust (N)
    """
    if t < t_burn:
        return T_max
    else:
        return 0.0


@jit(nopython=True, cache=True)
def compute_mass_flow(
    T: float,
    Isp: float,
    g0: float = G0
) -> float:
    """
    Compute mass flow rate from thrust.
    
    ṁ = T / (Isp * g₀)
    
    Args:
        T: Thrust (N)
        Isp: Specific impulse (s)
        g0: Standard gravity (m/s²)
        
    Returns:
        Mass flow rate (kg/s)
    """
    if T <= 0:
        return 0.0
    return T / (Isp * g0)


@jit(nopython=True, cache=True)
def compute_propulsion(
    t: float,
    T_max: float,
    t_burn: float,
    Isp: float,
    g0: float = G0
) -> Tuple[float, float, bool]:
    """
    Compute all propulsion quantities at once (optimized).
    
    Args:
        t: Current time (s)
        T_max: Maximum thrust (N)
        t_burn: Burn time (s)
        Isp: Specific impulse (s)
        g0: Standard gravity (m/s²)
        
    Returns:
        (thrust, mass_flow, is_burning) tuple
    """
    is_burning = t < t_burn
    
    if is_burning:
        T = T_max
        mdot = compute_mass_flow(T, Isp, g0)
    else:
        T = 0.0
        mdot = 0.0
    
    return T, mdot, is_burning


class Propulsion:
    """
    Propulsion model for rocket simulation.
    Provides thrust and mass flow as function of time.
    """
    
    def __init__(
        self,
        T_max: float,
        t_burn: float,
        Isp: float,
        thrust_curve_type: str = "constant"
    ):
        """
        Initialize propulsion model.
        
        Args:
            T_max: Maximum thrust (N)
            t_burn: Burn time (s)
            Isp: Specific impulse (s)
            thrust_curve_type: Type of thrust curve ("constant" only for now)
        """
        self.T_max = T_max
        self.t_burn = t_burn
        self.Isp = Isp
        self.thrust_curve_type = thrust_curve_type
        
        # Validate
        if T_max <= 0:
            raise ValueError("Thrust must be positive")
        if t_burn <= 0:
            raise ValueError("Burn time must be positive")
        if Isp <= 0:
            raise ValueError("Specific impulse must be positive")
    
    def get_thrust(self, t: float) -> float:
        """Get thrust at given time."""
        return compute_thrust_constant(t, self.T_max, self.t_burn)
    
    def get_mass_flow(self, t: float) -> float:
        """Get mass flow rate at given time."""
        T = self.get_thrust(t)
        return compute_mass_flow(T, self.Isp)
    
    def is_burning(self, t: float) -> bool:
        """Check if motor is still burning."""
        return t < self.t_burn
    
    def compute_all(self, t: float) -> Tuple[float, float, bool]:
        """
        Compute all propulsion quantities (most efficient).
        
        Returns:
            (thrust, mass_flow, is_burning)
        """
        return compute_propulsion(t, self.T_max, self.t_burn, self.Isp)
