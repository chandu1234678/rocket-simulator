# Rocket Design Optimization Guide

## Overview

This guide explains how to use the parallel optimization system to design a rocket that achieves a specific target apogee altitude.

## What Gets Optimized?

The optimizer adjusts three key design parameters:

1. **Rocket Diameter** (m) - Cross-sectional diameter of the rocket body
2. **Nose Cone Length** (m) - Length of the nose cone section
3. **Body Length** (m) - Length of the main body section

The optimizer runs multiple algorithms **simultaneously in parallel** to find the best combination that achieves your target apogee within tolerance.

## Quick Start

### 1. Basic Optimization

```python
from src.core.config import load_config
from src.optimization import RocketDesignOptimizer

# Load base configuration
config = load_config("data/config.json")

# Create optimizer
optimizer = RocketDesignOptimizer(config)

# Optimize for 300m apogee with ±5m tolerance
result = optimizer.optimize(
    target_apogee=300.0,
    tolerance=5.0
)

# Print results
print(f"Optimized Diameter: {result['diameter']:.4f} m")
print(f"Optimized Nose Length: {result['nose_cone_length']:.4f} m")
print(f"Optimized Body Length: {result['body_length']:.4f} m")
print(f"Achieved Apogee: {result['apogee']:.2f} m")
print(f"Error: {result['error']:.2f} m")
```

### 2. Run Example Script

```bash
python examples/optimize_rocket_design.py
```

This will:
- Load the base rocket configuration
- Run 4 optimization algorithms in parallel
- Display real-time progress
- Show the best design found
- Export results to `optimization_results.json`

## Configuration Options

### Target and Tolerance

```python
result = optimizer.optimize(
    target_apogee=500.0,  # Target altitude in meters
    tolerance=10.0         # Acceptable error in meters
)
```

### Design Variable Bounds

Specify the search range for each parameter:

```python
result = optimizer.optimize(
    target_apogee=300.0,
    tolerance=5.0,
    diameter_range=(0.10, 0.30),      # 10-30 cm diameter
    nose_length_range=(0.20, 0.80),   # 20-80 cm nose
    body_length_range=(0.80, 2.50)    # 80-250 cm body
)
```

### Optimization Methods

Choose which algorithms to run:

```python
result = optimizer.optimize(
    target_apogee=300.0,
    tolerance=5.0,
    methods=['differential_evolution', 'nelder-mead', 'powell', 'slsqp']
)
```

**Available Methods:**
- `differential_evolution` - Global optimizer, best for finding global optimum
- `nelder-mead` - Fast local optimizer, derivative-free
- `powell` - High-precision local optimizer
- `slsqp` - Sequential Least Squares, handles constraints well

### Iteration Control

```python
result = optimizer.optimize(
    target_apogee=300.0,
    tolerance=5.0,
    max_iterations=150  # More iterations = better convergence (but slower)
)
```

## Understanding Results

### Result Dictionary

```python
{
    'success': True,              # Did it converge within tolerance?
    'diameter': 0.2156,           # Optimized diameter (m)
    'nose_cone_length': 0.4523,   # Optimized nose length (m)
    'body_length': 1.6234,        # Optimized body length (m)
    'total_length': 2.0757,       # Total rocket length (m)
    'apogee': 298.45,             # Achieved apogee (m)
    'target_apogee': 300.0,       # Target apogee (m)
    'error': 1.55,                # Absolute error (m)
    'error_percent': 0.52,        # Percentage error
    'method': 'differential_evolution',  # Best method
    'iterations': 87,             # Number of iterations
    'computation_time': 45.2      # Time taken (seconds)
}
```

### Console Output

During optimization, you'll see real-time progress:

```
================================================================================
PARALLEL ROCKET OPTIMIZATION
================================================================================
Target Apogee: 300.00 m
Tolerance: 5.00 m
Methods: differential_evolution, nelder-mead, powell, slsqp
Parallel Workers: 7
Initial Guess: D=0.200m, Nose=0.500m, Body=1.500m
================================================================================

✓ CONVERGED | nelder-mead          | Apogee:  298.45m | Error:   1.55m | Time: 12.34s | Iters:   87
✓ CONVERGED | powell              | Apogee:  299.12m | Error:   0.88m | Time: 15.67s | Iters:  102
✓ CONVERGED | differential_evolution | Apogee:  300.23m | Error:   0.23m | Time: 45.23s | Iters:  234
✗ NOT CONVERGED | slsqp           | Apogee:  295.67m | Error:   4.33m | Time: 18.90s | Iters:  150
```

### Exported JSON

Results are saved to `optimization_results.json`:

```json
{
  "config": {
    "target_apogee": 300.0,
    "tolerance": 5.0,
    "bounds": {
      "diameter": [0.1, 0.3],
      "nose_length": [0.2, 0.8],
      "body_length": [0.8, 2.5]
    }
  },
  "best_result": {
    "method": "differential_evolution",
    "diameter": 0.2156,
    "nose_cone_length": 0.4523,
    "body_length": 1.6234,
    "total_length": 2.0757,
    "apogee": 300.23,
    "error": 0.23,
    "converged": true
  },
  "results": [ ... ]
}
```

## Advanced Usage

### Using Configuration File

Update `data/config.json`:

```json
{
  "optimization": {
    "enabled": true,
    "target_apogee": 400.0,
    "tolerance": 10.0,
    "max_iterations": 150,
    "diameter_range": [0.15, 0.35],
    "nose_length_range": [0.30, 1.00],
    "body_length_range": [1.00, 3.00],
    "methods": ["differential_evolution", "nelder-mead"],
    "constraints": {
      "length_to_diameter_ratio_min": 8.0,
      "length_to_diameter_ratio_max": 15.0,
      "nose_to_body_ratio_min": 0.2,
      "nose_to_body_ratio_max": 0.4
    }
  }
}
```

Then run:

```python
from src.core.config import load_config
from src.optimization import RocketDesignOptimizer

config = load_config("data/config.json")
optimizer = RocketDesignOptimizer(config)
result = optimizer.optimize_from_config(config.__dict__)
```

### Custom Constraints

The optimizer enforces physical constraints:

1. **Length-to-Diameter Ratio**: Total length / diameter (typically 5-20)
2. **Nose-to-Body Ratio**: Nose length / body length (typically 0.1-0.5)

These ensure the design is physically reasonable and aerodynamically stable.

## Performance Tips

### Faster Optimization

- Use fewer methods: `methods=['nelder-mead']`
- Reduce iterations: `max_iterations=50`
- Narrow search bounds
- Increase tolerance

### Better Convergence

- Use more methods (especially `differential_evolution`)
- Increase iterations: `max_iterations=200`
- Widen search bounds
- Decrease tolerance
- Use tighter constraints

### Parallel Performance

The optimizer automatically uses all available CPU cores minus one. On an 8-core system, it will use 7 workers to run 7 optimization methods simultaneously.

## Troubleshooting

### "Not Converged" Results

**Problem**: Optimization doesn't reach target within tolerance

**Solutions**:
1. Increase `max_iterations`
2. Widen the search bounds
3. Increase `tolerance`
4. Check if target is physically achievable with given propulsion

### Slow Performance

**Problem**: Optimization takes too long

**Solutions**:
1. Reduce `max_iterations`
2. Use fewer methods
3. Narrow search bounds
4. Increase simulation timestep (less accurate)

### Invalid Designs

**Problem**: Optimizer produces unrealistic designs

**Solutions**:
1. Tighten constraint parameters
2. Narrow search bounds
3. Check that bounds are physically reasonable

### All Methods Fail

**Problem**: No method converges

**Solutions**:
1. Check that target apogee is achievable
2. Verify propulsion parameters are correct
3. Widen search bounds significantly
4. Increase tolerance temporarily to see what's achievable

## Example Scenarios

### Scenario 1: Competition Rocket (300m target)

```python
result = optimizer.optimize(
    target_apogee=300.0,
    tolerance=5.0,
    diameter_range=(0.10, 0.25),
    nose_length_range=(0.20, 0.60),
    body_length_range=(0.80, 2.00),
    max_iterations=100
)
```

### Scenario 2: High-Altitude Rocket (1000m target)

```python
result = optimizer.optimize(
    target_apogee=1000.0,
    tolerance=20.0,
    diameter_range=(0.15, 0.40),
    nose_length_range=(0.40, 1.20),
    body_length_range=(1.50, 4.00),
    max_iterations=150
)
```

### Scenario 3: Micro Rocket (100m target)

```python
result = optimizer.optimize(
    target_apogee=100.0,
    tolerance=3.0,
    diameter_range=(0.05, 0.15),
    nose_length_range=(0.10, 0.30),
    body_length_range=(0.30, 1.00),
    max_iterations=80
)
```

## Testing

Run optimization tests:

```bash
# All optimization tests
pytest tests/test_optimization.py -v

# Specific test
pytest tests/test_optimization.py::test_simple_optimization -v
```

## Next Steps

1. Run the example: `python examples/optimize_rocket_design.py`
2. Modify target apogee and bounds
3. Experiment with different methods
4. Use optimized design in your simulations
5. Validate with physical testing

## References

- See `src/optimization/README.md` for technical details
- See `examples/optimize_rocket_design.py` for complete example
- See `tests/test_optimization.py` for usage examples
