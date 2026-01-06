# Contributing to ForenScope

Thank you for your interest in contributing to ForenScope! We welcome contributions from the community to help make this the best hybrid forensic platform.

## Getting Started

1.  **Fork** the repository on GitHub.
2.  **Clone** your fork locally.
3.  **Install dependencies** (`pip install -r requirements.txt`) and **Build** the engine (`make all`).

## Development Workflow

### Python (Logic Layer)
*   Follow PEP8 standards.
*   Use type hints (`mypy` compliant).
*   Run tests via `pytest`.

### Go (Engine Layer)
*   Follow standard Go patterns (Effective Go).
*   Run `go fmt` before committing.
*   Ensure goroutines do not leak (use `context` for cancellation).

### Protobuf Contracts
*   If you modify `.proto` files in `contracts/`, you **MUST** run `make proto` to regenerate steps.
*   Do not manually edit the generated `_pb2.py` or `.pb.go` files.

## Pull Requests

1.  Create a new branch for your feature (`git checkout -b feature/amazing-feature`).
2.  Commit your changes with clear messages.
3.  Push to the branch.
4.  Open a Pull Request.

## Code of Conduct

Please be respectful and professional in all interactions.
