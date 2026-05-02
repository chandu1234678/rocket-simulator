"""
Basic rocket simulation example.
Demonstrates complete workflow from config to results.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import load_config
from src.core.simulation import SimulationEngine
import time


def print_header():
    """Print simulation header."""
    print("=" * 60)
    print("🚀 ROCKET FLIGHT SIMULATOR")
    print("   ISRO-Level Trajectory Prediction")
    print("=" * 60)
    print()


def print_summary(summary: dict, elapsed_time: float):
    """Print simulation results."""
    print("\n" + "=" * 60)
    print("✅ SIMULATION COMPLETE")
    print("=" * 60)
    print()
    print("📊 RESULTS:")
    print(f"  Apogee:          {summary['apogee']:.2f} m")
    print(f"  Max Velocity:    {summary['max_velocity']:.2f} m/s")
    print(f"  Max Mach:        {summary['max_mach']:.3f}")
    print(f"  Burnout Time:    {summary['burnout_time']:.2f} s")
    print(f"  Apogee Time:     {summary['apogee_time']:.2f} s")
    print(f"  Flight Time:     {summary['flight_time']:.2f} s")
    print()
    print("⚡ PERFORMANCE:")
    print(f"  Computation Time: {elapsed_time:.3f} s")
    print(f"  Data Points:      {summary['num_points']}")
    print(f"  Speed:            {summary['num_points']/elapsed_time:.0f} points/s")
    print()
    print("=" * 60)


def main():
    """Run basic simulation."""
    print_header()
    
    # Load configuration
    print("📁 Loading configuration...")
    config_path = Path(__file__).parent.parent / "data" / "config.json"
    config = load_config(str(config_path))
    print(f"   Rocket: {config.rocket.name}")
    print(f"   Launch Site: {config.launch.latitude:.2f}°N, {config.launch.longitude:.2f}°E")
    print(f"   Altitude: {config.launch.altitude:.1f} m ASL")
    print()
    
    # Create simulation engine
    print("🔧 Initializing simulation engine...")
    sim = SimulationEngine(config)
    print("   ✓ Atmosphere model ready")
    print("   ✓ Propulsion model ready")
    print("   ✓ Aerodynamics model ready")
    print("   ✓ RK4 solver ready")
    print()
    
    # Run simulation
    print("🚀 Running simulation...")
    start_time = time.time()
    trajectory = sim.run()
    elapsed_time = time.time() - start_time
    print(f"   ✓ Simulation completed in {elapsed_time:.3f} seconds")
    print()
    
    # Get summary
    summary = sim.get_summary()
    
    # Print results
    print_summary(summary, elapsed_time)
    
    # Validation against OpenRocket
    print("📊 VALIDATION (vs OpenRocket):")
    openrocket_apogee = 161.478  # m
    openrocket_velocity = 91.946  # m/s
    openrocket_mach = 0.263
    
    apogee_error = abs(summary['apogee'] - openrocket_apogee) / openrocket_apogee * 100
    velocity_error = abs(summary['max_velocity'] - openrocket_velocity) / openrocket_velocity * 100
    mach_error = abs(summary['max_mach'] - openrocket_mach) / openrocket_mach * 100
    
    print(f"  Apogee Error:    {apogee_error:.2f}%")
    print(f"  Velocity Error:  {velocity_error:.2f}%")
    print(f"  Mach Error:      {mach_error:.2f}%")
    print()
    
    if apogee_error < 5.0:
        print("  ✅ Apogee within 5% target!")
    else:
        print("  ⚠️  Apogee error exceeds 5% - needs tuning")
    
    print("=" * 60)
    
    return trajectory, summary


if __name__ == "__main__":
    trajectory, summary = main()
