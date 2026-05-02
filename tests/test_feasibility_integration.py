"""
Test Pre-Flight Feasibility Check Integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimization.feasibility_checker import FeasibilityChecker

def test_feasibility_integration():
    """Test the integrated feasibility checker"""
    
    checker = FeasibilityChecker(supersonic_limit=1.2)
    
    print("="*80)
    print("TESTING PRE-FLIGHT FEASIBILITY CHECK INTEGRATION")
    print("="*80)
    
    # Test 1: Good design (should pass) - subsonic thrust
    print("\n\n" + "="*80)
    print("TEST 1: FEASIBLE DESIGN (Should PASS)")
    print("="*80)
    result1 = checker.check_feasibility(
        thrust=80.0,  # Well below supersonic threshold
        burn_time=1.8,
        specific_impulse=180,
        mass_initial=2.76,
        mass_dry=2.0,
        target_apogee=500.0
    )
    checker.print_feasibility(result1)
    
    assert result1.can_proceed, "Test 1 should pass"
    assert not result1.is_supersonic, "Test 1 should not be supersonic"
    print("\n TEST 1 PASSED")
    
    # Test 2: Supersonic design (should fail)
    print("\n\n" + "="*80)
    print("TEST 2: SUPERSONIC DESIGN (Should FAIL)")
    print("="*80)
    result2 = checker.check_feasibility(
        thrust=2000.0,  # Too much thrust
        burn_time=3.0,
        specific_impulse=250,
        mass_initial=2.76,
        mass_dry=2.0,
        target_apogee=1000.0
    )
    checker.print_feasibility(result2)
    
    assert not result2.can_proceed, "Test 2 should fail"
    assert result2.is_supersonic, "Test 2 should be supersonic"
    assert 'options' in result2.suggestions, "Test 2 should have suggestions"
    print("\n TEST 2 PASSED (Correctly rejected supersonic design)")
    
    # Test 3: Insufficient altitude (should fail)
    print("\n\n" + "="*80)
    print("TEST 3: INSUFFICIENT ALTITUDE (Should FAIL)")
    print("="*80)
    result3 = checker.check_feasibility(
        thrust=50.0,  # Very low thrust - subsonic but insufficient
        burn_time=0.5,
        specific_impulse=100,
        mass_initial=2.76,
        mass_dry=2.0,
        target_apogee=5000.0  # Unreachable with this low thrust
    )
    checker.print_feasibility(result3)
    
    assert not result3.can_proceed, "Test 3 should fail"
    assert not result3.is_supersonic, "Test 3 should not be supersonic"
    assert result3.ideal_apogee < result3.target_apogee, "Test 3 ideal should be less than target"
    print("\n TEST 3 PASSED (Correctly rejected insufficient design)")
    
    # Summary
    print("\n\n" + "="*80)
    print("ALL TESTS PASSED ")
    print("="*80)
    print("\n SUMMARY:")
    print(f"  Test 1 (Feasible):     {result1.can_proceed} ")
    print(f"  Test 2 (Supersonic):   {not result2.can_proceed} ")
    print(f"  Test 3 (Insufficient): {not result3.can_proceed} ")
    print("\n Pre-flight feasibility check is working correctly!")
    print("   - Saves ~20 minutes by catching bad designs early")
    print("   - Prevents supersonic flight")
    print("   - Provides actionable suggestions")
    print("="*80)

if __name__ == "__main__":
    test_feasibility_integration()
