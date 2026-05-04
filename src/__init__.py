"""
ISRO-Level Rocket Flight Simulator
Stage 1: Pure Python Implementation
"""

__version__ = "1.0.0"
__author__ = "GITAM Rocketry Team"

# Public API exports for easy imports
# Note: These imports may fail if dependencies are not installed
# Use try-except for graceful degradation

__all__ = [
    # Version info
    '__version__',
    '__author__',
]

# Optional imports - only available if modules are properly installed
try:
    from .optimization.hybrid_optimizer import HybridOptimizer
    from .optimization.fast_optimizer import FastOptimizer
    from .optimization.feasibility_checker import FeasibilityChecker
    __all__.extend(['HybridOptimizer', 'FastOptimizer', 'FeasibilityChecker'])
except ImportError:
    pass

try:
    from .optimization.optimization_result import OptimizationResult
    __all__.append('OptimizationResult')
except ImportError:
    pass

try:
    from .core.rocket_config_validator import ValidatedRocketConfig
    __all__.append('ValidatedRocketConfig')
except ImportError:
    pass

try:
    from .models.constants import SUPERSONIC_MACH_LIMIT
    __all__.append('SUPERSONIC_MACH_LIMIT')
except ImportError:
    pass

