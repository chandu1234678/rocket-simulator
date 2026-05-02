"""
Dynamics model - equations of motion for rocket.
Implements Newton's second law with variable mass.
Optimized with Numba JIT compilation.
"""
import numpy as np
from numba import jit
from typing import Tuple


# Physical constants
G0 = 9.80665  # m/s² - Standard gravity


@jit(nopython=True, cache=True)
def compute_acceleration(
    T: float,
    D: float,
    m: float,
    g: float = G0
) -> float:
    """
    Compute vertical acceleration from forces.
    
    a = (T - D - m*g) / m
    
    Args:
        T: Thrust (N)
        D: Drag (N)
        m: Mass (kg)
        g: Gravitational acceleration (m/s²)
        
    Returns:
        Acceleration (m/s²)
    """
    if m <= 0:
        raise ValueError("Mass must be positive")
    
    return (T - D - m * g) / m


@jit(nopython=True, cache=True)
def compute_derivatives(
    v: float,
    T: float,
    D: float,
    m: float,
    mdot: float,
    g: float = G0
) -> Tuple[float, float, float]:
    """
    Compute time derivatives of state variables.
    
    dh/dt = v
    dv/dt = (T - D - m*g) / m
    dm/dt = -ṁ
    
    Args:
        v: Velocity (m/s)
        T: Thrust (N)
        D: Drag (N)
        m: Mass (kg)
        mdot: Mass flow rate (kg/s)
        g: Gravitational acceleration (m/s²)
        
    Returns:
        (dh_dt, dv_dt, dm_dt) tuple
    """
    # Altitude rate of change
    dh_dt = v
    
    # Velocity rate of change (acceleration)
    dv_dt = compute_acceleration(T, D, m, g)
    
    # Mass rate of change
    dm_dt = -mdot
    
    return dh_dt, dv_dt, dm_dt


class Dynamics:
    """
    Dynamics model for rocket simulation.
    Computes equations of motion.
    """
    
    def __init__(self, g: float = G0):
        """
        Initialize dynamics model.
        
        Args:
            g: Gravitational acceleration (m/s²)
        """
        self.g = g
    
    def compute_acceleration(self, T: float, D: float, m: float) -> float:
        """Compute acceleration from forces."""
        return compute_acceleration(T, D, m, self.g)
    
    def compute_derivatives(
        self,
        v: float,
        T: float,
        D: float,
        m: float,
        mdot: float
    ) -> Tuple[float, float, float]:
        """
        Compute all derivatives.
        
        Returns:
            (dh_dt, dv_dt, dm_dt)
        """
        return compute_derivatives(v, T, D, m, mdot, self.g)
