FROM python:3.11-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt setup.py ./
COPY src/__init__.py src/__init__.py

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy scipy matplotlib pytest pytest-cov

FROM base as dev
COPY . .
RUN pip install -e . --no-deps

FROM dev as test
CMD ["pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing", "-k", "not parallel"]

FROM base as prod
COPY src/ src/
COPY data/ data/
RUN pip install -e . --no-deps
CMD ["python"]
