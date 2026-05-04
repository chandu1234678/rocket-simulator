# Docker Guide

## Quick Start

### Run Tests
```bash
docker-compose run test
```

### Development
```bash
docker-compose run dev bash
```

### Production
```bash
docker build --target prod -t rocket-simulator:latest .
docker run --rm rocket-simulator:latest python examples/basic_simulation.py
```

## Multi-Python Testing

```bash
# Python 3.10
docker build --build-arg PYTHON_VERSION=3.10 --target test -t rocket-sim:py310 -f Dockerfile.multi .
docker run --rm rocket-sim:py310

# Python 3.11
docker build --build-arg PYTHON_VERSION=3.11 --target test -t rocket-sim:py311 -f Dockerfile.multi .
docker run --rm rocket-sim:py311

# Python 3.12
docker build --build-arg PYTHON_VERSION=3.12 --target test -t rocket-sim:py312 -f Dockerfile.multi .
docker run --rm rocket-sim:py312
```

## Benefits

- **Consistency**: Same environment across all platforms
- **Isolation**: No dependency conflicts
- **Speed**: Layer caching for faster builds
- **Multi-Python**: Easy testing across versions

## Troubleshooting

### Clean Build
```bash
docker build --no-cache --target test -t rocket-simulator:test .
```

### Remove Old Images
```bash
docker system prune -a
```

### Enable BuildKit
```bash
export DOCKER_BUILDKIT=1
docker build --target test -t rocket-simulator:test .
```
