# Project Structure

## Directory Layout

```
rocket-trajectory-optimizer/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── simulation.py          # Main simulation engine
│   │   └── state.py               # State management
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── aerodynamics.py        # Basic aerodynamics
│   │   ├── advanced_aerodynamics.py  # 3-regime aerodynamics
│   │   ├── atmosphere.py          # Atmospheric model
│   │   ├── dynamics.py            # Equations of motion
│   │   ├── ideal_trajectory.py    # Zero-drag analyzer
│   │   └── propulsion.py          # Thrust model
│   │
│   ├── solvers/
│   │   ├── __init__.py
│   │   ├── rk4.py                 # RK4 solver
│   │   └── semi_implicit.py       # Semi-implicit solver
│   │
│   └── optimization/
│       ├── __init__.py
│       ├── feasibility_checker.py      # Pre-flight checks
│       ├── fast_optimizer.py           # Fast analytical optimizer
│       ├── hybrid_optimizer.py         # Hybrid optimizer
│       ├── vispootanam_parallel_optimizer.py  # Parallel regime optimizer
│       ├── parallel_optimizer.py       # Basic parallel optimizer
│       ├── rocket_optimizer.py         # Basic optimizer
│       └── flight_regime_analyzer.py   # Flight regime analysis
│
├── tests/
│   ├── __init__.py
│   ├── test_aerodynamics.py
│   ├── test_atmosphere.py
│   ├── test_flight_regime.py
│   ├── test_ideal_trajectory.py
│   ├── test_optimization.py
│   ├── test_feasibility_integration.py
│   ├── test_Vispootanam_complete_system.py
│   ├── test_parallel_speed.py
│   ├── test_speed_final.py
│   ├── calibrate_fast_optimizer.py
│   └── DEMO_Vispootanam_SYSTEM.py
│
├── examples/
│   ├── basic_simulation.py
│   ├── optimize_rocket_design.py
│   └── optimize_with_supersonic_check.py
│
├── data/
│   └── config.json
│
├── rocket/                         # Reference data and documents
│
├── requirements.txt
├── setup.py
├── README.md
├── PROJECT_STRUCTURE.md
└── FINAL_Vispootanam_SYSTEM_STATUS.md

```

## Core Components

### Models
- **aerodynamics.py**: Basic drag coefficient calculations
- **advanced_aerodynamics.py**: 3-regime system (D1/D2/D3)
- **atmosphere.py**: Standard atmosphere model
- **dynamics.py**: Rocket equations of motion
- **ideal_trajectory.py**: Zero-drag trajectory for feasibility
- **propulsion.py**: Thrust and mass flow calculations

### Solvers
- **rk4.py**: 4th-order Runge-Kutta integrator
- **semi_implicit.py**: Semi-implicit Euler (faster, stable)

### Optimization
- **feasibility_checker.py**: Pre-flight feasibility and supersonic prevention
- **fast_optimizer.py**: Ultra-fast analytical optimizer (0.016s)
- **hybrid_optimizer.py**: Fast guess + accurate refinement (0.5s)
- **vispootanam_parallel_optimizer.py**: Parallel regime optimization (1.6s)
- **parallel_optimizer.py**: Basic parallel optimization
- **rocket_optimizer.py**: Single-objective optimizer

### Core
- **simulation.py**: Main simulation orchestration
- **config.py**: Configuration data structures
- **state.py**: State vector management

## Usage Patterns

### Quick Feasibility Check
```python
from src.optimization.feasibility_checker import FeasibilityChecker

checker = FeasibilityChecker()
result = checker.check_feasibility(thrust, burn_time, isp, m0, m_dry, target)
```

### Fast Optimization
```python
from src.optimization.fast_optimizer import FastOptimizer

optimizer = FastOptimizer(base_config, target_apogee=5000.0)
result = optimizer.optimize_fast()
```

### Hybrid Optimization (Recommended)
```python
from src.optimization.hybrid_optimizer import HybridOptimizer

optimizer = HybridOptimizer(base_config, target_apogee=5000.0)
result = optimizer.optimize_hybrid()
```

### Parallel Regime Optimization (Highest Accuracy)
```python
from src.optimization.vispootanam_parallel_optimizer import VispootanamParallelOptimizer, VispootanamConfig

config = VispootanamConfig(target_apogee=5000.0, tolerance=50.0)
optimizer = VispootanamParallelOptimizer(base_config, config)
results = optimizer.optimize_all_regimes()
```

## Testing

Run all tests:
```bash
python -m pytest tests/
```

Run specific test:
```bash
python tests/test_Vispootanam_complete_system.py
```

## Performance Benchmarks

| Component | Time | Accuracy | Use Case |
|-----------|------|----------|----------|
| Fast Optimizer | 0.016s | 80% | Initial guess |
| Hybrid Optimizer | 0.5s | 90% | Balanced |
| Parallel Optimizer | 1.6s | 95% | Production |
| Feasibility Check | 2s | 100% | Pre-flight |
