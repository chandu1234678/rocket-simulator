"""
Advanced Aerodynamics Module
3-Regime Drag Coefficient System with Fallback
"""

import numpy as np
from typing import Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class FlightRegime(Enum):
    """Flight regime classification"""
    SUBSONIC = "D1_SUBSONIC"           # M < 0.3
    COMPRESSIBLE = "D2_COMPRESSIBLE"   # 0.3 <= M < 0.6
    TRANSONIC = "D3_TRANSONIC"         # 0.6 <= M < 1.2
    SUPERSONIC = "SUPERSONIC"          # M >= 1.2 (FORBIDDEN)


@dataclass
class RegimeConfig:
    """Configuration for each flight regime"""
    name: str
    mach_min: float
    mach_max: float
    cd_base_min: float
    cd_base_max: float
    user_weight: float  # 0.0 = purely derived, 1.0 = purely user
    derived_weight: float
    
    def __post_init__(self):
        assert abs(self.user_weight + self.derived_weight - 1.0) < 1e-6, \
            "Weights must sum to 1.0"


class AdvancedAerodynamics:
    """
    ISRO-Level Advanced Aerodynamics System
    
    Features:
    - 3 flight regimes with different Cd estimation strategies
    - Parallel regime optimization
    - Automatic fallback to base drag on divergence
    - Real-time capable (1000+ iterations)
    """
    
    # Regime definitions
    REGIMES = {
        FlightRegime.SUBSONIC: RegimeConfig(
            name="D1_SUBSONIC",
            mach_min=0.0,
            mach_max=0.3,
            cd_base_min=0.15,
            cd_base_max=0.35,
            user_weight=0.0,      # Purely derived
            derived_weight=1.0
        ),
        FlightRegime.COMPRESSIBLE: RegimeConfig(
            name="D2_COMPRESSIBLE",
            mach_min=0.3,
            mach_max=0.6,
            cd_base_min=0.20,
            cd_base_max=0.45,
            user_weight=0.3,      # 30% user, 70% derived
            derived_weight=0.7
        ),
        FlightRegime.TRANSONIC: RegimeConfig(
            name="D3_TRANSONIC",
            mach_min=0.6,
            mach_max=1.2,
            cd_base_min=0.30,
            cd_base_max=0.85,
            user_weight=0.6,      # 60% user, 40% derived
            derived_weight=0.4
        )
    }
    
    def __init__(self, 
                 user_cd_estimates: Optional[Dict[str, float]] = None,
                 surface_roughness: float = 0.0,
                 use_fallback: bool = True):
        """
        Initialize advanced aerodynamics
        
        Args:
            user_cd_estimates: User-provided Cd estimates for each regime
                              {'D1': 0.25, 'D2': 0.35, 'D3': 0.65}
            surface_roughness: Surface roughness factor (0.0 = smooth, 1.0 = rough)
            use_fallback: Enable fallback to base drag on divergence
        """
        self.user_cd_estimates = user_cd_estimates or {}
        self.surface_roughness = surface_roughness
        self.use_fallback = use_fallback
        self.fallback_active = False
        self.divergence_count = 0
        
    def classify_regime(self, mach: float) -> FlightRegime:
        """Classify flight regime based on Mach number"""
        if mach >= 1.2:
            return FlightRegime.SUPERSONIC
        elif mach >= 0.6:
            return FlightRegime.TRANSONIC
        elif mach >= 0.3:
            return FlightRegime.COMPRESSIBLE
        else:
            return FlightRegime.SUBSONIC
    
    def get_derived_cd(self, 
                       mach: float, 
                       diameter: float, 
                       nose_length: float,
                       body_length: float,
                       reynolds: float) -> float:
        """
        Calculate derived Cd using aerodynamic theory
        
        Based on:
        - Geometry (fineness ratio, nose shape)
        - Reynolds number (skin friction)
        - Mach number (compressibility)
        - Surface roughness
        """
        # Fineness ratio
        total_length = nose_length + body_length
        fineness_ratio = total_length / diameter
        
        # Base drag coefficient (geometry-dependent)
        # Optimal fineness ratio is ~10-15
        if fineness_ratio < 5:
            cd_base = 0.45  # Too short - high drag
        elif fineness_ratio > 20:
            cd_base = 0.40  # Too long - high skin friction
        else:
            # Optimal range
            cd_base = 0.25 + 0.02 * abs(fineness_ratio - 12.5)
        
        # Skin friction coefficient (Reynolds-dependent)
        if reynolds > 1e4:
            cf = 0.074 / (reynolds ** 0.2)  # Turbulent
        else:
            cf = 1.328 / np.sqrt(reynolds)  # Laminar
        
        # Surface area factor
        wetted_area = np.pi * diameter * total_length
        reference_area = np.pi * (diameter / 2) ** 2
        area_ratio = wetted_area / reference_area
        
        # Skin friction drag
        cd_friction = cf * area_ratio
        
        # Pressure drag (form drag)
        cd_pressure = cd_base * (1.0 + 0.1 * self.surface_roughness)
        
        # Compressibility correction
        if mach < 0.3:
            # Incompressible
            cd_compressibility = 1.0
        elif mach < 0.6:
            # Subsonic compressible
            beta = np.sqrt(1 - mach**2)
            cd_compressibility = 1.0 / beta
        else:
            # Transonic - wave drag
            if mach < 0.9:
                # Pre-transonic rise
                cd_wave = 0.1 * ((mach - 0.6) / 0.3) ** 2
            else:
                # Transonic spike
                cd_wave = 0.1 + 0.3 * np.exp(-10 * (mach - 1.0) ** 2)
            cd_compressibility = 1.0 + cd_wave
        
        # Total derived Cd
        cd_derived = (cd_friction + cd_pressure) * cd_compressibility
        
        return cd_derived
    
    def get_user_cd(self, regime: FlightRegime) -> float:
        """Get user-provided Cd estimate for regime"""
        regime_key = regime.value.split('_')[0]  # D1, D2, D3
        
        if regime_key in self.user_cd_estimates:
            return self.user_cd_estimates[regime_key]
        
        # Default estimates if not provided
        defaults = {
            'D1': 0.25,
            'D2': 0.35,
            'D3': 0.65
        }
        return defaults.get(regime_key, 0.35)
    
    def get_cd(self,
               mach: float,
               diameter: float,
               nose_length: float,
               body_length: float,
               reynolds: float,
               velocity: float,
               altitude: float) -> Tuple[float, FlightRegime, bool]:
        """
        Get drag coefficient for current flight conditions
        
        Returns:
            (cd, regime, fallback_used)
        """
        # Classify regime
        regime = self.classify_regime(mach)
        
        # SUPERSONIC CHECK
        if regime == FlightRegime.SUPERSONIC:
            # Return high drag to prevent further acceleration
            return 2.0, regime, False
        
        # Check for fallback mode
        if self.fallback_active:
            # Use simple base drag
            cd_base = 0.35 + 0.1 * self.surface_roughness
            return cd_base, regime, True
        
        # Get regime configuration
        config = self.REGIMES[regime]
        
        # Calculate derived Cd
        cd_derived = self.get_derived_cd(
            mach, diameter, nose_length, body_length, reynolds
        )
        
        # Get user Cd
        cd_user = self.get_user_cd(regime)
        
        # Blend based on regime weights
        cd = (config.derived_weight * cd_derived + 
              config.user_weight * cd_user)
        
        # Clamp to regime bounds
        cd = np.clip(cd, config.cd_base_min, config.cd_base_max)
        
        # Divergence detection
        if cd < 0 or cd > 2.0 or np.isnan(cd) or np.isinf(cd):
            self.divergence_count += 1
            if self.divergence_count > 10 and self.use_fallback:
                print(f"  Divergence detected - activating fallback to base drag")
                self.fallback_active = True
                cd_base = 0.35 + 0.1 * self.surface_roughness
                return cd_base, regime, True
        
        return cd, regime, False
    
    def get_base_drag_fallback(self) -> float:
        """Get simple base drag coefficient for fallback"""
        return 0.35 + 0.1 * self.surface_roughness
    
    def reset_fallback(self):
        """Reset fallback state for new simulation"""
        self.fallback_active = False
        self.divergence_count = 0
    
    def get_regime_bounds(self, regime: FlightRegime) -> Tuple[float, float]:
        """Get Cd bounds for optimization in specific regime"""
        if regime == FlightRegime.SUPERSONIC:
            return (0.0, 0.0)  # Not allowed
        config = self.REGIMES[regime]
        return (config.cd_base_min, config.cd_base_max)
    
    def print_regime_info(self):
        """Print regime configuration"""
        print("\n" + "="*80)
        print("ADVANCED AERODYNAMICS - REGIME CONFIGURATION")
        print("="*80)
        
        for regime, config in self.REGIMES.items():
            print(f"\n{config.name}:")
            print(f"  Mach Range:    {config.mach_min:.1f} - {config.mach_max:.1f}")
            print(f"  Cd Range:      {config.cd_base_min:.2f} - {config.cd_base_max:.2f}")
            print(f"  User Weight:   {config.user_weight*100:.0f}%")
            print(f"  Derived Weight: {config.derived_weight*100:.0f}%")
            
            regime_key = config.name.split('_')[0]
            if regime_key in self.user_cd_estimates:
                print(f"  User Cd:       {self.user_cd_estimates[regime_key]:.3f}")
        
        print(f"\nSurface Roughness: {self.surface_roughness:.3f}")
        print(f"Fallback Enabled:  {self.use_fallback}")
        print("="*80)


# Example usage and testing
if __name__ == "__main__":
    # Test advanced aerodynamics
    aero = AdvancedAerodynamics(
        user_cd_estimates={'D1': 0.22, 'D2': 0.33, 'D3': 0.68},
        surface_roughness=0.05,
        use_fallback=True
    )
    
    aero.print_regime_info()
    
    # Test different Mach numbers
    print("\n" + "="*80)
    print("DRAG COEFFICIENT CALCULATION TEST")
    print("="*80)
    
    test_conditions = [
        (0.2, "Subsonic"),
        (0.45, "Compressible"),
        (0.85, "Transonic"),
        (1.15, "Near-Supersonic"),
        (1.25, "Supersonic (FORBIDDEN)")
    ]
    
    diameter = 0.1
    nose_length = 0.3
    body_length = 1.2
    reynolds = 1e6
    
    print(f"\nRocket Geometry:")
    print(f"  Diameter:      {diameter:.3f} m")
    print(f"  Nose Length:   {nose_length:.3f} m")
    print(f"  Body Length:   {body_length:.3f} m")
    print(f"  Fineness Ratio: {(nose_length + body_length) / diameter:.1f}")
    
    print(f"\n{'Mach':<8} {'Regime':<20} {'Cd':<8} {'Fallback':<10}")
    print("-" * 80)
    
    for mach, description in test_conditions:
        cd, regime, fallback = aero.get_cd(
            mach, diameter, nose_length, body_length,
            reynolds, mach * 340, 1000
        )
        
        fallback_str = "YES" if fallback else "NO"
        print(f"{mach:<8.2f} {regime.value:<20} {cd:<8.4f} {fallback_str:<10}")
    
    print("="*80)
