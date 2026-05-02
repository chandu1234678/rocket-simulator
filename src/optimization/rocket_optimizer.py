"""
Rocket Optimization Wrapper
Integrates parallel optimizer with rocket simulation and supersonic flight checking
"""

import numpy as np
from typing import Dict, Any, Optional
import copy

from src.core.simulation import SimulationEngine
from src.core.config import Config
from src.optimization.parallel_optimizer import (
    ParallelRocketOptimizer,
    OptimizationConfig,
    OptimizationResult
)
from src.optimization.flight_regime_analyzer import (
    FlightRegimeAnalyzer,
    FlightRegimeAnalysis
)


class RocketDesignOptimizer:
    """
    High-level interface for optimizing rocket design parameters
    Includes supersonic flight regime checking
    """
    
    def __init__(self, base_config: Config, check_supersonic: bool = True):
        """
        Initialize optimizer with base configuration
        
        Args:
            base_config: Base simulation configuration (will be modified during optimization)
            check_supersonic: If True, check for supersonic flight and stop if detected
        """
        self.base_config = base_config
        self.simulation_cache = {}
        self.check_supersonic = check_supersonic
        self.flight_analyzer = FlightRegimeAnalyzer()
        self.last_analysis: Optional[FlightRegimeAnalysis] = None
        
    def _create_config(self, diameter: float, nose_length: float, body_length: float) -> Config:
        """Create a modified config with given parameters"""
        config = copy.deepcopy(self.base_config)
        config.rocket.diameter = diameter
        config.rocket.nose_cone_length = nose_length
        config.rocket.body_length = body_length
        config.rocket.length = nose_length + body_length
        
        # Update reference area (cross-sectional area)
        config.rocket.reference_area = np.pi * (diameter / 2) ** 2
        
        # Adjust mass based on size (simple scaling)
        original_volume = self.base_config.rocket.length * self.base_config.rocket.diameter ** 2
        new_volume = config.rocket.length * diameter ** 2
        volume_ratio = new_volume / original_volume
        
        config.rocket.mass_dry = self.base_config.rocket.mass_dry * volume_ratio
        config.rocket.mass_initial = config.rocket.mass_dry + config.rocket.propellant_mass
        
        return config
    
    def _analyze_configuration(self, config: Config) -> FlightRegimeAnalysis:
        """Analyze a configuration for flight regime"""
        # Run simulation
        sim = SimulationEngine(config)
        trajectory = sim.run()
        
        # Convert trajectory to arrays
        trajectory_data = trajectory.to_arrays()
        
        # Prepare config dict for analyzer
        config_dict = {
            'mass_initial': config.rocket.mass_initial,
            'mass_dry': config.rocket.mass_dry,
            'thrust_max': config.propulsion.thrust_max,
            'burn_time': config.propulsion.burn_time,
            'specific_impulse': config.propulsion.specific_impulse,
            'altitude_initial': config.launch.altitude,
            'temperature_initial': config.launch.temperature
        }
        
        # Analyze trajectory
        analysis = self.flight_analyzer.analyze_trajectory(trajectory_data, config_dict)
        
        return analysis
        
    def _simulation_function(self, diameter: float, nose_length: float, body_length: float) -> float:
        """
        Run simulation with given design parameters and return apogee
        
        Args:
            diameter: Rocket diameter (m)
            nose_length: Nose cone length (m)
            body_length: Body length (m)
        
        Returns:
            Apogee altitude (m)
        """
        # Create cache key
        cache_key = (round(diameter, 6), round(nose_length, 6), round(body_length, 6))
        
        # Check cache
        if cache_key in self.simulation_cache:
            return self.simulation_cache[cache_key]
        
        # Create modified config
        config = self._create_config(diameter, nose_length, body_length)
        
        # Run simulation
        sim = SimulationEngine(config)
        trajectory = sim.run()
        
        # Extract apogee
        apogee = trajectory.max_altitude
        
        # Cache result
        self.simulation_cache[cache_key] = apogee
        
        return apogee
    
    def optimize(
        self,
        target_apogee: float,
        tolerance: float = 5.0,
        diameter_range: tuple = (0.05, 0.5),
        nose_length_range: tuple = (0.1, 1.0),
        body_length_range: tuple = (0.5, 3.0),
        max_iterations: int = 100,
        methods: list = None
    ) -> Dict[str, Any]:
        """
        Optimize rocket design to achieve target apogee
        Checks for supersonic flight and provides recommendations if detected
        
        Args:
            target_apogee: Target apogee altitude (m)
            tolerance: Acceptable error in apogee (m)
            diameter_range: (min, max) diameter bounds (m)
            nose_length_range: (min, max) nose cone length bounds (m)
            body_length_range: (min, max) body length bounds (m)
            max_iterations: Maximum iterations per method
            methods: List of optimization methods to use
        
        Returns:
            Dictionary with optimization results or recommendations if supersonic
        """
        # Clear cache
        self.simulation_cache.clear()
        
        # First, check if base configuration goes supersonic
        if self.check_supersonic:
            print("\n" + "="*80)
            print("PRE-OPTIMIZATION FLIGHT REGIME CHECK")
            print("="*80)
            print("Analyzing base configuration for supersonic flight...")
            
            initial_analysis = self._analyze_configuration(self.base_config)
            self.last_analysis = initial_analysis
            
            if initial_analysis.is_supersonic:
                print(f"\n⚠️  WARNING: Base configuration is SUPERSONIC (Mach {initial_analysis.max_mach:.2f})")
                self.flight_analyzer.print_analysis(initial_analysis)
                
                return {
                    'status': 'SUPERSONIC_DETECTED',
                    'optimization_skipped': True,
                    'flight_analysis': initial_analysis,
                    'recommendations': initial_analysis.recommendations,
                    'message': 'Optimization stopped: Rocket goes supersonic. See recommendations.'
                }
            else:
                print(f"✓ Base configuration is {initial_analysis}")
                print("Proceeding with optimization...\n")
        
        # Create optimization config
        opt_config = OptimizationConfig(
            target_apogee=target_apogee,
            tolerance=tolerance,
            diameter_min=diameter_range[0],
            diameter_max=diameter_range[1],
            nose_length_min=nose_length_range[0],
            nose_length_max=nose_length_range[1],
            body_length_min=body_length_range[0],
            body_length_max=body_length_range[1],
            max_iterations=max_iterations,
            methods=methods
        )
        
        # Create optimizer
        optimizer = ParallelRocketOptimizer(self._simulation_function, opt_config)
        
        # Run optimization
        results = optimizer.optimize_parallel()
        
        # Check if best result goes supersonic
        if self.check_supersonic and results:
            best = results[0]
            best_config = self._create_config(best.diameter, best.nose_cone_length, best.body_length)
            best_analysis = self._analyze_configuration(best_config)
            self.last_analysis = best_analysis
            
            if best_analysis.is_supersonic:
                print(f"\n⚠️  WARNING: Optimized design is SUPERSONIC (Mach {best_analysis.max_mach:.2f})")
                self.flight_analyzer.print_analysis(best_analysis)
                
                return {
                    'status': 'SUPERSONIC_DETECTED',
                    'optimization_completed': True,
                    'optimized_design': {
                        'diameter': best.diameter,
                        'nose_cone_length': best.nose_cone_length,
                        'body_length': best.body_length,
                        'apogee': best.apogee
                    },
                    'flight_analysis': best_analysis,
                    'recommendations': best_analysis.recommendations,
                    'message': 'Optimized design goes supersonic. See recommendations.'
                }
        
        # Print summary
        optimizer.print_summary(results)
        
        # Export results
        optimizer.export_results("optimization_results.json")
        
        # Return best result as dictionary
        best = results[0]
        return {
            'status': 'SUCCESS',
            'success': best.success,
            'diameter': best.diameter,
            'nose_cone_length': best.nose_cone_length,
            'body_length': best.body_length,
            'total_length': best.nose_cone_length + best.body_length,
            'apogee': best.apogee,
            'target_apogee': target_apogee,
            'error': best.error,
            'error_percent': 100 * best.error / target_apogee,
            'method': best.method,
            'iterations': best.iterations,
            'computation_time': best.computation_time,
            'flight_analysis': self.last_analysis,
            'all_results': results
        }
    
    def optimize_from_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run optimization using configuration dictionary
        
        Args:
            config_dict: Configuration dictionary with optimization parameters
        
        Returns:
            Dictionary with optimization results
        """
        opt_params = config_dict.get('optimization', {})
        
        return self.optimize(
            target_apogee=opt_params.get('target_apogee', 200.0),
            tolerance=opt_params.get('tolerance', 5.0),
            diameter_range=tuple(opt_params.get('diameter_range', [0.05, 0.5])),
            nose_length_range=tuple(opt_params.get('nose_length_range', [0.1, 1.0])),
            body_length_range=tuple(opt_params.get('body_length_range', [0.5, 3.0])),
            max_iterations=opt_params.get('max_iterations', 100),
            methods=opt_params.get('methods', None)
        )


def run_optimization_example():
    """Example of running optimization with supersonic checking"""
    from src.core.config import load_config
    
    # Load base configuration
    config = load_config("data/config.json")
    
    # Create optimizer with supersonic checking enabled
    optimizer = RocketDesignOptimizer(config, check_supersonic=True)
    
    # Run optimization
    result = optimizer.optimize(
        target_apogee=300.0,  # Target 300m apogee
        tolerance=5.0,         # Within 5m
        diameter_range=(0.1, 0.3),
        nose_length_range=(0.2, 0.6),
        body_length_range=(0.8, 2.0),
        max_iterations=50
    )
    
    # Check result status
    if result['status'] == 'SUPERSONIC_DETECTED':
        print("\n⚠️  OPTIMIZATION STOPPED: Supersonic flight detected!")
        print("See recommendations above for propulsion modifications.")
    else:
        print("\nOptimization Complete!")
        print(f"Best Design:")
        print(f"  Diameter: {result['diameter']:.4f} m")
        print(f"  Nose Length: {result['nose_cone_length']:.4f} m")
        print(f"  Body Length: {result['body_length']:.4f} m")
        print(f"  Apogee: {result['apogee']:.2f} m (target: {result['target_apogee']:.2f} m)")
        print(f"  Error: {result['error']:.2f} m ({result['error_percent']:.2f}%)")
    
    return result


if __name__ == "__main__":
    run_optimization_example()
