"""
Parallel Optimization Module for Rocket Design
Optimizes diameter, nose cone length, and body length to achieve target apogee
Includes pre-flight feasibility checking
"""

import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from scipy.optimize import minimize, differential_evolution, Bounds
import time

from src.optimization.feasibility_checker import FeasibilityChecker, FeasibilityResult


@dataclass
class OptimizationResult:
    """Results from optimization run"""
    diameter: float
    nose_cone_length: float
    body_length: float
    apogee: float
    error: float
    iterations: int
    success: bool
    method: str
    computation_time: float
    trajectory_data: Optional[Dict] = None


@dataclass
class OptimizationConfig:
    """Configuration for optimization"""
    target_apogee: float
    tolerance: float
    
    # Design variable bounds
    diameter_min: float = 0.05
    diameter_max: float = 0.5
    nose_length_min: float = 0.1
    nose_length_max: float = 1.0
    body_length_min: float = 0.5
    body_length_max: float = 3.0
    
    # Optimization settings
    max_iterations: int = 100
    population_size: int = 15
    n_parallel_workers: int = None  # None = use all CPU cores
    
    # Constraints
    length_to_diameter_ratio_min: float = 5.0
    length_to_diameter_ratio_max: float = 20.0
    nose_to_body_ratio_min: float = 0.1
    nose_to_body_ratio_max: float = 0.5
    
    # Optimization methods to run in parallel
    methods: List[str] = None
    
    def __post_init__(self):
        if self.n_parallel_workers is None:
            self.n_parallel_workers = max(1, mp.cpu_count() - 1)
        if self.methods is None:
            self.methods = ['differential_evolution', 'nelder-mead', 'powell', 'slsqp']


class ParallelRocketOptimizer:
    """
    Parallel optimizer for rocket design parameters
    Optimizes diameter, nose cone length, and body length to achieve target apogee
    Includes pre-flight feasibility checking
    """
    
    def __init__(self, simulation_function: Callable, config: OptimizationConfig, 
                 base_rocket_config: Optional[Dict] = None):
        """
        Initialize optimizer
        
        Args:
            simulation_function: Function that takes (diameter, nose_length, body_length, base_config)
                                and returns apogee altitude
            config: Optimization configuration
            base_rocket_config: Base rocket configuration for feasibility check
        """
        self.simulate = simulation_function
        self.config = config
        self.evaluation_count = 0
        self.best_result = None
        self.all_results = []
        self.base_rocket_config = base_rocket_config
        self.feasibility_checker = FeasibilityChecker()
        self.feasibility_result = None
        
    def _objective_function(self, x: np.ndarray) -> float:
        """
        Objective function to minimize
        Returns squared error from target apogee
        """
        diameter, nose_length, body_length = x
        
        # Check constraints
        if not self._check_constraints(diameter, nose_length, body_length):
            return 1e10  # Large penalty for constraint violation
        
        try:
            # Run simulation
            apogee = self.simulate(diameter, nose_length, body_length)
            
            # Calculate error (we want to minimize this)
            error = abs(apogee - self.config.target_apogee)
            
            self.evaluation_count += 1
            
            return error
            
        except Exception as e:
            print(f"Simulation failed: {e}")
            return 1e10
    
    def _check_constraints(self, diameter: float, nose_length: float, body_length: float) -> bool:
        """Check if design satisfies constraints"""
        total_length = nose_length + body_length
        
        # Length to diameter ratio
        l_d_ratio = total_length / diameter
        if l_d_ratio < self.config.length_to_diameter_ratio_min or \
           l_d_ratio > self.config.length_to_diameter_ratio_max:
            return False
        
        # Nose to body ratio
        nose_body_ratio = nose_length / body_length
        if nose_body_ratio < self.config.nose_to_body_ratio_min or \
           nose_body_ratio > self.config.nose_to_body_ratio_max:
            return False
        
        return True
    
    def _optimize_with_method(self, method: str, x0: np.ndarray) -> OptimizationResult:
        """
        Run optimization with a specific method
        """
        start_time = time.time()
        self.evaluation_count = 0
        
        bounds = Bounds(
            [self.config.diameter_min, self.config.nose_length_min, self.config.body_length_min],
            [self.config.diameter_max, self.config.nose_length_max, self.config.body_length_max]
        )
        
        try:
            if method == 'differential_evolution':
                # Global optimization method
                result = differential_evolution(
                    self._objective_function,
                    bounds=list(zip(bounds.lb, bounds.ub)),
                    maxiter=self.config.max_iterations,
                    popsize=self.config.population_size,
                    tol=self.config.tolerance,
                    seed=int(time.time() * 1000) % 2**32,
                    workers=1,  # Each method runs in its own process
                    updating='deferred',
                    polish=True
                )
            elif method in ['nelder-mead', 'powell']:
                # Derivative-free methods
                result = minimize(
                    self._objective_function,
                    x0,
                    method=method,
                    bounds=bounds,
                    options={
                        'maxiter': self.config.max_iterations,
                        'xatol': self.config.tolerance,
                        'fatol': self.config.tolerance
                    }
                )
            elif method == 'slsqp':
                # Sequential Least Squares Programming
                result = minimize(
                    self._objective_function,
                    x0,
                    method='SLSQP',
                    bounds=bounds,
                    options={
                        'maxiter': self.config.max_iterations,
                        'ftol': self.config.tolerance
                    }
                )
            else:
                raise ValueError(f"Unknown optimization method: {method}")
            
            # Extract results
            diameter, nose_length, body_length = result.x
            apogee = self.simulate(diameter, nose_length, body_length)
            error = abs(apogee - self.config.target_apogee)
            
            computation_time = time.time() - start_time
            
            return OptimizationResult(
                diameter=diameter,
                nose_cone_length=nose_length,
                body_length=body_length,
                apogee=apogee,
                error=error,
                iterations=self.evaluation_count,
                success=result.success and error <= self.config.tolerance,
                method=method,
                computation_time=computation_time
            )
            
        except Exception as e:
            print(f"Optimization with {method} failed: {e}")
            computation_time = time.time() - start_time
            return OptimizationResult(
                diameter=x0[0],
                nose_cone_length=x0[1],
                body_length=x0[2],
                apogee=0.0,
                error=float('inf'),
                iterations=self.evaluation_count,
                success=False,
                method=method,
                computation_time=computation_time
            )
    
    def optimize_parallel(self, initial_guess: Optional[np.ndarray] = None, 
                         skip_feasibility_check: bool = False) -> List[OptimizationResult]:
        """
        Run multiple optimization methods in parallel
        
        Args:
            initial_guess: Initial guess [diameter, nose_length, body_length]
                          If None, uses midpoint of bounds
            skip_feasibility_check: Skip pre-flight feasibility check (default: False)
        
        Returns:
            List of OptimizationResult objects, sorted by error
        """
        if initial_guess is None:
            initial_guess = np.array([
                (self.config.diameter_min + self.config.diameter_max) / 2,
                (self.config.nose_length_min + self.config.nose_length_max) / 2,
                (self.config.body_length_min + self.config.body_length_max) / 2
            ])
        
        # PRE-FLIGHT FEASIBILITY CHECK
        if not skip_feasibility_check and self.base_rocket_config is not None:
            print(f"\n{'='*80}")
            print(f"PHASE 1: PRE-FLIGHT FEASIBILITY CHECK")
            print(f"{'='*80}")
            print(f"Checking if target is reachable without going supersonic...")
            print(f"(This takes 2 seconds vs 20 minutes for full optimization)")
            
            feasibility_start = time.time()
            
            # Extract rocket parameters from base config
            self.feasibility_result = self.feasibility_checker.check_feasibility(
                thrust=self.base_rocket_config.get('thrust', 747.1),
                burn_time=self.base_rocket_config.get('burn_time', 1.8),
                specific_impulse=self.base_rocket_config.get('specific_impulse', 180),
                mass_initial=self.base_rocket_config.get('mass_initial', 2.76),
                mass_dry=self.base_rocket_config.get('mass_dry', 2.0),
                target_apogee=self.config.target_apogee,
                temperature=self.base_rocket_config.get('temperature', 287.0)
            )
            
            feasibility_time = time.time() - feasibility_start
            
            # Print results
            self.feasibility_checker.print_feasibility(self.feasibility_result)
            print(f"\nFeasibility check completed in {feasibility_time:.2f}s")
            
            # Stop if not feasible
            if not self.feasibility_result.can_proceed:
                print(f"\n{'='*80}")
                print(f" OPTIMIZATION ABORTED")
                print(f"{'='*80}")
                print(f"Design is not feasible. Please modify rocket parameters as suggested above.")
                print(f"Time saved: ~20 minutes")
                print(f"{'='*80}\n")
                return []
            
            print(f"\n Feasibility check PASSED - proceeding with optimization...")
        
        print(f"\n{'='*80}")
        print(f"PHASE 2: PARALLEL ROCKET OPTIMIZATION")
        print(f"{'='*80}")
        print(f"Target Apogee: {self.config.target_apogee:.2f} m")
        print(f"Tolerance: {self.config.tolerance:.2f} m")
        print(f"Methods: {', '.join(self.config.methods)}")
        print(f"Parallel Workers: {self.config.n_parallel_workers}")
        print(f"Initial Guess: D={initial_guess[0]:.3f}m, Nose={initial_guess[1]:.3f}m, Body={initial_guess[2]:.3f}m")
        print(f"{'='*80}\n")
        
        results = []
        
        # Run optimizations in parallel
        with ProcessPoolExecutor(max_workers=self.config.n_parallel_workers) as executor:
            # Submit all optimization tasks
            future_to_method = {
                executor.submit(self._optimize_with_method, method, initial_guess): method
                for method in self.config.methods
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_method):
                method = future_to_method[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Print progress
                    status = " CONVERGED" if result.success else " NOT CONVERGED"
                    print(f"{status} | {result.method:20s} | "
                          f"Apogee: {result.apogee:7.2f}m | "
                          f"Error: {result.error:6.2f}m | "
                          f"Time: {result.computation_time:5.2f}s | "
                          f"Iters: {result.iterations:4d}")
                    
                except Exception as e:
                    print(f" FAILED | {method:20s} | Error: {str(e)}")
        
        # Sort results by error
        results.sort(key=lambda r: r.error)
        self.all_results = results
        self.best_result = results[0] if results else None
        
        return results
    
    def print_summary(self, results: List[OptimizationResult]):
        """Print summary of optimization results"""
        print(f"\n{'='*80}")
        print(f"OPTIMIZATION SUMMARY")
        print(f"{'='*80}")
        
        if not results:
            print("No results available")
            return
        
        best = results[0]
        print(f"\nBEST RESULT ({best.method}):")
        print(f"  Diameter:         {best.diameter:.4f} m")
        print(f"  Nose Cone Length: {best.nose_cone_length:.4f} m")
        print(f"  Body Length:      {best.body_length:.4f} m")
        print(f"  Total Length:     {best.nose_cone_length + best.body_length:.4f} m")
        print(f"  L/D Ratio:        {(best.nose_cone_length + best.body_length) / best.diameter:.2f}")
        print(f"  Nose/Body Ratio:  {best.nose_cone_length / best.body_length:.3f}")
        print(f"\n  Achieved Apogee:  {best.apogee:.2f} m")
        print(f"  Target Apogee:    {self.config.target_apogee:.2f} m")
        print(f"  Error:            {best.error:.2f} m ({100*best.error/self.config.target_apogee:.2f}%)")
        print(f"  Converged:        {'YES' if best.success else 'NO'}")
        print(f"  Iterations:       {best.iterations}")
        print(f"  Time:             {best.computation_time:.2f} s")
        
        print(f"\nALL METHODS COMPARISON:")
        print(f"{'Method':<20} {'Apogee (m)':>12} {'Error (m)':>12} {'Time (s)':>10} {'Converged':>10}")
        print(f"{'-'*80}")
        for r in results:
            conv = "YES" if r.success else "NO"
            print(f"{r.method:<20} {r.apogee:>12.2f} {r.error:>12.2f} {r.computation_time:>10.2f} {conv:>10}")
        
        print(f"{'='*80}\n")
    
    def export_results(self, filename: str = "optimization_results.json"):
        """Export results to JSON file"""
        import json
        
        if not self.all_results:
            print("No results to export")
            return
        
        data = {
            'config': {
                'target_apogee': self.config.target_apogee,
                'tolerance': self.config.tolerance,
                'bounds': {
                    'diameter': [self.config.diameter_min, self.config.diameter_max],
                    'nose_length': [self.config.nose_length_min, self.config.nose_length_max],
                    'body_length': [self.config.body_length_min, self.config.body_length_max]
                }
            },
            'results': [
                {
                    'method': r.method,
                    'diameter': r.diameter,
                    'nose_cone_length': r.nose_cone_length,
                    'body_length': r.body_length,
                    'total_length': r.nose_cone_length + r.body_length,
                    'apogee': r.apogee,
                    'error': r.error,
                    'error_percent': 100 * r.error / self.config.target_apogee,
                    'converged': r.success,
                    'iterations': r.iterations,
                    'computation_time': r.computation_time
                }
                for r in self.all_results
            ],
            'best_result': {
                'method': self.best_result.method,
                'diameter': self.best_result.diameter,
                'nose_cone_length': self.best_result.nose_cone_length,
                'body_length': self.best_result.body_length,
                'total_length': self.best_result.nose_cone_length + self.best_result.body_length,
                'apogee': self.best_result.apogee,
                'error': self.best_result.error,
                'converged': self.best_result.success
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Results exported to {filename}")
