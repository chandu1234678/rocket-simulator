"""
Configuration management for rocket simulation.
Loads and validates all simulation parameters.
"""
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class RocketConfig:
    """Rocket physical properties."""
    name: str
    diameter: float  # m
    length: float  # m
    mass_initial: float  # kg
    mass_dry: float  # kg
    propellant_mass: float  # kg
    reference_area: float  # m²
    nose_cone_length: float = 0.3  # m
    body_length: float = 1.2  # m
    
    def __post_init__(self):
        """Validate rocket configuration."""
        if self.mass_initial <= self.mass_dry:
            raise ValueError("Initial mass must be greater than dry mass")
        if abs(self.mass_initial - self.mass_dry - self.propellant_mass) > 0.01:
            raise ValueError("Mass balance error: m_initial ≠ m_dry + m_propellant")
        if self.diameter <= 0 or self.length <= 0:
            raise ValueError("Dimensions must be positive")
        if self.reference_area <= 0:
            raise ValueError("Reference area must be positive")


@dataclass
class PropulsionConfig:
    """Propulsion system properties."""
    thrust_max: float  # N
    burn_time: float  # s
    specific_impulse: float  # s
    thrust_curve_type: str = "constant"
    thrust_curve_data: Optional[list] = None
    
    def __post_init__(self):
        """Validate propulsion configuration."""
        if self.thrust_max <= 0:
            raise ValueError("Thrust must be positive")
        if self.burn_time <= 0:
            raise ValueError("Burn time must be positive")
        if self.specific_impulse <= 0:
            raise ValueError("Specific impulse must be positive")


@dataclass
class AerodynamicsConfig:
    """Aerodynamic properties."""
    cd_base: float  # Base drag coefficient
    cd_friction: float = 0.219
    cd_pressure: float = 0.026
    cd_base_drag: float = 0.121
    mach_model: str = "simple"  # "simple" or "advanced"
    transonic_spike_magnitude: float = 0.5
    transonic_spike_center: float = 1.0
    transonic_spike_width: float = 0.15
    
    def __post_init__(self):
        """Validate aerodynamics configuration."""
        if self.cd_base <= 0:
            raise ValueError("Base Cd must be positive")


@dataclass
class LaunchConfig:
    """Launch site and conditions."""
    altitude: float  # m ASL
    latitude: float  # degrees
    longitude: float  # degrees
    temperature: float  # K
    pressure: float  # Pa
    wind_speed: float = 0.0  # m/s
    wind_direction: float = 0.0  # degrees
    launch_angle: float = 90.0  # degrees (90 = vertical)
    launch_rod_length: float = 3.0  # m


@dataclass
class SimulationConfig:
    """Simulation parameters."""
    timestep: float  # s
    max_time: float  # s
    solver: str = "RK4"
    adaptive_timestep: bool = False
    min_timestep: float = 0.001
    max_timestep: float = 0.1
    tolerance: float = 1e-6


@dataclass
class OptimizationConfig:
    """Optimization parameters."""
    enabled: bool = False
    target_apogee: float = 200.0  # m
    variables: list = None
    method: str = "nelder-mead"
    constraints: Dict[str, float] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = ["thrust"]
        if self.constraints is None:
            self.constraints = {}


@dataclass
class OutputConfig:
    """Output and logging configuration."""
    log_trajectory: bool = True
    log_interval: float = 0.01  # s
    export_csv: bool = True
    export_json: bool = True
    generate_plots: bool = True
    plot_types: list = None
    
    def __post_init__(self):
        if self.plot_types is None:
            self.plot_types = ["altitude", "velocity", "acceleration", "mach", "forces"]


class Config:
    """Complete simulation configuration."""
    
    def __init__(
        self,
        rocket: RocketConfig,
        propulsion: PropulsionConfig,
        aerodynamics: AerodynamicsConfig,
        launch: LaunchConfig,
        simulation: SimulationConfig,
        optimization: OptimizationConfig,
        output: OutputConfig
    ):
        self.rocket = rocket
        self.propulsion = propulsion
        self.aerodynamics = aerodynamics
        self.launch = launch
        self.simulation = simulation
        self.optimization = optimization
        self.output = output
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary."""
        return cls(
            rocket=RocketConfig(**data['rocket']),
            propulsion=PropulsionConfig(**data['propulsion']),
            aerodynamics=AerodynamicsConfig(**data['aerodynamics']),
            launch=LaunchConfig(**data['launch']),
            simulation=SimulationConfig(**data['simulation']),
            optimization=OptimizationConfig(**data['optimization']),
            output=OutputConfig(**data['output'])
        )
    
    @classmethod
    def from_json(cls, filepath: str) -> 'Config':
        """Load configuration from JSON file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'rocket': self.rocket.__dict__,
            'propulsion': self.propulsion.__dict__,
            'aerodynamics': self.aerodynamics.__dict__,
            'launch': self.launch.__dict__,
            'simulation': self.simulation.__dict__,
            'optimization': self.optimization.__dict__,
            'output': self.output.__dict__
        }
    
    def to_json(self, filepath: str):
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


def load_config(filepath: str) -> Config:
    """
    Load configuration from JSON file.
    
    Args:
        filepath: Path to JSON configuration file
        
    Returns:
        Config object with all parameters loaded and validated
    """
    return Config.from_json(filepath)
