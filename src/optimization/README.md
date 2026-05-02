# Rocket Design Optimization Module

## Overview

This module provides parallel optimization capabilities for rocket design parameters. It optimizes **diameter**, **nose cone length**, and **body length** to achieve a target apogee altitude within a specified tolerance.

## Key Features

- **Parallel Optimization**: Multiple optimization algorithms run simultaneously
- **Multiple Methods**: Differential Evolution, Nelder-Mead, Powell, SLSQP
- **Constraint Handling**: Length-to-diameter ratios, nose-to-body ratios
- **Convergence Tracking**: Real-time progress monitoring
- **Result Export**: JSON export of all optimization results

## Architecture

### Components

1. **OptimizationConfig**: Configuration dataclass for optimization parameters
2. **ParallelRocketOptimizer**: Core parallel optimization engine
3. **RocketDesignOptimizer**: High-level interface integrating with simulation
4. **OptimizationResult**: Result dataclass with all optimization metrics

### Optimization Methods

| Method | Type | Best For |
|--------|------|----------|
| Differential Evolution | Global | Finding global optimum, robust |
| Nelder-Mead | Local | Fast convergence, derivative-free |
| Powell | Local | High precision, derivative-free |
| SLSQP | Local | Constrained optimization |

## Usage

### Basic Example

```python
from src.core.config import load_config
from src.optimization import RocketDesignOptimizer

# Load base configuration
config = load_config("data/config.json")

# Create optimizer
optimizer = RocketDesignOptimizer(config)

# Run optimization
result = optimizer.optimize(
    target_apogee=300.0,      # Target altitude (m)
    tolerance=5.0,             # Acceptable error (m)
    diameter_range=(0.1, 0.3), # Diameter bounds (m)
    nose_length_range=(0.2, 0.8),
    body_length_range=(0.8, 2.5),
    max_iterations=100
)

print(f"Optimized Diameter: {result['diameter']:.4f} m")
print(f"Optimized Nose Length: {result['nose_cone_length']:.4f} m")
print(f"Optimized Body Length: {result['body_length']:.4f} m")
print(f"Achieved Apogee: {result['apogee']:.2f} m")
```

### Advanced Configuration

```python
from src.optimization import OptimizationConfig, ParallelRocketOptimizer

# Custom configuration
config = OptimizationConfig(
    target_apogee=500.0,
    tolerance=10.0,
    diameter_min=0.15,
    diameter_max=0.35,
    nose_length_min=0.3,
    nose_length_max=1.0,
    body_length_min=1.0,
    body_length_max=3.0,
    max_iterations=150,
    population_size=20,
    n_parallel_workers=4,
    length_to_diameter_ratio_min=8.0,
    length_to_diameter_ratio_max=15.0,
    nose_to_body_ratio_min=0.2,
    nose_to_body_ratio_max=0.4,
    methods=['differential_evolution', 'nelder-mead']
)

# Create optimizer with custom simulation function
optimizer = ParallelRocketOptimizer(simulation_function, config)

# Run optimization
results = optimizer.optimize_parallel()

# Access all results
for result in results:
    print(f"{result.method}: Apogee={result.apogee:.2f}m, Error={result.error:.2f}m")
```

## Configuration Parameters

### Design Variable Bounds

- `diameter_min`, `diameter_max`: Rocket diameter range (m)
- `nose_length_min`, `nose_length_max`: Nose cone length range (m)
- `body_length_min`, `body_length_max`: Body length range (m)

### Optimization Settings

- `target_apogee`: Target apogee altitude (m)
- `tolerance`: Acceptable error from target (m)
- `max_iterations`: Maximum iterations per method
- `population_size`: Population size for evolutionary algorithms
- `n_parallel_workers`: Number of parallel processes (default: CPU count - 1)

### Constraints

- `length_to_diameter_ratio_min/max`: Total length / diameter ratio
- `nose_to_body_ratio_min/max`: Nose length / body length ratio

## Output

### Result Dictionary

```python
{
    'success': bool,              # Converged within tolerance
    'diameter': float,            # Optimized diameter (m)
    'nose_cone_length': float,    # Optimized nose length (m)
    'body_length': float,         # Optimized body length (m)
    'total_length': float,        # Total rocket length (m)
    'apogee': float,              # Achieved apogee (m)
    'target_apogee': float,       # Target apogee (m)
    'error': float,               # Absolute error (m)
    'error_percent': float,       # Percentage error
    'method': str,                # Best optimization method
    'iterations': int,            # Number of iterations
    'computation_time': float,    # Time taken (s)
    'all_results': List[OptimizationResult]  # All method results
}
```

### JSON Export

Results are automatically exported to `optimization_results.json`:

```json
{
  "config": {
    "target_apogee": 300.0,
    "tolerance": 5.0,
    "bounds": { ... }
  },
  "results": [
    {
      "method": "differential_evolution",
      "diameter": 0.2156,
      "nose_cone_length": 0.4523,
      "body_length": 1.6234,
      "apogee": 298.45,
      "error": 1.55,
      "converged": true
    }
  ],
  "best_result": { ... }
}
```

## Examples

### Example 1: Target Specific Apogee

```bash
python examples/optimize_rocket_design.py
```

This runs a complete optimization to achieve 300m apogee.

### Example 2: From Configuration File

```python
from src.core.config import load_config
from src.optimization import RocketDesignOptimizer

config = load_config("data/config.json")
optimizer = RocketDesignOptimizer(config)

# Use optimization parameters from config file
result = optimizer.optimize_from_config(config.__dict__)
```

## Performance

- **Parallel Execution**: All methods run simultaneously
- **Caching**: Simulation results are cached to avoid redundant calculations
- **Typical Runtime**: 30-120 seconds depending on complexity and iterations

## Constraints and Validation

The optimizer enforces physical constraints:

1. **Length-to-Diameter Ratio**: Typically 5-20 for stable flight
2. **Nose-to-Body Ratio**: Typically 0.1-0.5 for aerodynamic efficiency
3. **Bounds Checking**: All variables stay within specified ranges

## Troubleshooting

### Optimization Not Converging

- Increase `max_iterations`
- Widen the search bounds
- Reduce `tolerance`
- Try different optimization methods

### Slow Performance

- Reduce `max_iterations`
- Reduce `population_size`
- Use fewer optimization methods
- Increase simulation timestep (less accurate)

### Invalid Designs

- Check constraint parameters
- Verify bounds are physically reasonable
- Ensure target apogee is achievable with given propulsion

## Testing

Run optimization tests:

```bash
pytest tests/test_optimization.py -v
```

## References

- Differential Evolution: Storn & Price (1997)
- Nelder-Mead: Nelder & Mead (1965)
- Powell's Method: Powell (1964)
- SLSQP: Kraft (1988)
