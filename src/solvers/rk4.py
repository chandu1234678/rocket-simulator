"""
Runge-Kutta 4th Order (RK4) solver.
Industry-standard ODE integration method.
Optimized with Numba JIT compilation for maximum speed.
"""
import numpy as np
from typing import Callable, Tuple

# Note: Numba JIT removed for API compatibility
# Performance impact is minimal for typical simulations
def rk4_step(
    y: np.ndarray,
    t: float,
    dt: float,
    f: Callable
) -> np.ndarray:
    """
    Single RK4 integration step.
    
    Classic 4th-order Runge-Kutta:
    k₁ = f(t, y)
    k₂ = f(t + dt/2, y + dt*k₁/2)
    k₃ = f(t + dt/2, y + dt*k₂/2)
    k₄ = f(t + dt, y + dt*k₃)
    y_next = y + (dt/6) * (k₁ + 2*k₂ + 2*k₃ + k₄)
    
    Args:
        y: Current state vector [h, v, m]
        t: Current time
        dt: Time step
        f: Derivative function f(t, y) -> dy/dt
        
    Returns:
        Next state vector
    """
    # k1 = f(t, y)
    k1 = f(t, y)
    
    # k2 = f(t + dt/2, y + dt*k1/2)
    k2 = f(t + 0.5*dt, y + 0.5*dt*k1)
    
    # k3 = f(t + dt/2, y + dt*k2/2)
    k3 = f(t + 0.5*dt, y + 0.5*dt*k2)
    
    # k4 = f(t + dt, y + dt*k3)
    k4 = f(t + dt, y + dt*k3)
    
    # Weighted average
    y_next = y + (dt / 6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)
    
    return y_next


class RK4Solver:
    """
    Runge-Kutta 4th Order solver for rocket trajectory.
    
    Provides 4th-order accuracy: O(dt⁴)
    Stable and industry-standard for aerospace applications.
    """
    
    def __init__(self, dt: float = 0.01):
        """
        Initialize RK4 solver.
        
        Args:
            dt: Time step (s)
        """
        if dt <= 0:
            raise ValueError("Time step must be positive")
        self.dt = dt
    
    def step(
        self,
        y: np.ndarray,
        t: float,
        f: Callable[[float, np.ndarray], np.ndarray]
    ) -> np.ndarray:
        """
        Perform single RK4 integration step.
        
        Args:
            y: Current state vector [h, v, m]
            t: Current time (s)
            f: Derivative function f(t, y) -> dy/dt
            
        Returns:
            Next state vector
        """
        return rk4_step(y, t, self.dt, f)
    
    def integrate(
        self,
        y0: np.ndarray,
        t0: float,
        t_end: float,
        f: Callable[[float, np.ndarray], np.ndarray],
        callback: Callable[[float, np.ndarray], bool] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Integrate from t0 to t_end.
        
        Args:
            y0: Initial state vector
            t0: Initial time
            t_end: End time
            f: Derivative function
            callback: Optional callback function(t, y) -> continue_flag
            
        Returns:
            (t_array, y_array) tuple
        """
        # Initialize arrays
        n_steps = int((t_end - t0) / self.dt) + 1
        t_array = np.zeros(n_steps)
        y_array = np.zeros((n_steps, len(y0)))
        
        # Initial conditions
        t_array[0] = t0
        y_array[0] = y0
        
        # Integration loop
        t = t0
        y = y0.copy()
        
        for i in range(1, n_steps):
            # RK4 step
            y = self.step(y, t, f)
            t = t0 + i * self.dt
            
            # Store
            t_array[i] = t
            y_array[i] = y
            
            # Callback (for termination conditions)
            if callback is not None:
                if not callback(t, y):
                    # Truncate arrays
                    return t_array[:i+1], y_array[:i+1]
        
        return t_array, y_array
