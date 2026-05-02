"""Verify installation and system functionality."""

import sys
from pathlib import Path

def check_imports():
    """Verify all core modules can be imported."""
    print("Checking imports...")
    
    try:
        from src.models import ideal_trajectory, advanced_aerodynamics
        from src.solvers import semi_implicit
        from src.optimization import (
            feasibility_checker,
            fast_optimizer,
            hybrid_optimizer,
            vispootanam_parallel_optimizer
        )
        print("  All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"  Import error: {e}")
        return False

def check_structure():
    """Verify project structure."""
    print("\nChecking project structure...")
    
    required_dirs = [
        'src/core',
        'src/models',
        'src/solvers',
        'src/optimization',
        'tests',
        'examples',
        'data',
        'run'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  {dir_path}: OK")
        else:
            print(f"  {dir_path}: MISSING")
            all_exist = False
    
    return all_exist

def check_documentation():
    """Verify documentation files."""
    print("\nChecking documentation...")
    
    required_docs = [
        'README.md',
        'docs/USER_GUIDE.md',
        'docs/PROJECT_STRUCTURE.md',
        'docs/API_REFERENCE.md',
        'docs/TECHNICAL_SPECIFICATION.md'
    ]
    
    all_exist = True
    for doc in required_docs:
        if Path(doc).exists():
            print(f"  {doc}: OK")
        else:
            print(f"  {doc}: MISSING")
            all_exist = False
    
    return all_exist

def check_run_files():
    """Verify run files exist."""
    print("\nChecking run files...")
    
    required_files = [
        'run/run_complete_analysis.py',
        'run/run_feasibility_check.py',
        'run/run_fast_optimization.py',
        'run/run_accurate_optimization.py',
        'run/run_production_optimization.py',
        'run/run_trajectory_simulation.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  {file_path}: OK")
        else:
            print(f"  {file_path}: MISSING")
            all_exist = False
    
    return all_exist

def quick_functionality_test():
    """Run a quick functionality test."""
    print("\nRunning quick functionality test...")
    
    try:
        from src.optimization.fast_optimizer import FastOptimizer
        
        base_config = {
            'thrust': 80.0,
            'burn_time': 1.8,
            'specific_impulse': 180,
            'mass_initial': 2.76,
            'mass_dry': 2.0
        }
        
        optimizer = FastOptimizer(base_config, target_apogee=5000.0)
        result = optimizer.optimize_fast()
        
        if result['time'] < 5.0:
            print(f"  Fast optimizer: OK (time: {result['time']:.3f}s)")
            return True
        else:
            print(f"  Fast optimizer: SLOW (time: {result['time']:.3f}s)")
            return False
            
    except Exception as e:
        print(f"  Functionality test failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("="*60)
    print("SYSTEM VERIFICATION")
    print("="*60)
    
    results = {
        'imports': check_imports(),
        'structure': check_structure(),
        'documentation': check_documentation(),
        'run_files': check_run_files(),
        'functionality': quick_functionality_test()
    }
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {check.capitalize()}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("STATUS: ALL CHECKS PASSED")
        print("System is ready for use")
    else:
        print("STATUS: SOME CHECKS FAILED")
        print("Please review errors above")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
