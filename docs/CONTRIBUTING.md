# Contributing to Vispootanam

Thank you for your interest in contributing to the Vispootanam Rocket Trajectory Optimization System!

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contribution Workflow](#contribution-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize safety in all rocket-related code

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Promoting unsafe rocket designs

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of rocket physics (for physics-related contributions)
- Familiarity with NumPy and SciPy (for optimization contributions)

### Areas for Contribution

We welcome contributions in:

- **Bug fixes** - Fix issues in existing code
- **Performance improvements** - Optimize algorithms
- **New features** - Add capabilities (see roadmap)
- **Documentation** - Improve guides and examples
- **Testing** - Add test coverage
- **Examples** - Create usage examples

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/rocket-trajectory-optimizer.git
cd rocket-trajectory-optimizer
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 4. Verify Installation

```bash
python verify_installation.py
```

### 5. Run Tests

```bash
python -m pytest tests/ -v
```

## Contribution Workflow

### 1. Create a Branch

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/bug-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions
- `refactor/` - Code refactoring
- `perf/` - Performance improvements

### 2. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_optimization.py -v

# Check coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add fin optimization algorithm"
```

#### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Tests
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `style` - Code style changes
- `chore` - Maintenance tasks

**Example:**
```
feat: add fin optimization algorithm

Implements fin design optimization using genetic algorithm.
Optimizes fin count, size, and sweep angle for stability.

Closes #123
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

#### Formatting

```python
# Use 4 spaces for indentation
def calculate_drag(velocity, diameter):
    drag_coefficient = 0.35
    return 0.5 * drag_coefficient * velocity**2

# Maximum line length: 100 characters
# Use descriptive variable names
# Add docstrings to all functions and classes
```

#### Docstrings

```python
def optimize_trajectory(config: Dict, target: float) -> Dict:
    """
    Optimize rocket trajectory to reach target altitude.
    
    Args:
        config: Rocket configuration dictionary with keys:
            - thrust: Thrust force in Newtons
            - burn_time: Burn duration in seconds
            - mass_initial: Initial mass in kg
        target: Target apogee in meters
    
    Returns:
        Dictionary containing:
            - diameter: Optimized diameter in meters
            - apogee: Achieved apogee in meters
            - error: Error from target in meters
    
    Raises:
        ValueError: If config is invalid
        RuntimeError: If optimization fails to converge
    
    Example:
        >>> config = {'thrust': 80.0, 'burn_time': 1.8, ...}
        >>> result = optimize_trajectory(config, 5000.0)
        >>> print(f"Diameter: {result['diameter']:.4f} m")
    """
    pass
```

#### Type Hints

```python
from typing import Dict, List, Tuple, Optional

def simulate_flight(
    config: Dict[str, float],
    diameter: float,
    cd: float
) -> Tuple[float, float, bool]:
    """Simulate rocket flight."""
    pass
```

#### Imports

```python
# Standard library imports
import sys
from pathlib import Path
from typing import Dict, List

# Third-party imports
import numpy as np
from scipy.optimize import minimize

# Local imports
from src.models.aerodynamics import calculate_drag
from src.solvers.rk4 import RK4Solver
```

### Code Quality Tools

```bash
# Format code with Black
black src/ tests/

# Check style with flake8
flake8 src/ tests/ --max-line-length=100

# Type checking with mypy
mypy src/
```

### Performance Guidelines

- Use NumPy vectorization instead of loops
- Cache expensive computations
- Profile before optimizing
- Document performance characteristics

```python
# Good - vectorized
velocities = np.linspace(0, 100, 1000)
drags = 0.5 * cd * velocities**2

# Bad - loop
drags = []
for v in velocities:
    drags.append(0.5 * cd * v**2)
```

## Testing Guidelines

### Test Structure

```python
import pytest
from src.optimization.fast_optimizer import FastOptimizer

class TestFastOptimizer:
    """Test suite for FastOptimizer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = {
            'thrust': 80.0,
            'burn_time': 1.8,
            'specific_impulse': 180,
            'mass_initial': 2.76,
            'mass_dry': 2.0
        }
    
    def test_optimization_converges(self):
        """Test that optimization converges."""
        optimizer = FastOptimizer(self.config, target_apogee=5000.0)
        result = optimizer.optimize_fast()
        
        assert result['converged'] is True
        assert result['error'] < 100.0
    
    def test_supersonic_prevention(self):
        """Test that supersonic flight is prevented."""
        config = self.config.copy()
        config['thrust'] = 500.0  # Very high thrust
        
        optimizer = FastOptimizer(config, target_apogee=5000.0)
        result = optimizer.optimize_fast()
        
        assert result['max_mach'] < 1.2
    
    @pytest.mark.parametrize("target", [1000, 3000, 5000, 10000])
    def test_multiple_targets(self, target):
        """Test optimization for multiple target altitudes."""
        optimizer = FastOptimizer(self.config, target_apogee=target)
        result = optimizer.optimize_fast()
        
        assert result['apogee'] > 0
        assert result['time'] < 5.0
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error conditions
- Test performance requirements
- Test safety features thoroughly

```bash
# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Performance Tests

```python
import time

def test_optimization_speed():
    """Test that optimization meets speed requirements."""
    optimizer = FastOptimizer(config, target_apogee=5000.0)
    
    start = time.time()
    result = optimizer.optimize_fast()
    elapsed = time.time() - start
    
    assert elapsed < 0.1  # Must complete in <0.1s
```

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Include examples in docstrings
- Document parameters, returns, and exceptions
- Explain complex algorithms

### User Documentation

When adding features, update:

- `docs/USER_GUIDE.md` - For student users
- `docs/API_REFERENCE.md` - For developers
- `docs/TECHNICAL_SPECIFICATION.md` - For technical details
- `README.md` - If adding major features

### Examples

Add usage examples to `examples/` folder:

```python
"""
Example: Optimize rocket for competition
Demonstrates hybrid optimization for high accuracy.
"""

from src.optimization.hybrid_optimizer import HybridOptimizer

# Competition rocket configuration
config = {
    'thrust': 120.0,
    'burn_time': 2.5,
    'specific_impulse': 200,
    'mass_initial': 3.5,
    'mass_dry': 2.8
}

# Optimize for 10km target
optimizer = HybridOptimizer(config, target_apogee=10000.0)
result = optimizer.optimize_hybrid()

print(f"Optimized Design:")
print(f"  Diameter: {result['diameter']:.4f} m")
print(f"  Apogee: {result['apogee']:.2f} m")
```

## Pull Request Process

### Before Submitting

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation update
- [ ] Code refactoring

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
```

### Review Process

1. Automated checks run (tests, linting)
2. Maintainer reviews code
3. Address feedback
4. Approval and merge

### After Merge

- Delete your feature branch
- Update your fork
- Celebrate your contribution!

## Questions?

- Check existing issues and PRs
- Read documentation in `docs/`
- Ask in GitHub Discussions
- Email: support@example.com

## Recognition

Contributors are recognized in:
- CHANGELOG.md
- GitHub contributors page
- Project documentation

Thank you for contributing to Vispootanam!

---

**Last Updated:** May 2, 2026
