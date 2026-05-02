"""
Main simulation engine for rocket trajectory.
Orchestrates all physics models and numerical integration.
PRODUCTION-GRADE: Fast, accurate, robust.
"""
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass, field

from .state import State, StateDerivatives
from .config import Config
from ..models.atmosphere import Atmosphere
from ..models.propulsion import Propulsion
from ..models.aerodynamics import Aerodynamics
from ..models.dynamics import Dynamics
from ..solvers.rk4 import RK4Solver


@dataclass
class TrajectoryPoint:
    """Single point in trajectory."""
    t: float  # Time (s)
    h: float  # Altitude (m)
    v: float  # Velocity (m/s)
    a: float  # Acceleration (m/s²)
    m: float  # Mass (kg)
    T: float  # Thrust (N)
    D: float  # Drag (N)
    M: float  # Mach number
    Cd: float  # Drag coefficient
    rho: float  # Air density (kg/m³)


@dataclass
class Trajectory:
    """Complete trajectory data."""
    points: List[TrajectoryPoint] = field(default_factory=list)
    
    @property
    def max_altitude(self) -> float:
        """Maximum altitude reached (apogee)."""
        return max(p.h for p in self.points) if self.points else 0.0
    
    @property
    def max_velocity(self) -> float:
        """Maximum velocity reached."""
        return max(p.v for p in self.points) if self.points else 0.0
    
    @property
    def max_mach(self) -> float:
        """Maximum Mach number reached."""
        return max(p.M for p in self.points) if self.points else 0.0
    
    @property
    def burnout_time(self) -> float:
        """Time when thrust ends."""
        for p in self.points:
            if p.T == 0 and p.t > 0:
                return p.t
        return 0.0
    
    @property
    def apogee_time(self) -> float:
        """Time when apogee is reached."""
        max_h = self.max_altitude
        for p in self.points:
            if abs(p.h - max_h) < 0.01:
                return p.t
        return 0.0
    
    def to_arrays(self) -> dict:
        """Convert to arrays for plotting."""
        return {
            't': np.array([p.t for p in self.points]),
            'h': np.array([p.h for p in self.points]),
            'v': np.array([p.v for p in self.points]),
            'a': np.array([p.a for p in self.points]),
            'm': np.array([p.m for p in self.points]),
            'T': np.array([p.T for p in self.points]),
            'D': np.array([p.D for p in self.points]),
            'M': np.array([p.M for p in self.points]),
            'Cd': np.array([p.Cd for p in self.points]),
            'rho': np.array([p.rho for p in self.points]),
        }


class SimulationEngine:
    """
    Main rocket simulation engine.
    
    Integrates all physics models with RK4 solver.
    Optimized for speed and accuracy.
    """
    
    def __init__(self, config: Config):
        """
        Initialize simulation engine.
        
        Args:
            config: Complete simulation configuration
        """
        self.config = config
        
        # Initialize physics models
        self.atmosphere = Atmosphere(
            h0=config.launch.altitude,
            T0=config.launch.temperature,
            P0=config.launch.pressure,
            rho0=1.225  # Will be computed from P0, T0
        )
        
        self.propulsion = Propulsion(
            T_max=config.propulsion.thrust_max,
            t_burn=config.propulsion.burn_time,
            Isp=config.propulsion.specific_impulse
        )
        
        self.aerodynamics = Aerodynamics(
            A_ref=config.rocket.reference_area,
            Cd_base=config.aerodynamics.cd_base,
            use_advanced=config.aerodynamics.mach_model == "advanced",
            k_spike=config.aerodynamics.transonic_spike_magnitude,
            M_center=config.aerodynamics.transonic_spike_center,
            sigma=config.aerodynamics.transonic_spike_width
        )
        
        self.dynamics = Dynamics(g=9.80665)
        
        # Initialize solver
        self.solver = RK4Solver(dt=config.simulation.timestep)
        
        # Trajectory storage
        self.trajectory = Trajectory()
    
    def derivatives_function(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Compute derivatives for RK4 solver.
        
        This is the core physics function called by the integrator.
        
        Args:
            t: Current time (s)
            y: State vector [h, v, m]
            
        Returns:
            Derivative vector [dh/dt, dv/dt, dm/dt]
        """
        h, v, m = y
        
        # Atmosphere properties
        rho, T_atm, P, a = self.atmosphere.get_all_properties(h)
        
        # Propulsion
        T, mdot, is_burning = self.propulsion.compute_all(t)
        
        # Aerodynamics
        M, Cd, D = self.aerodynamics.compute_all(v, rho, a)
        
        # Dynamics
        dh_dt, dv_dt, dm_dt = self.dynamics.compute_derivatives(v, T, D, m, mdot)
        
        return np.array([dh_dt, dv_dt, dm_dt])
    
    def check_termination(self, state: State) -> bool:
        """
        Check if simulation should terminate.
        
        Termination conditions:
        1. Apogee reached (v = 0 and not burning)
        2. Ground impact (h < 0)
        3. Invalid state (NaN, negative mass, etc.)
        
        Args:
            state: Current state
            
        Returns:
            True if should continue, False if should terminate
        """
        # Check validity
        if not state.is_valid():
            return False
        
        # Ground impact
        if state.h < 0:
            return False
        
        # Apogee reached (velocity near zero and not burning)
        if state.v <= 0 and not self.propulsion.is_burning(state.t):
            return False
        
        return True
    
    def run(self) -> Trajectory:
        """
        Run complete simulation.
        
        Returns:
            Trajectory object with all flight data
        """
        # Initial state
        state = State(
            t=0.0,
            h=0.0,
            v=0.0,
            m=self.config.rocket.mass_initial,
            a=0.0
        )
        
        # Clear trajectory
        self.trajectory = Trajectory()
        
        # Simulation loop
        t = 0.0
        dt = self.config.simulation.timestep
        max_time = self.config.simulation.max_time
        
        while t < max_time:
            # Get current state vector
            y = state.to_array()
            
            # Compute current forces for logging
            rho, T_atm, P, a = self.atmosphere.get_all_properties(state.h)
            T, mdot, is_burning = self.propulsion.compute_all(t)
            M, Cd, D = self.aerodynamics.compute_all(state.v, rho, a)
            acc = self.dynamics.compute_acceleration(T, D, state.m)
            
            # Log trajectory point
            point = TrajectoryPoint(
                t=t,
                h=state.h,
                v=state.v,
                a=acc,
                m=state.m,
                T=T,
                D=D,
                M=M,
                Cd=Cd,
                rho=rho
            )
            self.trajectory.points.append(point)
            
            # Check termination
            if not self.check_termination(state):
                break
            
            # RK4 integration step
            y_next = self.solver.step(y, t, self.derivatives_function)
            
            # Update state
            t += dt
            state = State.from_array(t, y_next, a=acc)
            
            # Safety check
            if not state.is_valid():
                print(f"WARNING: Invalid state at t={t:.3f}s")
                break
        
        return self.trajectory
    
    def get_summary(self) -> dict:
        """
        Get simulation summary statistics.
        
        Returns:
            Dictionary with key results
        """
        return {
            'apogee': self.trajectory.max_altitude,
            'max_velocity': self.trajectory.max_velocity,
            'max_mach': self.trajectory.max_mach,
            'burnout_time': self.trajectory.burnout_time,
            'apogee_time': self.trajectory.apogee_time,
            'flight_time': self.trajectory.points[-1].t if self.trajectory.points else 0.0,
            'num_points': len(self.trajectory.points)
        }
