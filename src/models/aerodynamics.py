"""
Aerodynamics model with Mach-dependent drag coefficient.
CRITICAL: Implements transonic drag spike for accuracy.
Optimized with Numba JIT compilation.
"""
import numpy as np
from numba import jit
from typing import Tuple


@jit(nopython=True, cache=True)
def compute_mach_number(v: float, a: float) -> float:
    """
    Compute Mach number.
    
    M = v / a
    
    Args:
        v: Velocity (m/s)
        a: Speed of sound (m/s)
        
    Returns:
        Mach number (dimensionless)
    """
    if a <= 0:
        return 0.0
    return abs(v) / a


@jit(nopython=True, cache=True)
def drag_coefficient_simple(M: float, Cd_base: float = 0.366) -> float:
    """
    Simple constant drag coefficient model.
    
    Args:
        M: Mach number
        Cd_base: Base drag coefficient
        
    Returns:
        Drag coefficient
    """
    return Cd_base


@jit(nopython=True, cache=True)
def drag_coefficient_advanced(
    M: float,
    Cd_base: float = 0.366,
    k_spike: float = 0.5,
    M_center: float = 1.0,
    sigma: float = 0.15
) -> float:
    """
    Advanced Mach-dependent drag coefficient with transonic spike.
    
    CRITICAL FOR ACCURACY!
    
    Cd(M) = {
        Cd_base                                    if M < 0.3  (incompressible)
        Cd_base + 0.1 * M²                         if 0.3 ≤ M < 0.8  (subsonic)
        Cd_base + k * exp(-((M-1)²/σ²))            if 0.8 ≤ M < 1.2  (transonic)
        Cd_base + 0.2 / M                          if M ≥ 1.2  (supersonic)
    }
    
    Args:
        M: Mach number
        Cd_base: Base drag coefficient
        k_spike: Transonic spike magnitude
        M_center: Transonic spike center (usually 1.0)
        sigma: Transonic spike width
        
    Returns:
        Drag coefficient
    """
    if M < 0.3:
        # Incompressible flow
        return Cd_base
    
    elif M < 0.8:
        # Subsonic compressible
        return Cd_base + 0.1 * M * M
    
    elif M < 1.2:
        # Transonic - CRITICAL REGION
        # Gaussian spike centered at M = 1.0
        spike = k_spike * np.exp(-((M - M_center) ** 2) / (sigma ** 2))
        return Cd_base + spike
    
    else:
        # Supersonic
        return Cd_base + 0.2 / M


@jit(nopython=True, cache=True)
def compute_drag_force(
    v: float,
    rho: float,
    Cd: float,
    A_ref: float
) -> float:
    """
    Compute drag force.
    
    D = ½ * ρ * v² * Cd * A
    
    Args:
        v: Velocity (m/s)
        rho: Air density (kg/m³)
        Cd: Drag coefficient
        A_ref: Reference area (m²)
        
    Returns:
        Drag force (N), always positive
    """
    if v == 0:
        return 0.0
    return 0.5 * rho * v * v * Cd * A_ref


@jit(nopython=True, cache=True)
def compute_aerodynamics(
    v: float,
    rho: float,
    a: float,
    A_ref: float,
    Cd_base: float,
    use_advanced: bool = True,
    k_spike: float = 0.5,
    M_center: float = 1.0,
    sigma: float = 0.15
) -> Tuple[float, float, float]:
    """
    Compute all aerodynamic quantities at once (optimized).
    
    Args:
        v: Velocity (m/s)
        rho: Air density (kg/m³)
        a: Speed of sound (m/s)
        A_ref: Reference area (m²)
        Cd_base: Base drag coefficient
        use_advanced: Use Mach-dependent Cd model
        k_spike: Transonic spike magnitude
        M_center: Transonic spike center
        sigma: Transonic spike width
        
    Returns:
        (Mach, Cd, Drag) tuple
    """
    # Mach number
    M = compute_mach_number(v, a)
    
    # Drag coefficient
    if use_advanced:
        Cd = drag_coefficient_advanced(M, Cd_base, k_spike, M_center, sigma)
    else:
        Cd = drag_coefficient_simple(M, Cd_base)
    
    # Drag force
    D = compute_drag_force(v, rho, Cd, A_ref)
    
    return M, Cd, D


class Aerodynamics:
    """
    Aerodynamics model for rocket simulation.
    Provides drag force as function of velocity and atmospheric conditions.
    """
    
    def __init__(
        self,
        A_ref: float,
        Cd_base: float = 0.366,
        use_advanced: bool = True,
        k_spike: float = 0.5,
        M_center: float = 1.0,
        sigma: float = 0.15
    ):
        """
        Initialize aerodynamics model.
        
        Args:
            A_ref: Reference area (m²)
            Cd_base: Base drag coefficient
            use_advanced: Use Mach-dependent Cd model
            k_spike: Transonic spike magnitude
            M_center: Transonic spike center
            sigma: Transonic spike width
        """
        self.A_ref = A_ref
        self.Cd_base = Cd_base
        self.use_advanced = use_advanced
        self.k_spike = k_spike
        self.M_center = M_center
        self.sigma = sigma
    
    def get_drag_coefficient(self, M: float) -> float:
        """Get drag coefficient for given Mach number."""
        if self.use_advanced:
            return drag_coefficient_advanced(
                M, self.Cd_base, self.k_spike, self.M_center, self.sigma
            )
        else:
            return drag_coefficient_simple(M, self.Cd_base)
    
    def get_drag_force(self, v: float, rho: float, M: float) -> float:
        """Get drag force."""
        Cd = self.get_drag_coefficient(M)
        return compute_drag_force(v, rho, Cd, self.A_ref)
    
    def compute_all(
        self,
        v: float,
        rho: float,
        a: float
    ) -> Tuple[float, float, float]:
        """
        Compute all aerodynamic quantities (most efficient).
        
        Returns:
            (Mach, Cd, Drag)
        """
        return compute_aerodynamics(
            v, rho, a, self.A_ref, self.Cd_base,
            self.use_advanced, self.k_spike, self.M_center, self.sigma
        )
