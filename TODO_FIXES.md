# Rocket Simulator - Complete Fix To-Do List

**Generated:** May 4, 2026  
**Status:** Comprehensive audit of all bugs, physics errors, and code quality issues

---

## 🚨 CRITICAL BUGS (Must Fix Immediately)

### 1. **Thrust Not Time-Gated - ROOT CAUSE OF 404% ERROR**
- **File:** `src/optimization/vispootanam_parallel_optimizer.py` (~line 10075)
- **Issue:** Thrust applied for entire 200s simulation instead of 1.8s burn time
- **Current Code:** `current_thrust = thrust if altitude >= 0 else 0`
- **Fix:** `current_thrust = thrust if (altitude >= 0 and time_elapsed < burn_time) else 0.0`
- **Impact:** Causes 25,226m apogee instead of ~5,000m (404% error)
- **Priority:** P0 - Fix first

### 2. **Fast Initial Guess Uses Wrong Physics (Average Mass)**
- **File:** `src/optimization/hybrid_optimizer.py` (~line 8897)
- **Issue:** Uses F=ma with averaged mass instead of Tsiolkovsky equation
- **Current Code:**
  ```python
  m_avg = (m0 + m_dry) / 2
  v_burnout_ideal = (thrust / m_avg - g0) * burn_time
  ```
- **Fix:**
  ```python
  v_e = isp * g0
  mass_ratio = m0 / m_dry
  v_burnout_ideal = v_e * np.log(mass_ratio) - g0 * burn_time
  ```
- **Impact:** Wrong burnout velocity poisons all downstream heuristics
- **Priority:** P0

### 3. **Ideal Trajectory Velocity Integration Inconsistency**
- **File:** `src/models/ideal_trajectory.py` (lines 7087–7133)
- **Issue:** Burnout velocity from Tsiolkovsky but altitude from Euler loop - inconsistent
- **Fix:** Use Euler loop velocity consistently OR derive h_burnout analytically
- **Impact:** Burnout altitude and velocity don't match
- **Priority:** P0

### 4. **Apogee Estimate Ignores Burnout Altitude**
- **File:** `src/optimization/hybrid_optimizer.py` (~line 8901)
- **Issue:** `h_ideal = v_burnout_ideal**2 / (2 * g0)` ignores 200-400m gained during burn
- **Fix:** `h_apogee = h_burnout + v_burnout**2 / (2 * g0)`
- **Impact:** Underestimates apogee by 200-400m for low-altitude targets
- **Priority:** P0

### 5. **Supersonic Check Uses Sea-Level Sound Speed - SAFETY BUG**
- **Files:** 
  - `src/models/ideal_trajectory.py` (line 7065)
  - `src/optimization/feasibility_checker.py`
- **Issue:** Fixed temperature 287K instead of altitude-dependent
- **Current Code:** `speed_of_sound = np.sqrt(1.4 * 287.0 * 287.0)  # hardcoded`
- **Fix:**
  ```python
  T_at_burnout = 288.15 - 0.0065 * h_burnout  # ISA lapse rate
  speed_of_sound = np.sqrt(1.4 * 287.0 * T_at_burnout)
  max_mach = v_burnout / speed_of_sound
  ```
- **Impact:** Mach 1.176 at sea level is actually Mach 1.248 at altitude - safety check fails
- **Priority:** P0 - Safety critical

### 6. **State Validation Crashes on Normal Landing**
- **File:** `src/core/state.py` (lines 6006–6012)
- **Issue:** `__post_init__` raises ValueError for h<0 before termination check
- **Fix:** Remove altitude check from `__post_init__`, handle in simulation loop
- **Impact:** Unhandled exception crashes simulation at landing
- **Priority:** P0

### 7. **ProcessPoolExecutor Fails on Windows**
- **File:** `src/optimization/vispootanam_parallel_optimizer.py` (line 10333)
- **Issue:** `self._optimize_regime` can't be pickled on Windows spawn-based multiprocessing
- **Fix:** Use module-level function OR ThreadPoolExecutor OR return counts from child
- **Impact:** Parallel optimizer broken on Windows, evaluation counts always 0
- **Priority:** P1

### 8. **Convergence Graphs Use Fake Data**
- **File:** `tests/generate_performance_graphs.py` (lines 11247–11252)
- **Issue:** Hardcoded arrays instead of real measurements
- **Current Code:**
  ```python
  iterations_fast = np.array([1, 2, 3, 4, 5])
  errors_fast = np.array([500, 250, 150, 110, 102])
  ```
- **Fix:** Run actual optimizers and measure real convergence
- **Impact:** Performance claims (95% accuracy, 0.002s) are fabricated
- **Priority:** P1 - Credibility issue

---

## ⚠️ PHYSICS & FORMULA ERRORS

### 9. **Zero-Drag Apogee Formula Ignores Variable Mass**
- **File:** `src/models/ideal_trajectory.py`
- **Issue:** Uses initial mass instead of dry mass for coast phase
- **Current:** `h_ideal = KE_burnout / (m_initial × g)`
- **Fix:**
  ```python
  v_burnout = Isp × g₀ × ln(m_initial / m_dry) - g × t_burn
  h_ideal = v_burnout² / (2 × g) + h_burnout
  ```
- **Impact:** 11,460m claimed vs ~2,690m actual (4× error)
- **Priority:** P0

### 10. **Drag Uses Constant Air Density**
- **File:** `src/models/aerodynamics.py`
- **Issue:** Fixed ρ = 1.225 kg/m³ throughout flight
- **Fix:**
  ```python
  # ISA standard atmosphere
  rho = 1.225 * (1 - 0.0000226 * h)**4.256
  # OR simplified
  rho = 1.225 * np.exp(-h / 8500)
  ```
- **Impact:** 40% density error at 5km → 15-30% apogee error
- **Priority:** P0

### 11. **Speed of Sound Constant - Wrong Above Sea Level**
- **Files:** Multiple
- **Issue:** Fixed c_sound = 343 m/s
- **Fix:**
  ```python
  T = 288.15 - 0.0065 * h  # ISA lapse rate
  c_sound = 331.3 * np.sqrt(T / 273.15)
  Mach = v / c_sound
  ```
- **Impact:** Mach 1.19 at sea level = Mach 1.27 at altitude - safety check bypass
- **Priority:** P0 - Safety critical

### 12. **Propellant Mass Flow Rate Assumed Constant**
- **File:** `src/models/dynamics.py`
- **Issue:** Mass flow computed once, not updated per time step
- **Fix:**
  ```python
  m_dot = (m_initial - m_dry) / t_burn
  m_current = m_initial - m_dot * t_elapsed
  a = (thrust - drag - m_current * g) / m_current
  ```
- **Impact:** Wrong acceleration profile during burn
- **Priority:** P1

### 13. **Cross-Sectional Area Ignores Nose Cone and Fins**
- **File:** `src/models/aerodynamics.py`
- **Issue:** `A = π × (d/2)²` only uses body tube
- **Fix:** Use Barrowman equations for complete reference area
- **Impact:** Geometrically implausible designs
- **Priority:** P2

### 14. **Gravity Treated as Constant 9.81 m/s²**
- **Files:** Multiple
- **Issue:** No altitude correction
- **Fix:** `g = 9.80665 × (R_earth / (R_earth + h))²`
- **Impact:** ~0.14% error at 5km, compounds over coast phase
- **Priority:** P3

---

## 🐛 CODE BUGS

### 15. **Version Constraint Mismatch**
- **Files:** `README.md` vs `setup.py:29`
- **Issue:** README says Python 3.8+, setup.py requires 3.10+
- **Fix:** Make consistent (recommend 3.10+)
- **Priority:** P1

### 16. **Complete Analysis Reports 404% Error as "CLOSE"**
- **File:** `run/run_complete_analysis.py`, `hybrid_optimizer.py`
- **Issue:** 25,226m vs 5,000m target marked as CLOSE instead of FAILED
- **Fix:** Update result classification logic
- **Priority:** P1

### 17. **Supersonic Prevention Not Enforced**
- **File:** `src/optimization/hybrid_optimizer.py`
- **Issue:** Max Mach 1.589 returned as valid result
- **Fix:** Wire up post-optimization supersonic check
- **Priority:** P0 - Safety critical

### 18. **Bare Except Swallows Errors in Verification**
- **File:** `verify_installation.py:112`
- **Issue:** `except Exception as e` hides tracebacks
- **Fix:** Re-raise or log `traceback.format_exc()`
- **Priority:** P2

### 19. **Pandas Dependency Unused**
- **Files:** `setup.py:16`, `requirements.txt`
- **Issue:** pandas>=2.0.0 required but never imported
- **Fix:** Remove or move to extras_require
- **Impact:** +30MB install footprint
- **Priority:** P2

---

## ⚡ CODE QUALITY & IMPROVEMENTS

### 20. **No CI/GitHub Actions**
- **Location:** Repository root (missing `.github/workflows/`)
- **Fix:** Add pytest workflow on push
- **Priority:** P1

### 21. **Numba as Core Dependency**
- **File:** `setup.py:16`
- **Issue:** Should be optional, fails on some platforms
- **Fix:** Move to `extras_require["performance"]` with graceful fallback
- **Priority:** P2

### 22. **Version String Duplicated**
- **Files:** `setup.py:3`, `README.md` footer
- **Issue:** setup.py says 1.0.0, README says 3.0
- **Fix:** Single source of truth in `src/__init__.py` with `__version__`
- **Priority:** P2

### 23. **Physical Constants Undocumented**
- **Location:** `src/models/` (missing constants documentation)
- **Fix:** Add `constants.py` with sources cited
- **Priority:** P2

### 24. **No Type Hints**
- **Files:** All `src/optimization/*.py`
- **Issue:** mypy listed as dev dependency but no annotations
- **Fix:** Add type hints to public API
- **Priority:** P2

### 25. **Result Dict Uses String Keys**
- **Files:** `hybrid_optimizer.py`, `fast_optimizer.py`
- **Issue:** Plain dict with no schema
- **Fix:** Replace with `@dataclass` or `TypedDict`
- **Priority:** P2

### 26. **Rocket Config Has No Validation**
- **Files:** All optimizers
- **Issue:** Missing keys raise KeyError deep in physics code
- **Fix:** Add `RocketConfig` dataclass with `validate()` method
- **Priority:** P2

### 27. **verify_installation.py Uses .capitalize() Wrong**
- **File:** `verify_installation.py:140`
- **Issue:** 'run_files'.capitalize() → 'Run_files'
- **Fix:** Use `.replace('_', ' ').title()`
- **Priority:** P3

### 28. **Mach 1.2 Hardcoded Throughout**
- **Files:** `feasibility_checker.py`, `advanced_aerodynamics.py`
- **Fix:** Define `SUPERSONIC_MACH_LIMIT = 1.2` constant
- **Priority:** P3

### 29. **Accuracy Claims Not Reproducible**
- **File:** `README.md`
- **Issue:** "80%/90%/95% accuracy" with no benchmark
- **Fix:** Add `tests/test_accuracy.py` with reference cases
- **Priority:** P1

---

## 🏗️ ARCHITECTURE ISSUES

### 30. **No __init__.py Package Exports**
- **File:** `src/__init__.py`
- **Issue:** Users must import by full path
- **Fix:** Define clean public API exports
- **Priority:** P2

### 31. **Six run/ Scripts Duplicate Config**
- **Files:** All `run/*.py`
- **Issue:** Same ROCKET_CONFIG hardcoded 6 times
- **Fix:** Centralize in `data/default_config.yaml` with CLI overrides
- **Priority:** P2

### 32. **"Parallel Optimizer" Name Misleading**
- **File:** `src/optimization/vispootanam_parallel_optimizer.py`
- **Issue:** No documented parallelism mechanism
- **Fix:** Document multiprocessing OR rename to `AccurateOptimizer`
- **Priority:** P2

---

## 📋 PRIORITY SUMMARY

### **P0 - Critical (Fix Immediately):**
1. Thrust time-gating (#1)
2. Fast initial guess physics (#2)
3. Ideal trajectory consistency (#3)
4. Apogee burnout altitude (#4)
5. Supersonic check altitude correction (#5, #11)
6. State validation crash (#6)
7. Zero-drag apogee formula (#9)
8. Constant air density (#10)
9. Supersonic prevention enforcement (#17)

### **P1 - High Priority:**
- ProcessPoolExecutor Windows fix (#7)
- Fake convergence data (#8)
- Variable mass flow (#12)
- Version mismatch (#15)
- Result classification (#16)
- No CI (#20)
- Accuracy benchmarks (#29)

### **P2 - Medium Priority:**
- Code quality improvements (#18-28, #30-32)

### **P3 - Low Priority:**
- Minor improvements (#13, #14, #27, #28)

---

## 🎯 RECOMMENDED FIX ORDER

1. **Fix thrust time-gating** (#1) - This alone fixes the 404% error
2. **Fix all physics formulas** (#2, #3, #4, #9, #10, #11, #12) - Get the math right
3. **Fix safety checks** (#5, #11, #17) - Ensure supersonic prevention works
4. **Fix crashes** (#6) - Stability
5. **Replace fake data** (#8) - Credibility
6. **Fix Windows support** (#7) - Platform compatibility
7. **Add validation & types** (#24, #25, #26) - Prevent future bugs
8. **Add CI & tests** (#20, #29) - Catch regressions
9. **Clean up architecture** (#30, #31, #32) - Maintainability
10. **Polish** (#15-23, #27-28) - Documentation & UX

---

## 📊 IMPACT ANALYSIS

**Root Cause:** Issue #1 (thrust time-gating) is the single line causing the 404% error.

**Secondary Issues:** Issues #2-5, #9-11 compound the error and prevent accurate predictions.

**Safety Critical:** Issues #5, #11, #17 directly affect the "100% supersonic prevention" claim.

**Credibility:** Issue #8 undermines all performance claims in documentation.

**Total Issues:** 32 identified issues across critical bugs, physics errors, code bugs, quality, and architecture.

---

**Next Steps:**
1. Start with P0 critical bugs
2. Run full test suite after each fix
3. Update documentation with corrected formulas
4. Re-generate all performance graphs with real data
5. Add regression tests for each fixed bug
