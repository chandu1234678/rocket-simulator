# Installation Guide

Complete installation instructions for the Vispootanam Rocket Trajectory Optimization System.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Installation](#quick-installation)
3. [Detailed Installation](#detailed-installation)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements

- **Operating System:** Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher
- **RAM:** 4 GB
- **Disk Space:** 500 MB
- **Processor:** Dual-core 2.0 GHz

### Recommended Requirements

- **Operating System:** Windows 11, macOS 12+, or Linux (Ubuntu 22.04+)
- **Python:** 3.10 or higher
- **RAM:** 8 GB or more
- **Disk Space:** 1 GB
- **Processor:** Quad-core 2.5 GHz or better

### Software Dependencies

- Python 3.8+
- pip (Python package manager)
- Git (for cloning repository)

## Quick Installation

### For Students (Simplest Method)

```bash
# 1. Download and install Python from python.org
# 2. Download the project ZIP from GitHub
# 3. Extract to a folder
# 4. Open terminal/command prompt in that folder
# 5. Run:

pip install -r requirements.txt
python verify_installation.py
```

### For Developers

```bash
# Clone repository
git clone https://github.com/your-org/rocket-trajectory-optimizer.git
cd rocket-trajectory-optimizer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python verify_installation.py
```

## Detailed Installation

### Step 1: Install Python

#### Windows

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer
3. **Important:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```

#### macOS

```bash
# Using Homebrew (recommended)
brew install python@3.10

# Or download from python.org
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3-pip python3-venv
```

### Step 2: Install Git (Optional)

#### Windows

Download from [git-scm.com](https://git-scm.com/download/win)

#### macOS

```bash
brew install git
```

#### Linux

```bash
sudo apt install git
```

### Step 3: Get the Project

#### Option A: Clone with Git (Recommended)

```bash
git clone https://github.com/your-org/rocket-trajectory-optimizer.git
cd rocket-trajectory-optimizer
```

#### Option B: Download ZIP

1. Go to GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract to desired location
4. Open terminal in extracted folder

### Step 4: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (Command Prompt):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# You should see (venv) in your prompt
```

**Why use virtual environment?**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Easy to remove (just delete venv folder)

### Step 5: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# For development (optional)
pip install pytest pytest-cov black flake8 mypy
```

### Step 6: Verify Installation

```bash
python verify_installation.py
```

Expected output:
```
============================================================
SYSTEM VERIFICATION
============================================================
Checking imports...
  All core modules imported successfully

Checking project structure...
  src/core: OK
  src/models: OK
  ...

============================================================
STATUS: ALL CHECKS PASSED
System is ready for use
============================================================
```

## Platform-Specific Instructions

### Windows

#### PowerShell Execution Policy

If you get an error activating virtual environment:

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Long Path Support

Enable long paths for Windows:

1. Open Registry Editor (regedit)
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Set `LongPathsEnabled` to 1

Or use PowerShell (as Administrator):
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

#### Multiprocessing on Windows

For parallel optimization, ensure scripts have:

```python
if __name__ == '__main__':
    main()
```

### macOS

#### Xcode Command Line Tools

Some packages require compilation:

```bash
xcode-select --install
```

#### M1/M2 (Apple Silicon)

Use native Python for best performance:

```bash
# Check architecture
python -c "import platform; print(platform.machine())"
# Should show: arm64

# If showing x86_64, install native Python:
arch -arm64 brew install python@3.10
```

### Linux

#### Additional Dependencies

```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc gcc-c++ python3-devel

# Arch
sudo pacman -S base-devel python
```

#### Permission Issues

If pip install fails with permission errors:

```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
```

## Verification

### Basic Verification

```bash
python verify_installation.py
```

### Comprehensive Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python tests/test_optimization.py

# Run system demo
python tests/DEMO_VISPOOTANAM_SYSTEM.py
```

### Performance Benchmark

```bash
python tests/test_speed_final.py
```

Expected performance:
- Fast Optimizer: < 0.01s
- Hybrid Optimizer: < 1s
- Parallel Optimizer: < 3s

### Quick Functionality Test

```bash
python run/run_fast_optimization.py
```

Should complete in < 1 second with optimization results.

## Troubleshooting

### Common Issues

#### Issue: "Python not found"

**Solution:**
```bash
# Windows: Add Python to PATH
# Or use full path:
C:\Python310\python.exe verify_installation.py

# Linux/Mac: Install Python
sudo apt install python3.10  # Ubuntu
brew install python@3.10     # macOS
```

#### Issue: "pip not found"

**Solution:**
```bash
# Install pip
python -m ensurepip --upgrade

# Or download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

#### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Issue: "Permission denied"

**Solution:**
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Or use --user flag
pip install --user -r requirements.txt
```

#### Issue: NumPy/SciPy installation fails

**Solution:**
```bash
# Windows: Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or use pre-built wheels
pip install --only-binary :all: numpy scipy

# Or use conda
conda install numpy scipy
```

#### Issue: Slow optimization on Windows

**Solution:**
- Ensure multiprocessing protection: `if __name__ == '__main__':`
- Use fewer workers: `n_parallel_workers=2`
- Try hybrid optimizer instead of parallel

#### Issue: Tests fail on import

**Solution:**
```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows

# Or install in development mode
pip install -e .
```

### Getting Help

If issues persist:

1. Check [GitHub Issues](https://github.com/your-org/rocket-trajectory-optimizer/issues)
2. Read [FAQ](docs/FAQ.md)
3. Ask in [Discussions](https://github.com/your-org/rocket-trajectory-optimizer/discussions)
4. Email: support@example.com

### Reporting Bugs

Include:
- Operating system and version
- Python version (`python --version`)
- Full error message
- Steps to reproduce
- Output of `python verify_installation.py`

## Uninstallation

### Remove Virtual Environment

```bash
# Deactivate virtual environment
deactivate

# Delete virtual environment folder
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows
```

### Remove Project

```bash
# Delete project folder
cd ..
rm -rf rocket-trajectory-optimizer  # Linux/Mac
rmdir /s rocket-trajectory-optimizer  # Windows
```

### Remove Python Packages (if not using venv)

```bash
pip uninstall -r requirements.txt -y
```

## Updating

### Update to Latest Version

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Verify
python verify_installation.py
```

### Check for Updates

```bash
# Check current version
python -c "from src import __version__; print(__version__)"

# Check latest release on GitHub
```

## Next Steps

After successful installation:

1. **For Students:** Read [User Guide](USER_GUIDE.md)
2. **For Developers:** Read [API Reference](API_REFERENCE.md)
3. **Try Examples:** Run scripts in `run/` folder
4. **Run Tests:** `python -m pytest tests/`

## Support

- **Documentation:** `docs/` folder
- **Examples:** `examples/` folder
- **Issues:** GitHub Issues
- **Email:** support@example.com

---

**Last Updated:** May 2, 2026
