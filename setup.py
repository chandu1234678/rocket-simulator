from setuptools import setup, find_packages
import os
import re

# Read version from src/__init__.py (single source of truth)
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), 'src', '__init__.py')
    with open(init_file, 'r') as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise RuntimeError("Unable to find version string in src/__init__.py")

setup(
    name="rocket-simulator",
    version=get_version(),
    description="ISRO-level rocket flight simulation system",
    author="GITAM University Rocketry Team",
    author_email="bbodapat2@gitam.in",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "performance": [
            "numba>=0.57.0",  # Optional JIT compilation for speed
        ],
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "mypy>=1.3.0",
            "pylint>=2.17.0",
        ],
        "docs": [
            "sphinx>=6.2.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3.10",
    ],
)
