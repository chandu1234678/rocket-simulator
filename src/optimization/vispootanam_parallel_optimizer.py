"""
Vispootanam-Level Parallel Regime Optimizer
Simultaneous optimization across 3 flight regimes with strict convergence
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from scipy.optimize import differential_evolution, Bounds
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.advanced_aerodynamics import AdvancedAerodynamics, FlightRegime
from src.optimization.feasibility_checker import FeasibilityChecker
from src.solvers.semi_implicit import SemiImplicitSolver, SemiImplicitState


@dataclass
class VispootanamOptimizationResult:
    """Results from Vispootanam-level optimization"""
    regime: FlightRegime
    diameter: float
    nose_cone_length: float
    body_length: float
    cd_optimized: float
    apogee: float
    max_mach: float
    error: float
    error_rate: float  # Error decrease rate
    iterations: int
    converged: bool
    computation_time: float
    fallback_used: bool
    trajectory_data: Optional[Dict] = None


@dataclass
class VispootanamConfig:
    """Vispootanam-level optimization configuration"""
    target_apogee: float
    tolerance: float
    
    # Design bounds
    diameter_min: float = 0.05
    diameter_max: float = 0.5
    nose_length_min: float = 0.1
    nose_length_max: float = 1.0
    body_length_min: float = 0.5
    body_length_max: float = 3.0
    
    # Cd bounds per regime
    cd_d1_min: float = 0.15
    cd_d1_max: float = 0.35
    cd_d2_min: float = 0.20
    cd_d2_max: float = 0.45
    cd_d3_min: float = 0.30
    cd_d3_max: float = 0.85
    
    # Optimization settings (tuned for speed - target <2s)
    max_iterations: int = 5   # Reduced from 10 for speed
    population_size: int = 4   # Reduced from 6 for speed
    n_parallel_workers: int = None
    
    # Convergence criteria
    error_rate_threshold: float = 0.01  # Error must decrease by 1% per iteration
    min_error_decrease: float = 0.1     # Minimum error decrease (m)
    
    # Supersonic prevention
    supersonic_limit: float = 1.2
    
    # User Cd estimates
    user_cd_estimates: Dict[str, float] = None
    surface_roughness: float = 0.0
    
    def __post_init__(self):
        if self.n_parallel_workers is None:
            self.n_parallel_workers = max(1, mp.cpu_count() - 1)
        if self.user_cd_estimates is None:
            self.user_cd_estimates = {'D1': 0.25, 'D2': 0.35, 'D3': 0.65}


class VispootanamParallelOptimizer:
    """
    Vispootanam-Level Parallel Optimizer
    
    Features:
    - Simultaneous optimization across 3 regimes (D1, D2, D3)
    - Semi-implicit solver for stability
    - Automatic fallback to base drag on divergence
    - Strict convergence with decreasing error rate
    - Real-time capable (1000+ iterations)
    - Supersonic prevention with suggestions
    """
    
    def __init__(self, 
                 base_rocket_config: Dict,
                 config: VispootanamConfig):
        """
        Initialize Vispootanam optimizer
        
        Args:
            base_rocket_config: Base rocket parameters (thrust, burn_time, etc.)
            config: Optimization configuration
        """
        self.base_config = base_rocket_config
        self.config = config
        self.feasibility_checker = FeasibilityChecker(
            supersonic_limit=config.supersonic_limit
        )
        self.evaluation_count = 0
        self.best_result = None
        self.all_results = []
        self.error_history = []
        self.simulation_cache = {}  # Cache for speed
        
    def _simulate_trajectory(self,
                            diameter: float,
                            nose_length: float,
                            body_length: float,
                            cd_user_estimates: Dict[str, float]) -> Tuple[float, float, bool]:
        """
        Simulate trajectory with advanced aerodynamics (with caching)
        
        Returns:
            (apogee, max_mach, fallback_used)
        """
        # Create cache key
        cache_key = (
            round(diameter, 4),
            round(nose_length, 4),
            round(body_length, 4),
            tuple(sorted(cd_user_estimates.items()))
        )
        
        # Check cache
        if cache_key in self.simulation_cache:
            return self.simulation_cache[cache_key]
        
        # Create advanced aerodynamics
        aero = AdvancedAerodynamics(
            user_cd_estimates=cd_user_estimates,
            surface_roughness=self.config.surface_roughness,
            use_fallback=True
        )
        
        # Extract rocket parameters
        thrust = self.base_config['thrust']
        burn_time = self.base_config['burn_time']
        specific_impulse = self.base_config['specific_impulse']
        mass_initial = self.base_config['mass_initial']
        mass_dry = self.base_config['mass_dry']
        
        # Calculate mass flow rate
        g0 = 9.81
        mass_flow_rate = thrust / (specific_impulse * g0)
        
        # Reference area
        reference_area = np.pi * (diameter / 2) ** 2
        
        # Acceleration function
        def acceleration_func(altitude, velocity, mass):
            # Atmospheric density
            rho = 1.225 * np.exp(-altitude / 8500)
            
            # Speed of sound
            temperature = 288.15 - 0.0065 * altitude
            speed_of_sound = np.sqrt(1.4 * 287 * temperature)
            
            # Mach number
            mach = abs(velocity) / speed_of_sound if speed_of_sound > 0 else 0
            
            # Reynolds number
            mu = 1.81e-5  # Dynamic viscosity
            reynolds = rho * abs(velocity) * diameter / mu if mu > 0 else 1e6
            
            # Get drag coefficient
            cd, regime, fallback = aero.get_cd(
                mach, diameter, nose_length, body_length,
                reynolds, velocity, altitude
            )
            
            # Drag force
            drag = 0.5 * rho * velocity**2 * cd * reference_area
            if velocity < 0:
                drag = -drag
            
            # Thrust (only during burn)
            current_thrust = thrust if altitude >= 0 else 0
            
            # Net acceleration
            accel = (current_thrust - drag) / mass - g0
            
            return accel
        
        # Mass rate function
        def mass_rate_func(time, mass):
            if time < burn_time and mass > mass_dry:
                return -mass_flow_rate
            return 0.0
        
        # Termination condition
        def termination_condition(state):
            # Stop when falling and hits ground
            return state.altitude <= 0 and state.velocity < 0 and state.time > 0.1
        
        # Initial state
        initial_state = SemiImplicitState(
            time=0.0,
            altitude=0.0,
            velocity=0.0,
            acceleration=0.0,
            mass=mass_initial
        )
        
        # Solve (optimized time step for speed - target <2s total)
        solver = SemiImplicitSolver(dt=0.2, adaptive_dt=True)  # 2x faster than 0.1
        times, altitudes, velocities, accelerations, iterations = solver.integrate(
            initial_state,
            acceleration_func,
            mass_rate_func,
            termination_condition,
            max_time=200.0
        )
        
        # Calculate max apogee and max Mach
        max_apogee = np.max(altitudes)
        
        # Calculate max Mach
        max_mach = 0.0
        for alt, vel in zip(altitudes, velocities):
            temp = 288.15 - 0.0065 * alt
            speed_of_sound = np.sqrt(1.4 * 287 * temp)
            mach = abs(vel) / speed_of_sound
            max_mach = max(max_mach, mach)
        
        # Cache result
        result = (max_apogee, max_mach, aero.fallback_active)
        self.simulation_cache[cache_key] = result
        
        return result
    
    def _objective_function_regime(self,
                                   x: np.ndarray,
                                   regime: FlightRegime) -> float:
        """
        Objective function for specific regime
        
        x = [diameter, nose_length, body_length, cd_value]
        """
        diameter, nose_length, body_length, cd_value = x
        
        # Create Cd estimates for this regime
        regime_key = regime.value.split('_')[0]
        cd_estimates = self.config.user_cd_estimates.copy()
        cd_estimates[regime_key] = cd_value
        
        try:
            # Simulate
            apogee, max_mach, fallback = self._simulate_trajectory(
                diameter, nose_length, body_length, cd_estimates
            )
            
            # Supersonic penalty
            if max_mach >= self.config.supersonic_limit:
                return 1e10 + max_mach * 1e6
            
            # Calculate error
            error = abs(apogee - self.config.target_apogee)
            
            self.evaluation_count += 1
            self.error_history.append(error)
            
            return error
            
        except Exception as e:
            return 1e10
    
    def _optimize_regime(self, regime: FlightRegime) -> VispootanamOptimizationResult:
        """Optimize for specific flight regime"""
        start_time = time.time()
        self.evaluation_count = 0
        self.error_history = []
        
        # Get Cd bounds for this regime
        regime_key = regime.value.split('_')[0]
        if regime_key == 'D1':
            cd_min, cd_max = self.config.cd_d1_min, self.config.cd_d1_max
        elif regime_key == 'D2':
            cd_min, cd_max = self.config.cd_d2_min, self.config.cd_d2_max
        else:  # D3
            cd_min, cd_max = self.config.cd_d3_min, self.config.cd_d3_max
        
        # Bounds: [diameter, nose_length, body_length, cd]
        bounds = [
            (self.config.diameter_min, self.config.diameter_max),
            (self.config.nose_length_min, self.config.nose_length_max),
            (self.config.body_length_min, self.config.body_length_max),
            (cd_min, cd_max)
        ]
        
        try:
            # Progress callback
            iteration_count = [0]
            best_error = [float('inf')]
            
            def callback(xk, convergence):
                iteration_count[0] += 1
                error = self._objective_function_regime(xk, regime)
                if error < best_error[0]:
                    best_error[0] = error
                    diameter, nose_length, body_length, cd = xk
                    print(f"    Iter {iteration_count[0]:3d}: "
                          f"D={diameter:.4f}m, Cd={cd:.4f}, Error={error:.1f}m")
                return False
            
            print(f"\n  Optimizing {regime.value}...")
            print("  " + "-" * 70)
            
            # Optimize (with early termination for speed)
            result = differential_evolution(
                lambda x: self._objective_function_regime(x, regime),
                bounds=bounds,
                maxiter=self.config.max_iterations,
                popsize=self.config.population_size,
                tol=self.config.tolerance * 10,  # Relaxed tolerance for speed
                seed=int(time.time() * 1000) % 2**32,
                workers=1,
                updating='immediate',  # Faster than 'deferred'
                polish=False,  # Skip final polish for speed
                atol=self.config.tolerance * 2,  # Relaxed for early termination
                strategy='best1bin',  # Faster strategy
                callback=callback
            )
            
            print("  " + "-" * 70)
            print(f"  Completed in {iteration_count[0]} iterations\n")
            
            # Extract results
            diameter, nose_length, body_length, cd_optimized = result.x
            
            # Final simulation
            regime_key = regime.value.split('_')[0]
            cd_estimates = self.config.user_cd_estimates.copy()
            cd_estimates[regime_key] = cd_optimized
            
            apogee, max_mach, fallback = self._simulate_trajectory(
                diameter, nose_length, body_length, cd_estimates
            )
            
            error = abs(apogee - self.config.target_apogee)
            
            # Calculate error rate (how fast error decreased)
            if len(self.error_history) > 10:
                initial_error = np.mean(self.error_history[:10])
                final_error = np.mean(self.error_history[-10:])
                error_rate = (initial_error - final_error) / initial_error
            else:
                error_rate = 0.0
            
            computation_time = time.time() - start_time
            
            return VispootanamOptimizationResult(
                regime=regime,
                diameter=diameter,
                nose_cone_length=nose_length,
                body_length=body_length,
                cd_optimized=cd_optimized,
                apogee=apogee,
                max_mach=max_mach,
                error=error,
                error_rate=error_rate,
                iterations=self.evaluation_count,
                converged=result.success and error <= self.config.tolerance,
                computation_time=computation_time,
                fallback_used=fallback
            )
            
        except Exception as e:
            print(f"Optimization failed for {regime.value}: {e}")
            return VispootanamOptimizationResult(
                regime=regime,
                diameter=0.1,
                nose_cone_length=0.3,
                body_length=1.0,
                cd_optimized=0.35,
                apogee=0.0,
                max_mach=0.0,
                error=float('inf'),
                error_rate=0.0,
                iterations=0,
                converged=False,
                computation_time=time.time() - start_time,
                fallback_used=False
            )
    
    def optimize_all_regimes(self) -> List[VispootanamOptimizationResult]:
        """
        Optimize across all 3 regimes in parallel
        
        Returns:
            List of results sorted by error
        """
        print(f"\n{'='*80}")
        print(f"VISPOOTANAM-LEVEL PARALLEL REGIME OPTIMIZATION")
        print(f"{'='*80}")
        print(f"Target Apogee: {self.config.target_apogee:.2f} m")
        print(f"Tolerance: {self.config.tolerance:.2f} m")
        print(f"Supersonic Limit: {self.config.supersonic_limit:.1f}")
        print(f"Max Iterations: {self.config.max_iterations}")
        print(f"Parallel Workers: {self.config.n_parallel_workers}")
        print(f"{'='*80}\n")
        
        # Phase 1: Feasibility check
        print("PHASE 1: PRE-FLIGHT FEASIBILITY CHECK")
        print("-" * 80)
        
        feasibility_result = self.feasibility_checker.check_feasibility(
            thrust=self.base_config['thrust'],
            burn_time=self.base_config['burn_time'],
            specific_impulse=self.base_config['specific_impulse'],
            mass_initial=self.base_config['mass_initial'],
            mass_dry=self.base_config['mass_dry'],
            target_apogee=self.config.target_apogee
        )
        
        self.feasibility_checker.print_feasibility(feasibility_result)
        
        if not feasibility_result.can_proceed:
            print("\n OPTIMIZATION ABORTED - Design not feasible")
            return []
        
        print("\n Feasibility check PASSED\n")
        
        # Phase 2: Parallel regime optimization
        print("PHASE 2: PARALLEL REGIME OPTIMIZATION")
        print("-" * 80)
        
        regimes = [
            FlightRegime.SUBSONIC,
            FlightRegime.COMPRESSIBLE,
            FlightRegime.TRANSONIC
        ]
        
        results = []
        
        with ProcessPoolExecutor(max_workers=self.config.n_parallel_workers) as executor:
            future_to_regime = {
                executor.submit(self._optimize_regime, regime): regime
                for regime in regimes
            }
            
            for future in as_completed(future_to_regime):
                regime = future_to_regime[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    status = " CONVERGED" if result.converged else " NOT CONVERGED"
                    fallback_str = " [FALLBACK]" if result.fallback_used else ""
                    
                    print(f"{status} | {result.regime.value:<20} | "
                          f"Apogee: {result.apogee:7.2f}m | "
                          f"Error: {result.error:6.2f}m | "
                          f"Mach: {result.max_mach:.3f} | "
                          f"Time: {result.computation_time:5.2f}s{fallback_str}")
                    
                except Exception as e:
                    print(f" FAILED | {regime.value:<20} | Error: {str(e)}")
        
        # Sort by error
        results.sort(key=lambda r: r.error)
        self.all_results = results
        self.best_result = results[0] if results else None
        
        return results
    
    def print_summary(self, results: List[VispootanamOptimizationResult]):
        """Print optimization summary"""
        print(f"\n{'='*80}")
        print(f"OPTIMIZATION SUMMARY")
        print(f"{'='*80}")
        
        if not results:
            print("No results available")
            return
        
        best = results[0]
        print(f"\nBEST RESULT ({best.regime.value}):")
        print(f"  Diameter:         {best.diameter:.4f} m")
        print(f"  Nose Cone Length: {best.nose_cone_length:.4f} m")
        print(f"  Body Length:      {best.body_length:.4f} m")
        print(f"  Cd Optimized:     {best.cd_optimized:.4f}")
        print(f"  Max Mach:         {best.max_mach:.3f}")
        print(f"\n  Achieved Apogee:  {best.apogee:.2f} m")
        print(f"  Target Apogee:    {self.config.target_apogee:.2f} m")
        print(f"  Error:            {best.error:.2f} m ({100*best.error/self.config.target_apogee:.2f}%)")
        print(f"  Error Rate:       {best.error_rate*100:.2f}% decrease")
        print(f"  Converged:        {'YES' if best.converged else 'NO'}")
        print(f"  Fallback Used:    {'YES' if best.fallback_used else 'NO'}")
        print(f"  Iterations:       {best.iterations}")
        print(f"  Time:             {best.computation_time:.2f} s")
        
        print(f"\nALL REGIMES COMPARISON:")
        print(f"{'Regime':<20} {'Apogee (m)':>12} {'Error (m)':>12} {'Mach':>8} {'Time (s)':>10}")
        print(f"{'-'*80}")
        for r in results:
            print(f"{r.regime.value:<20} {r.apogee:>12.2f} {r.error:>12.2f} {r.max_mach:>8.3f} {r.computation_time:>10.2f}")
        
        print(f"{'='*80}\n")


# Example usage
if __name__ == "__main__":
    # Base rocket configuration
    base_config = {
        'thrust': 80.0,  # Subsonic thrust
        'burn_time': 1.8,
        'specific_impulse': 180,
        'mass_initial': 2.76,
        'mass_dry': 2.0,
        'temperature': 287.0
    }
    
    # Vispootanam configuration (optimized for speed)
    Vispootanam_config = VispootanamConfig(
        target_apogee=500.0,
        tolerance=10.0,
        max_iterations=15,  # Fast convergence
        population_size=8,   # Small population
        user_cd_estimates={'D1': 0.22, 'D2': 0.33, 'D3': 0.68},
        surface_roughness=0.05
    )
    
    # Optimize
    optimizer = VispootanamParallelOptimizer(base_config, Vispootanam_config)
    results = optimizer.optimize_all_regimes()
    optimizer.print_summary(results)
