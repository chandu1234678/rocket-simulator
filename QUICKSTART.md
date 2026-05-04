# Quick Start Guide - Rocket Simulator

Get started with the Vispootanam Rocket Simulator in 5 minutes!

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Install

```bash
# Clone the repository
git clone https://github.com/chandu1234678/rocket-simulator.git
cd rocket-simulator

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Verify installation
python verify_installation.py
```

### Optional: Install Numba for Performance

```bash
pip install numba
```

This provides 10-100x speedup for physics calculations.

---

## 🎯 Your First Simulation

### Option 1: Complete Analysis (Recommended)

Run the complete workflow with all features:

```bash
python run/run_complete_analysis.py
```

This will:
1. Check feasibility (can your rocket reach the target?)
2. Optimize the design (find best diameter and drag coefficient)
3. Show detailed results

**Output:**
```
Target: 500m
Optimized Design:
  Diameter: 0.1234m
  Nose Length: 0.3702m
  Body Length: 1.234m
  Drag Coefficient: 0.366
  
Achieved: 498.5m (99.7% accuracy)
Max Mach: 0.85 (subsonic ✓)
```

### Option 2: Fast Optimization

For quick estimates (0.02 seconds):

```bash
python run/run_fast_optimization.py
```

### Option 3: Accurate Optimization

For production designs (0.5 seconds):

```bash
python run/run_accurate_optimization.py
```

---

## 🔧 Customize Your Rocket

Edit the configuration in any run script:

```python
# Load default configuration
from data.default_rocket_config import get_config

ROCKET_CONFIG = get_config('default')

# Override specific parameters
ROCKET_CONFIG['thrust'] = 100.0        # Increase thrust
ROCKET_CONFIG['mass_initial'] = 3.0    # Heavier rocket

TARGET_APOGEE = 1000.0  # Target altitude in meters
```

### Available Presets

```python
get_config('default')        # Standard model rocket
get_config('high_altitude')  # More propellant, higher thrust
get_config('low_altitude')   # Safer, lower performance
get_config('competition')    # Optimized for accuracy
```

---

## 📊 Understanding Results

### Key Metrics

**Diameter**: Body tube diameter (meters)
- Larger = more drag = lower altitude
- Typical: 0.05m to 0.5m

**Drag Coefficient (Cd)**: Aerodynamic efficiency
- Lower = less drag = higher altitude
- Typical: 0.3 to 0.8

**Max Mach**: Maximum speed relative to sound
- Must stay below 1.2 (supersonic limit)
- Typical: 0.5 to 1.1

**Error**: Difference from target altitude
- < 10%: Excellent
- < 20%: Good
- > 50%: Failed

### Safety Checks

✅ **Subsonic**: Max Mach < 1.2 (safe)  
❌ **Supersonic**: Max Mach ≥ 1.2 (UNSAFE - rejected)

---

## 🧪 Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_aerodynamics.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 📚 Examples

### Example 1: Design for 500m Altitude

```python
from data.default_rocket_config import get_config
from src.optimization.hybrid_optimizer import HybridOptimizer

# Load configuration
config = get_config('default')

# Create optimizer
optimizer = HybridOptimizer(
    base_config=config,
    target_apogee=500.0,
    tolerance=50.0
)

# Optimize
result = optimizer.optimize_hybrid()

print(f"Diameter: {result['diameter']:.4f}m")
print(f"Apogee: {result['apogee']:.1f}m")
print(f"Error: {result['error']:.1f}m")
```

### Example 2: Check Feasibility

```python
from src.optimization.feasibility_checker import FeasibilityChecker

checker = FeasibilityChecker()

result = checker.check_feasibility(
    thrust=80.0,
    burn_time=1.8,
    specific_impulse=180,
    mass_initial=2.2,
    mass_dry=2.0,
    target_apogee=5000.0
)

if result.can_proceed:
    print("✓ Design is feasible!")
else:
    print(f"✗ Problem: {result.reason}")
    print("Suggestions:")
    for option in result.suggestions['options'].values():
        print(f"  - {option['message']}")
```

### Example 3: Custom Rocket

```python
from data.default_rocket_config import get_config

# Start with default
config = get_config('default')

# Customize for high altitude
config['thrust'] = 150.0           # More thrust
config['burn_time'] = 2.5          # Longer burn
config['specific_impulse'] = 200   # Better propellant
config['mass_initial'] = 3.5       # More propellant
config['mass_dry'] = 2.5           # Heavier structure

# Now use this config with any optimizer
```

---

## 🎓 Learning Path

### Beginner
1. Run `run_complete_analysis.py` with default settings
2. Modify `TARGET_APOGEE` and observe changes
3. Try different presets: `get_config('high_altitude')`

### Intermediate
4. Customize rocket parameters (thrust, mass, ISP)
5. Run `run_feasibility_check.py` to understand limits
6. Compare fast vs accurate optimizers

### Advanced
7. Write custom optimization scripts
8. Modify physics models in `src/models/`
9. Add new optimization algorithms
10. Contribute to the project!

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

```bash
# Make sure you're in the project root
cd rocket-simulator

# Install in editable mode
pip install -e .
```

### "Numba not available" warning

This is normal! The code works without numba, just slower.

To install numba for better performance:
```bash
pip install numba
```

### Tests failing

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Reinstall package
pip install -e . --no-deps

# Run tests
pytest tests/ -v
```

### Import errors in run scripts

Run scripts from the project root:
```bash
# Good
python run/run_complete_analysis.py

# Bad (don't cd into run/)
cd run
python run_complete_analysis.py  # Will fail
```

---

## 📖 Next Steps

- Read [USER_GUIDE.md](docs/USER_GUIDE.md) for detailed usage
- Check [API_REFERENCE.md](docs/API_REFERENCE.md) for API docs
- See [TECHNICAL_SPECIFICATION.md](docs/TECHNICAL_SPECIFICATION.md) for physics
- Review [examples/](examples/) for more code samples

---

## 🤝 Get Help

- **Issues**: https://github.com/chandu1234678/rocket-simulator/issues
- **Discussions**: https://github.com/chandu1234678/rocket-simulator/discussions
- **Email**: bbodapat2@gitam.in

---

## ⚡ Performance Tips

1. **Use Hybrid Optimizer** for best balance (0.5s, 90% accuracy)
2. **Install Numba** for 10-100x speedup
3. **Start with feasibility check** to avoid wasted optimization
4. **Use Fast Optimizer** for initial exploration
5. **Use Parallel Optimizer** only for final production designs

---

**Happy Rocketing! 🚀**
