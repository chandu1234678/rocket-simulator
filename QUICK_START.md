# 🚀 QUICK START GUIDE
## Get Running in 5 Minutes

---

## Step 1: Environment Setup (2 minutes)

```bash
# Navigate to project directory
cd rocket-simulator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

**Verify installation:**
```bash
python -c "import numpy, scipy, matplotlib; print('✅ All dependencies installed!')"
```

---

## Step 2: Run Your First Simulation (1 minute)

Once Phase 1 is complete, you'll run:

```bash
python examples/basic_simulation.py
```

**Expected output:**
```
🚀 Rocket Simulation Starting...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Configuration: Kushinagar-001
Launch Site: 26.74°N, 83.887°E, 83.5m ASL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Simulating... ████████████████████ 100%

✅ Simulation Complete!

📊 Results:
  Apogee:        161.48 m
  Max Velocity:   91.95 m/s
  Max Mach:        0.263
  Burn Time:       1.80 s
  Flight Time:    18.45 s

📈 Plots saved to: output/trajectory_plots.png
```

---

## Step 3: Explore Examples (2 minutes)

### Example 1: Basic Simulation
```python
from src.core.simulation import SimulationEngine
from src.core.config import load_config

config = load_config('data/config.json')
sim = SimulationEngine(config)
trajectory = sim.run()

print(f"Apogee: {trajectory.max_altitude:.2f} m")
```

### Example 2: Parameter Sweep
```python
# Sweep thrust values
thrusts = [500, 600, 700, 800]
apogees = []

for thrust in thrusts:
    config.propulsion.thrust_max = thrust
    sim = SimulationEngine(config)
    trajectory = sim.run()
    apogees.append(trajectory.max_altitude)

# Plot results
import matplotlib.pyplot as plt
plt.plot(thrusts, apogees)
plt.xlabel('Thrust (N)')
plt.ylabel('Apogee (m)')
plt.show()
```

### Example 3: Optimization (Phase 3)
```python
from src.optimization import optimize_for_apogee

# Find thrust for 200m apogee
optimal_thrust = optimize_for_apogee(
    target_apogee=200.0,
    config=config
)

print(f"Optimal thrust: {optimal_thrust:.2f} N")
```

---

## Step 4: Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/test_atmosphere.py -v
```

---

## Step 5: Modify Configuration

Edit `data/config.json` to change rocket parameters:

```json
{
  "rocket": {
    "mass_initial": 11.01,    // Change this
    "diameter": 0.216,         // Or this
    ...
  },
  "propulsion": {
    "thrust_max": 747.1,       // Or this
    ...
  }
}
```

Then re-run simulation to see effects!

---

## 🎯 Next Steps

1. **Read the Architecture**: [ROCKET_SIMULATION_ARCHITECTURE.md](ROCKET_SIMULATION_ARCHITECTURE.md)
2. **Follow the Roadmap**: [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)
3. **Track Progress**: [PHASE_CHECKLIST.md](PHASE_CHECKLIST.md)
4. **Start Coding**: Begin with Phase 1, Day 1 tasks

---

## 🆘 Troubleshooting

### Import Error: No module named 'src'
```bash
# Make sure you installed in development mode
pip install -e .
```

### NumPy/SciPy Installation Failed
```bash
# On Linux, install system dependencies first
sudo apt-get install python3-dev

# On Mac with M1/M2
pip install --upgrade pip
pip install numpy scipy --no-cache-dir
```

### Tests Not Found
```bash
# Make sure pytest is installed
pip install pytest pytest-cov
```

---

## 📚 Useful Commands

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
pylint src/

# Generate documentation
cd docs && make html

# Clean build artifacts
rm -rf build/ dist/ *.egg-info
```

---

## 🎉 You're Ready!

Start with **Phase 1, Day 1** from the roadmap:
- Create `src/core/state.py`
- Create `src/core/config.py`
- Write your first tests

**Happy coding! 🚀**
