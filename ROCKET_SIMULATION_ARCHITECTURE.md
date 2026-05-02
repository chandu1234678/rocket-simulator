# ISRO-LEVEL ROCKET FLIGHT SIMULATION SYSTEM
## Comprehensive Architecture & Implementation Guide

**Project**: Real-Time Rocket Trajectory Simulation  
**Target**: ISRO/IN-SPACe Competition Standards  
**Location**: Kushinagar Launch Site (26.74°N, 83.887°E, 83.5m ASL)  
**Date**: May 2026

---

## EXECUTIVE SUMMARY

This document defines a professional-grade rocket flight simulator capable of predicting trajectory, optimizing design parameters, and meeting ISRO competition requirements. The system implements physics-accurate modeling with Mach-dependent aerodynamics, variable mass dynamics, and atmospheric effects.

### Key Capabilities
- **1-DOF vertical flight simulation** with extensibility to 2D/3D
- **Mach-dependent drag modeling** (subsonic → transonic → supersonic)
- **Real-time trajectory prediction** with apogee optimization
- **Design parameter optimization** (thrust, burn time, propellant mass)
- **Competition-ready outputs** matching OpenRocket validation data

---

## 1. PROBLEM DEFINITION

### 1.1 Objective
Design a modular rocket flight simulator that:
1. Predicts maximum altitude (apogee) with <5% error
2. Handles transonic flow regime accurately
3. Optimizes design parameters toward target apogee
4. Supports multi-stage rockets (future extension)
5. Validates against OpenRocket simulation data

### 1.2 Reference Mission Parameters
Based on `rckt_kushinagar.csv` analysis:

| Parameter | Value | Unit |
|-----------|-------|------|
| **Initial Mass** | 11,010 | g |
| **Propellant Mass** | 2,935.3 | g |
| **Dry Mass** | 8,074.7 | g |
| **Burn Time** | ~1.8 | s |
| **Max Thrust** | 747.1 | N |
| **Diameter** | 21.6 | cm |
| **Reference Area** | 366.435 | cm² |
| **Launch Site Altitude** | 83.5 | m ASL |
| **Target Apogee** | ~162 | m |
| **Max Velocity** | ~92 | m/s |
| **Max Mach Number** | ~0.27 | - |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  (Input Validation, Configuration Loading, Results Display)  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  SIMULATION ORCHESTRATOR                     │
│         (Main Loop, Event Handling, Data Logging)            │
└─┬──────────┬──────────┬──────────┬──────────┬──────────┬───┘
  │          │          │          │          │          │
  ▼          ▼          ▼          ▼          ▼          ▼
┌────┐   ┌────┐   ┌────┐   ┌────┐   ┌────┐   ┌────┐
│Atmo│   │Prop│   │Aero│   │Dyn │   │Solv│   │Opt │
│sph.│   │uls.│   │dyn.│   │amic│   │er  │   │imiz│
└────┘   └────┘   └────┘   └────┘   └────┘   └────┘
  │          │          │          │          │          │
  └──────────┴──────────┴──────────┴──────────┴──────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                    │
│        (Trajectory Logging, Performance Metrics, Export)     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Module Breakdown

#### **Module 1: Configuration & Input**
- **Purpose**: Load and validate user inputs
- **Inputs**: 
  - Rocket geometry (diameter, length, nose cone)
  - Mass properties (initial, dry, propellant)
  - Propulsion (thrust curve, Isp, burn time)
  - Launch conditions (altitude, temperature, wind)
- **Validation**:
  - `mass_initial > mass_dry > 0`
  - `burn_time > 0`
  - `diameter > 0`
  - Physical constraint checks

#### **Module 2: Atmosphere Model**
- **Purpose**: Compute air properties vs altitude
- **Inputs**: Altitude (h)
- **Outputs**: 
  - Air density (ρ)
  - Temperature (T)
  - Pressure (P)
  - Speed of sound (a)
- **Models**:
  - **Simple**: Exponential decay `ρ(h) = ρ₀ * exp(-h/H)` where H ≈ 8500m
  - **Advanced**: ISA (International Standard Atmosphere) tables

```
ρ(h) = ρ₀ * exp(-h / 8500)
T(h) = T₀ - 0.0065 * h  (up to 11km)
a(h) = √(γ * R * T(h))
```

#### **Module 3: Propulsion Model**
- **Purpose**: Calculate thrust and mass flow
- **Inputs**: Time (t), burn time (t_burn)
- **Outputs**: 
  - Thrust (T)
  - Mass flow rate (ṁ)
  - Remaining propellant mass
- **Equations**:

```
T(t) = {
  T_max           if t < t_burn
  0               if t ≥ t_burn
}

ṁ = T / (Isp * g₀)

m(t) = m₀ - ∫ṁ dt
```

**Thrust Curve Options**:
1. **Constant**: T = T_max
2. **Linear ramp**: T = T_max * (t / t_ramp)
3. **Custom profile**: Interpolated from data

#### **Module 4: Aerodynamics Model**
- **Purpose**: Calculate drag force with Mach dependency
- **Inputs**: 
  - Velocity (v)
  - Air density (ρ)
  - Mach number (M)
- **Outputs**: 
  - Drag force (D)
  - Drag coefficient (Cd)

**Critical: Transonic Drag Spike**

```
Drag Force:
D = ½ * ρ * v² * Cd(M) * A

Mach Number:
M = v / a(h)

Drag Coefficient Model:
Cd(M) = {
  Cd₀                           if M < 0.3  (incompressible)
  Cd₀ + k₁ * M²                 if 0.3 ≤ M < 0.8  (subsonic)
  Cd₀ + k₂ * exp(-((M-1)²/σ²))  if 0.8 ≤ M < 1.2  (transonic)
  Cd₀ + k₃ / M                  if M ≥ 1.2  (supersonic)
}
```

**Typical Values**:
- Cd₀ (base) ≈ 0.35-0.45
- Transonic spike: Cd_max ≈ 0.8-1.2 at M ≈ 1.0
- k₂ ≈ 0.4-0.6 (spike magnitude)
- σ ≈ 0.15 (spike width)

**Component Breakdown** (from CSV data):
- Friction drag: ~0.219
- Pressure drag: ~0.026
- Base drag: ~0.121
- Total: ~0.366

#### **Module 5: Dynamics & Kinematics**
- **Purpose**: Compute equations of motion
- **Governing Equation** (1-DOF vertical):

```
m * dv/dt = T - D - m*g

where:
  T = Thrust
  D = Drag
  m = time-varying mass
  g = gravitational acceleration
```

**State Variables**:
```
State = {
  t:  time (s)
  h:  altitude (m)
  v:  velocity (m/s)
  m:  mass (kg)
}
```

**Derivatives**:
```
dh/dt = v
dv/dt = (T - D - m*g) / m
dm/dt = -ṁ  (during burn)
```

#### **Module 6: Numerical Solver**
- **Purpose**: Integrate equations of motion
- **Method**: **Runge-Kutta 4th Order (RK4)**

**Why RK4?**
- ✅ 4th order accuracy: O(Δt⁴)
- ✅ Stable for rocket dynamics
- ✅ Industry standard
- ❌ NOT Euler (1st order, unstable)
- ❌ NOT Crank-Nicolson (for PDEs, overkill)

**RK4 Algorithm**:
```
k₁ = f(t, y)
k₂ = f(t + Δt/2, y + Δt*k₁/2)
k₃ = f(t + Δt/2, y + Δt*k₂/2)
k₄ = f(t + Δt, y + Δt*k₃)

y(t + Δt) = y(t) + (Δt/6) * (k₁ + 2k₂ + 2k₃ + k₄)
```

**Timestep Selection**:
- Δt = 0.01s (typical, from CSV)
- Adaptive: reduce if |dv/dt| > threshold

#### **Module 7: Optimization Engine**
- **Purpose**: Find design parameters for target apogee
- **Objective Function**:

```
minimize: |h_simulated - h_target|
```

**Design Variables**:
- Thrust (T)
- Burn time (t_burn)
- Propellant mass (m_prop)

**Methods**:
1. **Binary Search** (simple, 1D)
2. **Gradient-Free Optimization** (Nelder-Mead, Powell)
3. **Genetic Algorithm** (multi-objective)

**Constraints**:
- T_min ≤ T ≤ T_max
- t_burn > 0
- m_prop ≤ m_initial - m_dry

---

## 3. FLOW REGIME CLASSIFICATION

### 3.1 Regime Definitions

| Regime | Mach Range | Cd Behavior | Critical Effects |
|--------|------------|-------------|------------------|
| **Incompressible** | M < 0.3 | Constant | Negligible compressibility |
| **Subsonic** | 0.3 ≤ M < 0.8 | Slight increase | Compressibility effects |
| **Transonic** ⚠️ | 0.8 ≤ M < 1.2 | **DRAG SPIKE** | Shock waves, flow separation |
| **Supersonic** | M ≥ 1.2 | Decreases | Oblique shocks, wave drag |

### 3.2 Why Transonic Matters
- **Most rockets pass through M ≈ 1.0**
- **Drag can increase 2-3x** during transonic regime
- **Ignoring this = 20-30% apogee error**

---

## 4. SIMULATION LOOP (CORE ENGINE)

### 4.1 Main Loop Pseudocode

```python
# Initialize
state = State(t=0, h=0, v=0, m=m_initial)
trajectory = []

# Main loop
while state.v >= 0 or is_burning:
    # 1. Atmosphere
    rho, T, P, a = atmosphere.get_properties(state.h)
    
    # 2. Mach number
    M = state.v / a
    
    # 3. Aerodynamics
    Cd = aerodynamics.get_drag_coefficient(M)
    D = 0.5 * rho * state.v**2 * Cd * A_ref
    
    # 4. Propulsion
    if state.t < t_burn:
        T = propulsion.get_thrust(state.t)
        m_dot = propulsion.get_mass_flow()
    else:
        T = 0
        m_dot = 0
    
    # 5. Dynamics
    a_total = (T - D - state.m * g) / state.m
    
    # 6. Integrate (RK4)
    state = solver.step(state, dt)
    
    # 7. Log data
    trajectory.append(state.copy())
    
    # 8. Check termination
    if state.v == 0 and T == 0:
        break  # Apogee reached

# Post-process
apogee = max(state.h for state in trajectory)
```

### 4.2 Termination Conditions
1. **Burnout**: t ≥ t_burn
2. **Apogee**: v = 0 (velocity becomes zero)
3. **Ground impact**: h ≤ 0 (if simulating descent)

### 4.3 Event Detection
- **IGNITION**: t = 0
- **LIFTOFF**: h > 0 (first time)
- **LAUNCHROD**: h > rod_length
- **BURNOUT**: t = t_burn
- **APOGEE**: v = 0

---

## 5. OUTPUTS & VALIDATION

### 5.1 Primary Outputs
1. **Maximum Altitude** (apogee) [m]
2. **Maximum Velocity** [m/s]
3. **Maximum Mach Number** [-]
4. **Time to Apogee** [s]
5. **Burnout Altitude** [m]
6. **Burnout Velocity** [m/s]

### 5.2 Trajectory Data (Time Series)
- Time (s)
- Altitude (m)
- Velocity (m/s)
- Acceleration (m/s²)
- Mach number (-)
- Drag force (N)
- Thrust (N)
- Mass (kg)

### 5.3 Validation Against OpenRocket
Compare against `rckt_kushinagar.csv`:

| Metric | OpenRocket | Target Accuracy |
|--------|------------|-----------------|
| Apogee | 161.478 m | ±5% (153-169 m) |
| Max Velocity | 91.946 m/s | ±5% |
| Max Mach | 0.263 | ±10% |
| Burnout Time | ~1.8 s | ±0.1 s |

---

## 6. STABILITY & NUMERICAL SAFETY

### 6.1 Divergence Detection
Monitor for:
- **NaN values** (division by zero)
- **Negative mass** (propellant overburn)
- **Unrealistic Mach** (M > 3 for model rocket)
- **Velocity explosion** (dv/dt > 1000 m/s²)

### 6.2 Handling Instabilities
```python
if is_diverging(state):
    # Option 1: Reduce timestep
    dt = dt / 2
    retry_step()
    
    # Option 2: Clamp values
    state.v = max(0, min(state.v, v_max))
    
    # Option 3: Abort with error
    raise SimulationError("Divergence detected")
```

### 6.3 Timestep Adaptation
```python
# Adaptive timestep
if abs(dv_dt) > threshold:
    dt_new = dt * 0.5
else:
    dt_new = min(dt * 1.2, dt_max)
```

---

## 7. EXTENSIONS (ISRO-GRADE)

### 7.1 Level 2: 2D Trajectory
- Add pitch angle (θ)
- Wind model (horizontal velocity)
- Lateral drift calculation

```
dx/dt = v * sin(θ) + v_wind
dh/dt = v * cos(θ)
```

### 7.2 Level 3: Multi-Stage Rockets
- Stage separation events
- Mass discontinuities
- Inter-stage coast phases

### 7.3 Level 4: Advanced Physics
- **CFD-based Cd lookup tables**
- **Real atmosphere** (ISA standard)
- **6-DOF dynamics** (rotation, stability)
- **Fin flutter analysis**
- **Parachute deployment**

---

## 8. IMPLEMENTATION ROADMAP

### Phase 1: Core Simulator (Week 1-2)
- [ ] Implement State class
- [ ] Atmosphere model (exponential)
- [ ] Propulsion model (constant thrust)
- [ ] Aerodynamics (constant Cd)
- [ ] RK4 solver
- [ ] Main simulation loop
- [ ] Basic validation (no drag case)

### Phase 2: Mach-Dependent Aerodynamics (Week 3)
- [ ] Implement Cd(M) piecewise function
- [ ] Transonic drag spike model
- [ ] Validate against OpenRocket data
- [ ] Tune Cd parameters

### Phase 3: Optimization (Week 4)
- [ ] Binary search for single parameter
- [ ] Multi-parameter optimization (Nelder-Mead)
- [ ] Constraint handling
- [ ] Convergence criteria

### Phase 4: Polish & Documentation (Week 5)
- [ ] GUI/CLI interface
- [ ] Data export (CSV, plots)
- [ ] User manual
- [ ] Competition report

---

## 9. TECHNOLOGY STACK

### 9.1 Recommended Languages
1. **Python** (rapid prototyping, scientific libraries)
   - NumPy (arrays, math)
   - SciPy (optimization, integration)
   - Matplotlib (plotting)
   - Pandas (data handling)

2. **Java** (competition requirement, OOP structure)
   - Apache Commons Math (numerical methods)
   - JFreeChart (plotting)

3. **MATLAB** (academic, built-in solvers)

### 9.2 Project Structure (Java Example)
```
rocket-simulator/
├── src/
│   ├── main/
│   │   ├── config/
│   │   │   └── SimulationConfig.java
│   │   ├── models/
│   │   │   ├── Atmosphere.java
│   │   │   ├── Propulsion.java
│   │   │   ├── Aerodynamics.java
│   │   │   └── Dynamics.java
│   │   ├── solvers/
│   │   │   ├── ODESolver.java
│   │   │   └── RK4Solver.java
│   │   ├── optimization/
│   │   │   └── Optimizer.java
│   │   ├── core/
│   │   │   ├── State.java
│   │   │   ├── SimulationEngine.java
│   │   │   └── DataLogger.java
│   │   └── Main.java
│   └── test/
│       └── ValidationTests.java
├── data/
│   ├── rckt_kushinagar.csv
│   └── validation_results.csv
├── docs/
│   └── ARCHITECTURE.md
└── README.md
```

---

## 10. CRITICAL SUCCESS FACTORS

### 10.1 Must-Have Features
✅ **Transonic drag modeling** (non-negotiable)  
✅ **RK4 integration** (accuracy requirement)  
✅ **Validation against OpenRocket** (<5% error)  
✅ **Modular architecture** (extensibility)  
✅ **Numerical stability** (no crashes)

### 10.2 Common Pitfalls to Avoid
❌ Using Euler integration (unstable)  
❌ Ignoring transonic regime (huge error)  
❌ Constant Cd assumption (unrealistic)  
❌ Mixing physics and solver code (unmaintainable)  
❌ No validation (blind trust in results)

---

## 11. VALIDATION CHECKLIST

### 11.1 Unit Tests
- [ ] Atmosphere: ρ(0) = 1.225 kg/m³
- [ ] Propulsion: ṁ = T / (Isp * g₀)
- [ ] Aerodynamics: D = 0 when v = 0
- [ ] Solver: RK4 matches analytical solution (free fall)

### 11.2 Integration Tests
- [ ] No drag: h_max = v₀² / (2g) + h₀
- [ ] No thrust: ballistic trajectory
- [ ] Constant thrust: linear acceleration phase

### 11.3 System Tests
- [ ] OpenRocket comparison: apogee within 5%
- [ ] Mach profile matches reference
- [ ] Mass conservation: m(t) ≥ m_dry

---

## 12. COMPETITION DELIVERABLES

### 12.1 Required Outputs
1. **Simulation Report** (PDF)
   - Methodology
   - Validation results
   - Apogee prediction
   - Design optimization

2. **Source Code** (GitHub/ZIP)
   - Well-commented
   - README with build instructions
   - Sample input files

3. **Presentation** (PPT)
   - Architecture overview
   - Key results
   - Live demo

### 12.2 Evaluation Criteria
- **Accuracy** (40%): Apogee prediction vs actual flight
- **Physics Fidelity** (30%): Mach effects, variable mass
- **Code Quality** (20%): Modularity, documentation
- **Innovation** (10%): Optimization, advanced features

---

## 13. REFERENCES

### 13.1 Technical References
1. **Rocket Propulsion Elements** - Sutton & Biblarz
2. **Modern Compressible Flow** - Anderson
3. **Numerical Recipes** - Press et al.
4. **OpenRocket Technical Documentation**

### 13.2 Standards
- **ISO 14222**: Space systems - Rocket propulsion
- **AIAA S-080**: Space Systems - Metallic Pressure Vessels
- **MIL-STD-1540**: Test Requirements for Launch, Upper-Stage, and Space Vehicles

### 13.3 Online Resources
- NASA CEA (Chemical Equilibrium with Applications)
- RASAero II (aerodynamic analysis)
- OpenRocket forums

---

## 14. CONTACT & SUPPORT

**Project Team**: GITAM University Rocketry Team  
**Competition**: IN-SPACe / ISRO Challenge 2026  
**Location**: Kushinagar Launch Site  

**Technical Lead**: [Your Name]  
**Email**: [your.email@gitam.edu]  
**GitHub**: [repository-link]

---

## APPENDIX A: EQUATIONS SUMMARY

### A.1 Atmosphere
```
ρ(h) = ρ₀ * exp(-h / H)  where H = 8500 m
T(h) = T₀ - L * h        where L = 0.0065 K/m
P(h) = P₀ * (T(h)/T₀)^(g/(R*L))
a(h) = √(γ * R * T(h))   where γ = 1.4
```

### A.2 Propulsion
```
T(t) = T_max  (constant thrust)
ṁ = T / (Isp * g₀)
m(t) = m₀ - ṁ * t
```

### A.3 Aerodynamics
```
D = ½ * ρ * v² * Cd(M) * A
M = v / a(h)
Cd(M) = Cd₀ + k * exp(-((M-1)²/σ²))  (transonic)
```

### A.4 Dynamics
```
m * dv/dt = T - D - m*g
dh/dt = v
dm/dt = -ṁ
```

### A.5 RK4 Integration
```
k₁ = f(t, y)
k₂ = f(t + Δt/2, y + Δt*k₁/2)
k₃ = f(t + Δt/2, y + Δt*k₂/2)
k₄ = f(t + Δt, y + Δt*k₃)
y_next = y + (Δt/6) * (k₁ + 2k₂ + 2k₃ + k₄)
```

---

## APPENDIX B: SAMPLE INPUT FILE

```json
{
  "rocket": {
    "name": "Kushinagar-001",
    "diameter": 0.216,
    "length": 1.5,
    "mass_initial": 11.01,
    "mass_dry": 8.0747,
    "reference_area": 0.0366435
  },
  "propulsion": {
    "thrust_max": 747.1,
    "burn_time": 1.8,
    "specific_impulse": 180,
    "thrust_curve": "constant"
  },
  "aerodynamics": {
    "cd_base": 0.366,
    "cd_transonic_spike": 0.5,
    "mach_transonic_center": 1.0,
    "mach_transonic_width": 0.15
  },
  "launch": {
    "altitude": 83.5,
    "latitude": 26.74,
    "longitude": 83.887,
    "temperature": 14.457,
    "pressure": 1003.457,
    "wind_speed": 1.807,
    "wind_direction": 90
  },
  "simulation": {
    "timestep": 0.01,
    "max_time": 100,
    "solver": "RK4"
  },
  "optimization": {
    "target_apogee": 200,
    "variables": ["thrust", "burn_time"],
    "method": "nelder-mead"
  }
}
```

---

## APPENDIX C: GLOSSARY

| Term | Definition |
|------|------------|
| **Apogee** | Maximum altitude reached by rocket |
| **Burnout** | Time when propellant is exhausted |
| **Cd** | Drag coefficient (dimensionless) |
| **Isp** | Specific impulse (s) |
| **Mach** | Ratio of velocity to speed of sound |
| **RK4** | Runge-Kutta 4th order integration method |
| **Transonic** | Flow regime near Mach 1 with shock waves |
| **TWR** | Thrust-to-weight ratio |

---

**Document Version**: 1.0  
**Last Updated**: May 1, 2026  
**Status**: Ready for Implementation

---

*This architecture document provides a complete blueprint for building an ISRO-level rocket simulator. Follow the modular design, implement RK4 integration, and validate against OpenRocket data. Success requires attention to transonic aerodynamics and numerical stability.*

**Next Step**: Begin Phase 1 implementation with core simulator modules.
