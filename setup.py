from setuptools import setup, find_packages

setup(
    name="rocket-simulator",
    version="1.0.0",
    description="ISRO-level rocket flight simulation system",
    author="GITAM University Rocketry Team",
    author_email="your.email@gitam.edu",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "matplotlib>=3.7.0",
        "pandas>=2.0.0",
        "numba>=0.57.0",
    ],
    extras_require={
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
