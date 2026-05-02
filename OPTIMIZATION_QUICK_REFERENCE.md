# Rocket Optimization - Quick Reference

## One-Line Usage

```python
from src.core.config import load_config
from src.optimization import RocketDesignOptimizer

result = RocketDesignOptimizer(load_config("data/config.json")).optimize(target_apogee=300.0, tolerance=5.0)
```

## Run Example

```bash
python examples/optimize_rocket_design.py
```

## Basic API

```python
from src.optimization import RocketDesignOptimizer

optimizer = RocketDesignOptimizer(config)

result = optimizer.optimize(
    target_apogee=300.0,           # Target altitude (m)
    tolerance=5.0,                  # Acceptable error (m)
    diameter_range=(0.1, 0.3),      # Min/max diameter (m)
    nose_length_range=(0.2, 0.8),   # Min/max nose length (m)
    body_length_range=(0.8, 2.5),   # Min/max body length (m)
    max_iterations=100,             # Max iterations per method
    methods=['differential_evolution', 'nelder-mead', 'powell', 'slsqp']
)
```

## Result Access

```python
result['diameter']           # Optimized diameter (m)
result['nose_cone_length']   # Optimized nose length (m)
result['body_length']        # Optimized body length (m)
result['apogee']             # Achieved apogee (m)
result['error']              # Error from target (m)
result['success']            # Converged? (bool)
result['method']             # Best method name
result['iterations']         # Number of iterations
result['computation_time']   # Time taken (s)
```

## Optimization Methods

| Method | Type | Speed | Accuracy | Best For |
|--------|------|-------|----------|----------|
| `differential_evolution` | Global | Slow | High | Finding global optimum |
| `nelder-mead` | Local | Fast | Medium | Quick results |
| `powell` | Local | Medium | High | High precision |
| `slsqp` | Local | Medium | Medium | Constrained problems |

## Common Scenarios

### Competition Rocket (300m)
```python
result = optimizer.optimize(target_apogee=300.0, tolerance=5.0,
    diameter_range=(0.10, 0.25), nose_length_range=(0.20, 0.60),
    body_length_range=(0.80, 2.00))
```

### High Altitude (1000m)
```python
result = optimizer.optimize(target_apogee=1000.0, tolerance=20.0,
    diameter_range=(0.15, 0.40), nose_length_range=(0.40, 1.20),
    body_length_range=(1.50, 4.00))
```

### Micro Rocket (100m)
```python
result = optimizer.optimize(target_apogee=100.0, tolerance=3.0,
    diameter_range=(0.05, 0.15), nose_length_range=(0.10, 0.30),
    body_length_range=(0.30, 1.00))
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Not converging | Increase `max_iterations` or `tolerance` |
| Too slow | Use fewer methods: `methods=['nelder-mead']` |
| Invalid designs | Tighten bounds or check constraints |
| All methods fail | Check if target is achievable |

## Configuration File

Edit `data/config.json`:

```json
{
  "optimization": {
    "enabled": true,
    "target_apogee": 300.0,
    "tolerance": 5.0,
    "max_iterations": 100,
    "diameter_range": [0.10, 0.30],
    "nose_length_range": [0.20, 0.80],
    "body_length_range": [0.80, 2.50],
    "methods": ["differential_evolution", "nelder-mead"]
  }
}
```

Then:
```python
result = optimizer.optimize_from_config(config.__dict__)
```

## Testing

```bash
# All tests
pytest tests/test_optimization.py -v

# Specific test
pytest tests/test_optimization.py::test_simple_optimization -v
```

## Output Files

- `optimization_results.json` - Complete results in JSON format

## Key Constraints

- **L/D Ratio**: 5-20 (length/diameter)
- **Nose/Body Ratio**: 0.1-0.5 (nose_length/body_length)

## Performance

- **Parallel execution**: Uses all CPU cores
- **Typical time**: 30-60 seconds for 4 methods
- **Caching**: Simulation results cached automatically

## Documentation

- **User Guide**: `OPTIMIZATION_GUIDE.md`
- **Technical Docs**: `src/optimization/README.md`
- **Implementation**: `OPTIMIZATION_IMPLEMENTATION_SUMMARY.md`

## Import Paths

```python
from src.optimization import (
    RocketDesignOptimizer,      # Main interface
    ParallelRocketOptimizer,    # Low-level optimizer
    OptimizationConfig,         # Configuration
    OptimizationResult          # Result dataclass
)
```

## Example Output

```
✓ CONVERGED | differential_evolution | Apogee: 300.23m | Error: 0.23m | Time: 45.23s
✓ CONVERGED | nelder-mead          | Apogee: 298.45m | Error: 1.55m | Time: 12.34s
✓ CONVERGED | powell              | Apogee: 299.12m | Error: 0.88m | Time: 15.67s

BEST RESULT:
  Diameter:    0.2156 m
  Nose Length: 0.4523 m
  Body Length: 1.6234 m
  Apogee:      300.23 m (target: 300.00 m)
  Error:       0.23 m (0.08%)
```
