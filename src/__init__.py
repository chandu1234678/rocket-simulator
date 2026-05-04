"""
ISRO-Level Rocket Flight Simulator
Stage 1: Pure Python Implementation
"""

__version__ = "1.0.0"
__author__ = "GITAM Rocketry Team"

# Public API exports for easy imports
from src.optimization.hybrid_optimizer import HybridOptimizer
from src.optimization.fast_optimizer import FastOptimizer
from src.optimization.feasibility_checker import FeasibilityChecker
from src.optimization.optimization_result import OptimizationResult
from src.core.rocket_config_validator import ValidatedRocketConfig
from src.models.constants import SUPERSONIC_MACH_LIMIT

__all__ = [
    # Version info
    '__version__',
    '__author__',
    
    # Optimizers
    'HybridOptimizer',
    'FastOptimizer',
    
    # Validation
    'FeasibilityChecker',
    'ValidatedRocketConfig',
    
    # Results
    'OptimizationResult',
    
    # Constants
    'SUPERSONIC_MACH_LIMIT',
]
