"""
Optimization Result Data Classes
Type-safe result structures for optimization outputs
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OptimizationResult:
    """
    Type-safe optimization result
    
    Replaces plain dict with structured data for better type safety
    and IDE support.
    """
    # Optimized parameters
    diameter: float  # Rocket diameter (m)
    nose_length: float  # Nose cone length (m)
    body_length: float  # Body tube length (m)
    cd: float  # Drag coefficient (dimensionless)
    
    # Performance metrics
    apogee: float  # Achieved apogee (m)
    max_mach: float  # Maximum Mach number
    error: float  # Error from target (m)
    
    # Optimization metadata
    converged: bool  # Whether optimization converged
    iterations: int  # Number of iterations
    time: float  # Computation time (s)
    
    # Optional fields
    phase1_time: Optional[float] = None  # Phase 1 time for hybrid (s)
    phase2_time: Optional[float] = None  # Phase 2 time for hybrid (s)
    optimization_steps: Optional[int] = None  # Actual optimization steps
    supersonic_violation: Optional[bool] = None  # Supersonic flag
    
    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility"""
        result = {
            'diameter': self.diameter,
            'nose_length': self.nose_length,
            'body_length': self.body_length,
            'cd': self.cd,
            'apogee': self.apogee,
            'max_mach': self.max_mach,
            'error': self.error,
            'converged': self.converged,
            'iterations': self.iterations,
            'time': self.time,
        }
        
        # Add optional fields if present
        if self.phase1_time is not None:
            result['phase1_time'] = self.phase1_time
        if self.phase2_time is not None:
            result['phase2_time'] = self.phase2_time
        if self.optimization_steps is not None:
            result['optimization_steps'] = self.optimization_steps
        if self.supersonic_violation is not None:
            result['supersonic_violation'] = self.supersonic_violation
            
        return result
    
    @property
    def error_percent(self) -> float:
        """Calculate error as percentage of target"""
        if self.apogee > 0:
            return (self.error / self.apogee) * 100
        return 0.0
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage"""
        return 100.0 - self.error_percent
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"OptimizationResult(\n"
            f"  diameter={self.diameter:.4f}m,\n"
            f"  apogee={self.apogee:.2f}m,\n"
            f"  error={self.error:.2f}m ({self.error_percent:.2f}%),\n"
            f"  max_mach={self.max_mach:.3f},\n"
            f"  converged={self.converged},\n"
            f"  time={self.time:.3f}s\n"
            f")"
        )


# Example usage
if __name__ == "__main__":
    # Create result
    result = OptimizationResult(
        diameter=0.2066,
        nose_length=0.6197,
        body_length=2.0655,
        cd=0.5524,
        apogee=500.0,
        max_mach=0.200,
        error=0.0,
        converged=True,
        iterations=6,
        time=0.022
    )
    
    print("="*60)
    print("OPTIMIZATION RESULT (Type-Safe)")
    print("="*60)
    print(result)
    print()
    print(f"Accuracy: {result.accuracy:.2f}%")
    print(f"Error Percent: {result.error_percent:.2f}%")
    print()
    print("Convert to dict for backward compatibility:")
    print(result.to_dict())
    print("="*60)
