"""
Rocket Configuration Validator
Prevents inconsistent or invalid rocket parameters for optimization
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidatedRocketConfig:
    """
    Validated rocket configuration for optimization
    
    All parameters must be physically consistent:
    - Propellant mass = mass_initial - mass_dry
    - Burn time = propellant_mass / mass_flow_rate
    - Mass flow rate = thrust / (specific_impulse * g0)
    
    The burn_time parameter is optional and will be calculated if not provided.
    If provided, it will be validated against the calculated value.
    """
    
    # Required parameters
    thrust: float  # Thrust force (N)
    specific_impulse: float  # Specific impulse (s)
    mass_initial: float  # Initial total mass (kg)
    mass_dry: float  # Dry mass without propellant (kg)
    
    # Optional parameters
    burn_time: Optional[float] = None  # Burn duration (s) - calculated if not provided
    
    # Physical constants
    g0: float = 9.81  # Standard gravity (m/s²)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()
        
        # Calculate burn time if not provided
        if self.burn_time is None:
            self.burn_time = self.calculate_burn_time()
        else:
            # Validate provided burn time
            calculated_burn_time = self.calculate_burn_time()
            relative_error = abs(self.burn_time - calculated_burn_time) / calculated_burn_time
            
            if relative_error > 0.1:  # 10% tolerance
                raise ValueError(
                    f"Provided burn_time ({self.burn_time:.3f}s) is inconsistent with "
                    f"propellant mass and thrust. Calculated burn_time: {calculated_burn_time:.3f}s. "
                    f"Relative error: {relative_error*100:.1f}%. "
                    f"Either remove burn_time to auto-calculate, or adjust propellant mass."
                )
    
    def validate(self):
        """
        Validate all parameters
        
        Raises:
            ValueError: If any parameter is invalid
        """
        errors = []
        
        # Check positive values
        if self.thrust <= 0:
            errors.append(f"thrust must be positive, got {self.thrust}")
        
        if self.specific_impulse <= 0:
            errors.append(f"specific_impulse must be positive, got {self.specific_impulse}")
        
        if self.mass_initial <= 0:
            errors.append(f"mass_initial must be positive, got {self.mass_initial}")
        
        if self.mass_dry <= 0:
            errors.append(f"mass_dry must be positive, got {self.mass_dry}")
        
        if self.burn_time is not None and self.burn_time <= 0:
            errors.append(f"burn_time must be positive, got {self.burn_time}")
        
        # Check mass relationship
        if self.mass_initial <= self.mass_dry:
            errors.append(
                f"mass_initial ({self.mass_initial}) must be greater than "
                f"mass_dry ({self.mass_dry}). Propellant mass would be "
                f"{self.mass_initial - self.mass_dry:.3f} kg."
            )
        
        # Check reasonable ranges
        if self.thrust > 10000:
            errors.append(f"thrust ({self.thrust}N) seems unreasonably high for model rocket")
        
        if self.specific_impulse > 500:
            errors.append(f"specific_impulse ({self.specific_impulse}s) seems unreasonably high")
        
        if self.mass_initial > 100:
            errors.append(f"mass_initial ({self.mass_initial}kg) seems unreasonably high for model rocket")
        
        # Propellant mass check
        propellant_mass = self.mass_initial - self.mass_dry
        if propellant_mass < 0.01:
            errors.append(
                f"Propellant mass ({propellant_mass:.4f}kg) is too small. "
                f"Minimum recommended: 0.01kg"
            )
        
        if propellant_mass > self.mass_initial * 0.5:
            errors.append(
                f"Propellant mass ({propellant_mass:.3f}kg) is more than 50% of total mass. "
                f"This is unusual for solid rockets."
            )
        
        if errors:
            raise ValueError("Rocket configuration validation failed:\n  " + "\n  ".join(errors))
    
    def calculate_burn_time(self) -> float:
        """
        Calculate burn time from propellant mass and thrust
        
        Returns:
            Burn time in seconds
        """
        propellant_mass = self.mass_initial - self.mass_dry
        mass_flow_rate = self.thrust / (self.specific_impulse * self.g0)
        burn_time = propellant_mass / mass_flow_rate
        return burn_time
    
    def get_mass_flow_rate(self) -> float:
        """Get mass flow rate (kg/s)"""
        return self.thrust / (self.specific_impulse * self.g0)
    
    def get_propellant_mass(self) -> float:
        """Get propellant mass (kg)"""
        return self.mass_initial - self.mass_dry
    
    def to_dict(self) -> dict:
        """Convert to dictionary for compatibility with existing code"""
        return {
            'thrust': self.thrust,
            'burn_time': self.burn_time,
            'specific_impulse': self.specific_impulse,
            'mass_initial': self.mass_initial,
            'mass_dry': self.mass_dry
        }
    
    @classmethod
    def from_dict(cls, config: dict) -> 'ValidatedRocketConfig':
        """
        Create ValidatedRocketConfig from dictionary
        
        Args:
            config: Dictionary with rocket parameters
        
        Returns:
            Validated ValidatedRocketConfig instance
        """
        return cls(
            thrust=config['thrust'],
            specific_impulse=config['specific_impulse'],
            mass_initial=config['mass_initial'],
            mass_dry=config['mass_dry'],
            burn_time=config.get('burn_time')  # Optional
        )
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"ValidatedRocketConfig(\n"
            f"  thrust={self.thrust:.1f}N,\n"
            f"  burn_time={self.burn_time:.3f}s,\n"
            f"  specific_impulse={self.specific_impulse:.0f}s,\n"
            f"  mass_initial={self.mass_initial:.3f}kg,\n"
            f"  mass_dry={self.mass_dry:.3f}kg,\n"
            f"  propellant_mass={self.get_propellant_mass():.3f}kg,\n"
            f"  mass_flow_rate={self.get_mass_flow_rate():.4f}kg/s\n"
            f")"
        )
