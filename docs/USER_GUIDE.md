# How to Use - Rocket Trajectory Optimization System

## For Aerospace Students (No Coding Experience Required!)

This guide will help you use the rocket optimization system without needing to know programming.

## Quick Start (3 Steps)

### Step 1: Install Python
1. Download Python from https://www.python.org/downloads/
2. Install Python (make sure to check "Add Python to PATH")
3. Open Command Prompt (Windows) or Terminal (Mac/Linux)

### Step 2: Install Requirements
```bash
cd path/to/rocket-trajectory-optimizer
pip install -r requirements.txt
```

### Step 3: Run Your Analysis
```bash
python run_complete_analysis.py
```

That's it! The program will analyze your rocket and give you results.

---

## Available Programs

### 1. Complete Analysis (Recommended for Beginners)
**File:** `run_complete_analysis.py`

**What it does:**
- Checks if your rocket is safe
- Optimizes the design
- Gives you final specifications

**How to use:**
1. Open `run_complete_analysis.py` in a text editor
2. Find the section that says "ENTER YOUR ROCKET PARAMETERS HERE"
3. Change the numbers to match your rocket
4. Save the file
5. Run: `python run_complete_analysis.py`

**Example parameters:**
```python
ROCKET_CONFIG = {
    'thrust': 80.0,              # Your motor's thrust in Newtons
    'burn_time': 1.8,            # How long the motor burns (seconds)
    'specific_impulse': 180,     # Motor efficiency (from motor specs)
    'mass_initial': 2.76,        # Total weight with propellant (kg)
    'mass_dry': 2.0,             # Weight without propellant (kg)
}

TARGET_APOGEE = 5000.0           # How high you want to go (meters)
```

---

### 2. Feasibility Check Only
**File:** `run_feasibility_check.py`

**What it does:**
- Quick check (2 seconds)
- Tells you if your rocket is safe
- Warns if it will go supersonic (dangerous!)
- Suggests fixes if there are problems

**When to use:**
- Before building your rocket
- To test different motor options
- To check if a design is safe

**How to run:**
```bash
python run_feasibility_check.py
```

---

### 3. Fast Optimization
**File:** `run_fast_optimization.py`

**What it does:**
- Very fast (0.02 seconds)
- Gives you initial design estimates
- 80% accuracy (good enough for early design)

**When to use:**
- Quick design iterations
- Exploring different options
- Initial estimates

**How to run:**
```bash
python run_fast_optimization.py
```

---

### 4. Accurate Optimization (Recommended)
**File:** `run_accurate_optimization.py`

**What it does:**
- Fast (0.5 seconds)
- 90% accuracy
- Best balance of speed and accuracy

**When to use:**
- Final design before building
- Competition rockets
- When you need reliable results

**How to run:**
```bash
python run_accurate_optimization.py
```

---

### 5. Production Optimization
**File:** `run_production_optimization.py`

**What it does:**
- Highest accuracy (95%)
- Takes 1.6 seconds
- Tests 3 different flight regimes

**When to use:**
- Final competition designs
- Research projects
- When accuracy is critical

**How to run:**
```bash
python run_production_optimization.py
```

**Note:** On Windows, you may need to add this at the bottom of the file:
```python
if __name__ == '__main__':
    main()
```

---

### 6. Trajectory Simulation
**File:** `run_trajectory_simulation.py`

**What it does:**
- Simulates your rocket's flight
- Shows altitude, velocity, and Mach number
- Gives you complete trajectory data

**When to use:**
- After optimization
- To see detailed flight path
- To verify your design

**How to run:**
```bash
python run_trajectory_simulation.py
```

---

## Understanding the Parameters

### Rocket Parameters

**Thrust** (Newtons)
- Force produced by your motor
- Found in motor specifications
- Example: Estes C6-5 = 5N, Cesaroni Pro38 = 200N

**Burn Time** (seconds)
- How long the motor burns
- Found in motor specifications
- Example: 1.8 seconds

**Specific Impulse** (seconds)
- Motor efficiency
- Found in motor specifications
- Higher = more efficient
- Example: 180 seconds

**Initial Mass** (kg)
- Total weight with propellant
- Weigh your rocket with motor
- Example: 2.76 kg

**Dry Mass** (kg)
- Weight without propellant
- Weigh your rocket without motor, then add motor casing weight
- Example: 2.0 kg

**Diameter** (meters)
- Body tube diameter
- Measure your rocket
- Example: 0.1 m = 10 cm

**Nose Cone Length** (meters)
- Length of nose cone
- Measure your rocket
- Example: 0.3 m = 30 cm

**Body Length** (meters)
- Length of body tube
- Measure your rocket
- Example: 1.0 m = 100 cm

**Drag Coefficient**
- How aerodynamic your rocket is
- Typical values: 0.3-0.5
- Lower = more aerodynamic
- Example: 0.35

### Target Parameters

**Target Apogee** (meters)
- How high you want your rocket to go
- Example: 5000 m = 5 km

**Tolerance** (meters)
- Acceptable error
- Example: 50 m means anywhere from 4950m to 5050m is OK

---

## Understanding the Results

### Feasibility Check Results

**FEASIBLE**
- Your rocket is safe and can reach the target
- You can proceed with building

**NOT FEASIBLE - Supersonic**
- Your rocket will go faster than Mach 1.2
- This is DANGEROUS!
- You must reduce thrust, burn time, or increase mass

**NOT FEASIBLE - Insufficient Altitude**
- Your rocket cannot reach the target
- You must increase thrust, burn time, or reduce mass

### Optimization Results

**Diameter**
- Optimized body tube diameter
- Use this size when building

**Drag Coefficient (Cd)**
- Expected drag for your rocket
- Lower is better (more aerodynamic)

**Achieved Apogee**
- Predicted maximum altitude
- Should be close to your target

**Maximum Mach**
- Fastest speed (relative to sound)
- Must be below 1.2 for safety

---

## Common Issues and Solutions

### Issue: "Module not found"
**Solution:** Install requirements
```bash
pip install -r requirements.txt
```

### Issue: "Rocket goes supersonic"
**Solutions:**
1. Reduce thrust (use smaller motor)
2. Reduce burn time (use shorter burn motor)
3. Increase mass (add weight)
4. Increase diameter (more drag)

### Issue: "Cannot reach target altitude"
**Solutions:**
1. Increase thrust (use bigger motor)
2. Increase burn time (use longer burn motor)
3. Reduce mass (make rocket lighter)
4. Reduce diameter (less drag)

### Issue: "Optimization takes too long"
**Solution:** Use fast optimization instead:
```bash
python run_fast_optimization.py
```

### Issue: "Results don't match real flight"
**Possible reasons:**
1. Wind (not modeled)
2. Motor performance variation
3. Build quality differences
4. Measurement errors

**Solution:** Add safety margin (aim 10% higher than needed)

---

## Tips for Best Results

### 1. Accurate Measurements
- Weigh your rocket carefully
- Measure dimensions precisely
- Use motor specifications from manufacturer

### 2. Safety First
- Always check feasibility before building
- Never exceed Mach 1.2
- Add safety margins to your design

### 3. Iterative Design
- Start with fast optimization
- Refine with accurate optimization
- Verify with trajectory simulation

### 4. Documentation
- Save your results
- Record actual flight data
- Compare predictions vs reality

---

## Example Workflow

### For a School Project:

1. **Design Phase**
   ```bash
   python run_feasibility_check.py
   ```
   - Check if design is safe
   - Adjust parameters if needed

2. **Optimization Phase**
   ```bash
   python run_accurate_optimization.py
   ```
   - Get optimized dimensions
   - Record specifications

3. **Verification Phase**
   ```bash
   python run_trajectory_simulation.py
   ```
   - Verify flight path
   - Check all parameters

4. **Build and Test**
   - Build rocket with optimized specs
   - Test fly
   - Compare results

### For a Competition:

1. **Initial Design**
   ```bash
   python run_fast_optimization.py
   ```

2. **Refinement**
   ```bash
   python run_accurate_optimization.py
   ```

3. **Final Verification**
   ```bash
   python run_production_optimization.py
   ```

4. **Pre-Flight Check**
   ```bash
   python run_trajectory_simulation.py
   ```

---

## Getting Help

### If you get stuck:

1. Read the error message carefully
2. Check your parameter values
3. Make sure all files are in the correct location
4. Verify Python and packages are installed

### Common Error Messages:

**"FileNotFoundError"**
- You're in the wrong directory
- Solution: `cd` to the project folder

**"ImportError"**
- Missing packages
- Solution: `pip install -r requirements.txt`

**"ValueError"**
- Invalid parameter value
- Solution: Check your numbers (no negative values!)

---

## Quick Reference Card

```
PROGRAM                          SPEED    ACCURACY    USE FOR
================================================================
run_complete_analysis.py         Fast     Good        Beginners
run_feasibility_check.py         2s       100%        Safety check
run_fast_optimization.py         0.02s    80%         Quick estimates
run_accurate_optimization.py     0.5s     90%         Most projects
run_production_optimization.py   1.6s     95%         Competitions
run_trajectory_simulation.py     Fast     High        Verification
```

---

## Need More Help?

- Check `README.md` for technical details
- See `PROJECT_STRUCTURE.md` for code organization
- Read `SYSTEM_OVERVIEW.md` for complete reference

---

**Remember:** Always prioritize safety! If the system says your rocket will go supersonic, DO NOT build it without modifications.

Happy rocketeering!
