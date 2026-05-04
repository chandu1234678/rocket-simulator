"""
Hybrid Optimizer - Vispootanam Level
Combines fast analytical (initial guess) + accurate numerical (refinement)
Target: <3 seconds with 90%+ accuracy
"""

import numpy as np
from typing import Dict, Tuple
from scipy.optimize import minimize
import time

from src.optimization.vispootanam_parallel_optimizer import VispootanamParallelOptimizer, VispootanamConfig
from src.models.constants import SUPERSONIC_MACH_LIMIT


class HybridOptimizer:
    """
    Hybrid Fast + Accurate Optimizer
    
    Strategy:
    1. Phase 1: Fast analytical guess (0.001s)
    2. Phase 2: Local refinement with accurate simulation (2-3s)
    
    Total time: <3s
    Accuracy: 90%+
    """
    
    def __init__(self, base_config: Dict, target_apogee: float, tolerance: float = 10.0, max_iterations: int = 20, nose_ratio: float = 3.0, body_ratio: float = 10.0):
        self.base_config = base_config
        self.target_apogee = target_apogee
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.nose_ratio = nose_ratio  # Nose length = nose_ratio × diameter
        self.body_ratio = body_ratio  # Body length = body_ratio × diameter
        self.eval_count = 0
        self.iteration_count = 0
        self.best_error = float('inf')
        self.show_iterations = True  # Control iteration display
        
    def fast_initial_guess(self) -> Tuple[float, float]:
        """
        Fast analytical initial guess
        
        Uses physics-based heuristics:
        - Larger diameter = more drag = lower apogee
        - Higher Cd = more drag = lower apogee
        
        Returns: (diameter_guess, cd_guess)
        """
        # Extract parameters
        thrust = self.base_config['thrust']
        burn_time = self.base_config['burn_time']
        isp = self.base_config['specific_impulse']
        m0 = self.base_config['mass_initial']
        m_dry = self.base_config['mass_dry']
        
        g0 = 9.81
        
        # Estimate burnout velocity using Tsiolkovsky equation (correct physics)
        v_e = isp * g0  # Exhaust velocity
        mass_ratio = m0 / m_dry
        v_burnout_ideal = v_e * np.log(mass_ratio) - g0 * burn_time
        
        # Estimate burnout altitude (rough approximation)
        h_burnout = 0.5 * v_burnout_ideal * burn_time  # Average velocity * time
        
        # Estimate ideal apogee (no drag) - includes burnout altitude
        h_ideal = h_burnout + v_burnout_ideal**2 / (2 * g0)
        
        # Ratio of target to ideal
        ratio = self.target_apogee / h_ideal if h_ideal > 0 else 0.5
        
        # Improved heuristic for better initial guess
        if ratio < 0.3:
            # Need lots of drag
            diameter_guess = 0.20  # Larger diameter
            cd_guess = 0.60        # Higher Cd
        elif ratio < 0.5:
            # Need moderate drag
            diameter_guess = 0.15
            cd_guess = 0.50
        elif ratio < 0.7:
            # Need some drag
            diameter_guess = 0.12
            cd_guess = 0.40
        else:
            # Need minimal drag
            diameter_guess = 0.10
            cd_guess = 0.30
        
        return diameter_guess, cd_guess
    
    def accurate_refine(self, diameter_init: float, cd_init: float) -> Dict:
        """
        Fast refinement using analytical simulation (NOT slow numerical)
        
        Uses gradient-based optimization with fast physics for speed
        """
        from src.optimization.fast_optimizer import FastOptimizer
        
        # Create fast optimizer for quick simulation
        fast_opt = FastOptimizer(self.base_config, self.target_apogee, self.tolerance)
        fast_opt.show_iterations = False  # We'll handle display ourselves
        
        # Track iterations properly
        iteration_data = []
        
        # Objective function
        def objective(x):
            diameter, cd = x
            
            try:
                apogee, max_mach = fast_opt.fast_simulate(diameter, cd)
                
                # Supersonic penalty
                if max_mach >= SUPERSONIC_MACH_LIMIT:
                    penalty = 1e6 + (max_mach - SUPERSONIC_MACH_LIMIT) * 1e5
                    return penalty
                
                error = abs(apogee - self.target_apogee)
                self.eval_count += 1
                
                # Store data for callback
                iteration_data.append({
                    'diameter': diameter,
                    'cd': cd,
                    'apogee': apogee,
                    'error': error,
                    'mach': max_mach
                })
                
                return error
            except Exception as e:
                return 1e6
        
        # Callback function - called after each optimization iteration
        def callback(xk):
            if iteration_data:
                self.iteration_count += 1
                data = iteration_data[-1]  # Get most recent evaluation
                
                if self.show_iterations:
                    status = "✓" if data['error'] < self.best_error else " "
                    print(f"  {status} Iteration {self.iteration_count:2d}: "
                          f"D={data['diameter']:.4f}m, Cd={data['cd']:.4f}, "
                          f"Apogee={data['apogee']:7.1f}m, Error={data['error']:6.1f}m, Mach={data['mach']:.3f}")
                    
                    if data['error'] < self.best_error:
                        self.best_error = data['error']
        
        # Initial guess
        x0 = np.array([diameter_init, cd_init])
        
        # Bounds
        bounds = [(0.05, 0.5), (0.15, 0.85)]
        
        # Show optimization header
        if self.show_iterations:
            print("\n  Refining with fast analytical simulation...")
            print("  " + "-" * 80)
        
        # Optimize using L-BFGS-B with proper callback
        result = minimize(
            objective,
            x0,
            method='L-BFGS-B',
            bounds=bounds,
            callback=callback,
            options={
                'maxiter': self.max_iterations,
                'ftol': 1e-6,
                'gtol': 1e-5,
                'disp': False
            }
        )
        
        if self.show_iterations:
            print("  " + "-" * 80)
            print(f"  Optimization completed in {self.iteration_count} iterations\n")
        
        # Extract results
        diameter_opt, cd_opt = result.x
        
        # Final simulation
        apogee_final, max_mach_final = fast_opt.fast_simulate(diameter_opt, cd_opt)
        error_final = abs(apogee_final - self.target_apogee)
        
        # Estimate nose and body length based on diameter using user-specified ratios
        # These are NOT optimized - just geometric estimates based on typical rocket proportions
        nose_length = self.nose_ratio * diameter_opt
        body_length = self.body_ratio * diameter_opt
        
        return {
            'diameter': diameter_opt,
            'nose_length': nose_length,
            'body_length': body_length,
            'cd': cd_opt,
            'apogee': apogee_final,
            'max_mach': max_mach_final,
            'error': error_final,
            'converged': result.success and error_final <= self.tolerance,
            'iterations': self.eval_count,
            'optimization_steps': self.iteration_count  # Actual optimization iterations
        }
    
    def optimize_hybrid(self) -> Dict:
        """
        Hybrid optimization: fast guess + accurate refinement
        
        Returns: optimization results
        """
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"HYBRID Vispootanam-LEVEL OPTIMIZATION")
        print(f"{'='*80}")
        print(f"Target Apogee: {self.target_apogee:.2f} m")
        print(f"Tolerance: {self.tolerance:.2f} m")
        print(f"Strategy: Fast guess + Accurate refinement")
        print(f"{'='*80}\n")
        
        # Phase 1: Fast initial guess
        print("PHASE 1: Fast Initial Guess")
        print("-" * 80)
        phase1_start = time.time()
        
        diameter_guess, cd_guess = self.fast_initial_guess()
        
        phase1_time = time.time() - phase1_start
        print(f"  Diameter guess:  {diameter_guess:.4f} m")
        print(f"  Cd guess:        {cd_guess:.4f}")
        print(f"  Time:            {phase1_time:.3f} s")
        
        # Phase 2: Accurate refinement
        print(f"\nPHASE 2: Accurate Local Refinement")
        print("-" * 80)
        phase2_start = time.time()
        
        result = self.accurate_refine(diameter_guess, cd_guess)
        
        phase2_time = time.time() - phase2_start
        total_time = time.time() - start_time
        
        # CRITICAL: Supersonic prevention check
        if result['max_mach'] >= 1.2:
            print(f"\n{'='*80}")
            print(f"⚠️  SUPERSONIC VIOLATION DETECTED")
            print(f"{'='*80}")
            print(f"  Max Mach: {result['max_mach']:.3f} (limit: 1.2)")
            print(f"  This design is UNSAFE and must be rejected!")
            print(f"{'='*80}\n")
            result['converged'] = False
            result['supersonic_violation'] = True
        else:
            result['supersonic_violation'] = False
        
        # Print results
        print(f"\n{'='*80}")
        print(f" HYBRID OPTIMIZATION COMPLETE")
        print(f"{'='*80}")
        print(f"\n RESULTS:")
        print(f"  Diameter:         {result['diameter']:.4f} m")
        print(f"  Nose Cone Length (estimated): {result['nose_length']:.4f} m  # {self.nose_ratio}×D")
        print(f"  Body Length (estimated):      {result['body_length']:.4f} m  # {self.body_ratio}×D")
        print(f"  Total Length:     {result['nose_length'] + result['body_length']:.4f} m")
        print(f"  Cd Optimized:     {result['cd']:.4f}")
        print(f"  Achieved Apogee:  {result['apogee']:.2f} m")
        print(f"  Target Apogee:    {self.target_apogee:.2f} m")
        print(f"  Error:            {result['error']:.2f} m ({100*result['error']/self.target_apogee:.2f}%)")
        print(f"  Max Mach:         {result['max_mach']:.3f}")
        print(f"  Converged:        {'YES' if result['converged'] else 'NO'}")
        print(f"  Optimization Steps: {result['optimization_steps']}")
        print(f"\n⏱  TIMING:")
        print(f"  Phase 1 (Fast):   {phase1_time:.3f} s")
        print(f"  Phase 2 (Refine): {phase2_time:.3f} s")
        print(f"  Total Time:       {total_time:.3f} s ")
        print(f"\n{'='*80}")
        
        result['time'] = total_time
        result['phase1_time'] = phase1_time
        result['phase2_time'] = phase2_time
        
        return result


# Test
if __name__ == "__main__":
    # Base configuration
    base_config = {
        'thrust': 80.0,
        'burn_time': 1.8,
        'specific_impulse': 180,
        'mass_initial': 2.76,
        'mass_dry': 2.0
    }
    
    # Test different targets
    test_targets = [300, 500, 1000]
    
    print("="*80)
    print("HYBRID OPTIMIZER TEST")
    print("="*80)
    
    for target in test_targets:
        optimizer = HybridOptimizer(base_config, target_apogee=target, tolerance=10.0)
        result = optimizer.optimize_hybrid()
        
        # Check performance
        accuracy = 100 - (result['error'] / target * 100)
        speed_ok = result['time'] < 3.0
        accuracy_ok = accuracy >= 90
        
        print(f"\n Target {target}m:")
        print(f"   Accuracy: {accuracy:.1f}% {'' if accuracy_ok else ''}")
        print(f"   Speed: {result['time']:.3f}s {'' if speed_ok else ''}")
        print(f"   Status: {' PASS' if (speed_ok and accuracy_ok) else ' NEEDS WORK'}")
    
    print("\n" + "="*80)
