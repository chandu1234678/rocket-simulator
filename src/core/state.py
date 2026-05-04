"""
State management for rocket simulation.
High-performance implementation with validation.
"""
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class State:
    """
    Rocket state at a given time.
    
    Attributes:
        t: Time (s)
        h: Altitude above ground (m)
        v: Vertical velocity (m/s)
        m: Total mass (kg)
        a: Acceleration (m/s²) - computed, not integrated
    """
    t: float
    h: float
    v: float
    m: float
    a: float = 0.0
    
    def __post_init__(self):
        """Validate state after initialization."""
        if self.m <= 0:
            raise ValueError(f"Mass must be positive, got {self.m}")
        # Note: Altitude can be negative during landing - validation moved to simulation loop
        if not np.isfinite([self.t, self.h, self.v, self.m, self.a]).all():
            raise ValueError("State contains non-finite values (NaN or Inf)")
    
    def copy(self) -> 'State':
        """Create a deep copy of the state."""
        return State(
            t=self.t,
            h=self.h,
            v=self.v,
            m=self.m,
            a=self.a
        )
    
    def is_valid(self) -> bool:
        """Check if state is physically valid."""
        return (
            self.m > 0 and
            self.h >= 0 and
            np.isfinite([self.t, self.h, self.v, self.m, self.a]).all()
        )
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for numerical operations."""
        return np.array([self.h, self.v, self.m])
    
    @classmethod
    def from_array(cls, t: float, arr: np.ndarray, a: float = 0.0) -> 'State':
        """Create state from numpy array."""
        return cls(t=t, h=arr[0], v=arr[1], m=arr[2], a=a)


@dataclass
class StateDerivatives:
    """
    Time derivatives of state variables.
    
    dh/dt = v
    dv/dt = a
    dm/dt = -mdot
    """
    dh_dt: float  # Velocity (m/s)
    dv_dt: float  # Acceleration (m/s²)
    dm_dt: float  # Mass flow rate (kg/s)
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.dh_dt, self.dv_dt, self.dm_dt])
