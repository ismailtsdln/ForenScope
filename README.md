# ForenScope

![Status](https://img.shields.io/badge/Status-Development-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Go](https://img.shields.io/badge/Go-1.21%2B-cyan)
![License](https://img.shields.io/badge/License-MIT-green)

**ForenScope** is a professional-grade, high-performance hybrid digital forensics platform. It combines the flexibility and rich ecosystem of Python for orchestration and analysis with the raw performance of Go for disk scanning and data processing.

## 🚀 Features

- **Hybrid Architecture**: Python Orchestrator + Go Engine via gRPC.
- **High Performance**: Parallel disk scanning, carving, and hashing powered by Go.
- **Modular Design**: Plugin-based artifact parsers and extensible report generation.
- **Forensic Intelligence**: Registry analysis, Browser artifacts, System logs.
- **Timeline Analysis**: Unified timeline generation from multiple sources.
- **Enterprise Ready**: Structured logging, error handling, worker pools, and API support.

## 🛠 Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a deep dive.

- **Python**: Logic, Parsers, API (FastAPI), CLI (Typer)
- **Go**: Raw I/O, Scanning, Hashing, Carving
- **Communication**: gRPC / Protobuf

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Go 1.21+
- Protoc compiler

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ismailtsdln/ForenScope.git
   cd ForenScope
   ```

2. **Initialize the Environment (Python)**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Build the Engine (Go)**
   ```bash
   cd engine
   go mod download
   go build -o ../bin/engine main.go
   ```

4. **Generate Protobufs**
   ```bash
   # Scripts provided in Makefile (Coming Soon)
   ```

### Usage

**CLI Example:**
```bash
python -m cli scan --image /path/to/disk.img --fast
```

**Run API Server:**
```bash
uvicorn api.main:app --reload
```

## 📚 Documentation

- [Architecture](ARCHITECTURE.md)
- [Developer Guide](docs/DEVELOPMENT.md) (Coming Soon)

## 🛡 License

MIT License
