"""
Numba utilities with graceful fallback
Provides optional JIT compilation for performance
"""

import functools
import warnings

# Try to import numba
try:
    from numba import jit as numba_jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    warnings.warn(
        "Numba not available. Code will run without JIT compilation. "
        "Install numba for better performance: pip install numba",
        ImportWarning
    )


def jit(*args, **kwargs):
    """
    JIT decorator with graceful fallback
    
    If numba is available, uses numba.jit for compilation.
    If not available, returns the function unchanged.
    
    Usage:
        @jit(nopython=True, cache=True)
        def my_function(x):
            return x * 2
    
    Args:
        *args: Positional arguments for numba.jit
        **kwargs: Keyword arguments for numba.jit
    
    Returns:
        Decorated function (compiled if numba available, unchanged otherwise)
    """
    def decorator(func):
        if NUMBA_AVAILABLE:
            # Use numba JIT compilation
            return numba_jit(*args, **kwargs)(func)
        else:
            # No compilation, return function as-is
            @functools.wraps(func)
            def wrapper(*func_args, **func_kwargs):
                return func(*func_args, **func_kwargs)
            return wrapper
    
    # Handle both @jit and @jit(...) syntax
    if len(args) == 1 and callable(args[0]) and not kwargs:
        # Called as @jit without parentheses
        func = args[0]
        if NUMBA_AVAILABLE:
            return numba_jit(func)
        else:
            return func
    else:
        # Called as @jit(...) with arguments
        return decorator


def is_numba_available() -> bool:
    """
    Check if numba is available
    
    Returns:
        True if numba is installed and working, False otherwise
    """
    return NUMBA_AVAILABLE


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("NUMBA AVAILABILITY CHECK")
    print("="*60)
    
    if NUMBA_AVAILABLE:
        print("✓ Numba is AVAILABLE")
        print("  JIT compilation will be used for performance")
    else:
        print("✗ Numba is NOT AVAILABLE")
        print("  Code will run without JIT compilation")
        print("  Install with: pip install numba")
    
    print("="*60)
    
    # Test the decorator
    @jit(nopython=True, cache=True)
    def test_function(x):
        return x * 2
    
    result = test_function(5)
    print(f"\nTest function result: {result}")
    print(f"Expected: 10")
    print(f"Status: {'✓ PASS' if result == 10 else '✗ FAIL'}")
