# Building ForenScope

This document provides detailed build instructions for ForenScope, including optional YARA integration.

## Prerequisites

### Core Requirements
- **Python 3.10+**
- **Go 1.21+**
- **protoc** (Protocol Buffers Compiler)
  ```bash
  # macOS
  brew install protobuf
  
  # Ubuntu/Debian
  sudo apt-get install protobuf-compiler
  
  # Windows (via Chocolatey)
  choco install protoc
  ```

### Python Dependencies
```bash
pip install -r requirements.txt
```

### Go Dependencies
```bash
cd engine
go mod tidy
```

---

## Standard Build (Without YARA)

The standard build uses a stub implementation for YARA, allowing the engine to compile without the go-yara library installed.

```bash
# From project root
make all
```

This command will:
1. Generate Protocol Buffer files
2. Build the Go engine (without YARA support)
3. Create `bin/engine` executable

---

## Building with YARA Support

### Install YARA Library

#### macOS
```bash
brew install yara
```

#### Ubuntu/Debian
```bash
sudo apt-get install libyara-dev
```

#### From Source
```bash
git clone https://github.com/VirusTotal/yara.git
cd yara
./bootstrap.sh
./configure --enable-cuckoo --enable-magic
make
sudo make install
sudo ldconfig  # Linux only
```

### Install go-yara Binding
```bash
go get github.com/hillu/go-yara/v4
```

### Build Engine with YARA
```bash
cd engine
go build -tags yara -o ../bin/engine main.go
```

The `-tags yara` flag enables the YARA implementation instead of the stub.

### Verify YARA Support
```bash
./bin/engine --help
# Look for YARA-related options
```

---

## Build Targets

### Full Build (Protobuf + Engine)
```bash
make all
```

### Protobuf Generation Only
```bash
make proto
```

This generates:
- `core/rpc/engine_pb2.py` (Python)
- `core/rpc/engine_pb2_grpc.py` (Python)
- `engine/proto/engine.pb.go` (Go)
- `engine/proto/engine_grpc.pb.go` (Go)

### Engine Only
```bash
make build
```

### Run Engine Directly
```bash
make run-engine
```

---

## Cross-Platform Builds

### Linux from macOS
```bash
cd engine
GOOS=linux GOARCH=amd64 go build -o ../bin/engine-linux main.go
```

### Windows from macOS/Linux
```bash
cd engine
GOOS=windows GOARCH=amd64 go build -o ../bin/engine.exe main.go
```

### With YARA (Requires Platform-Specific YARA Libraries)
```bash
GOOS=linux GOARCH=amd64 go build -tags yara -o ../bin/engine-linux main.go
```

**Note:** Cross-compiling with YARA requires the YARA library to be built for the target platform.

---

## Testing

### Python Tests
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=core --cov=artifacts --cov=orchestrator
```

### Go Tests
```bash
cd engine
go test ./... -v

# With coverage
go test ./... -v -cover

# Specific package
go test ./scanner -v
```

### Integration Tests
```bash
# Start the engine in one terminal
./bin/engine

# Run CLI tests in another terminal
python cli/main.py ping
python cli/main.py scan --image ./tests
```

---

## Troubleshooting

### Protobuf Generation Fails
**Issue:** `protoc: command not found`

**Solution:** Install Protocol Buffers compiler (see Prerequisites)

---

### YARA Build Fails
**Issue:** `fatal error: yara.h: No such file or directory`

**Solution:** Install YARA development headers:
```bash
# Ubuntu/Debian
sudo apt-get install libyara-dev

# macOS
brew install yara
```

---

### Python Import Errors
**Issue:** `ModuleNotFoundError: No module named 'grpc'`

**Solution:** Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

### Go Module Errors
**Issue:** `go.mod file not found`

**Solution:**
```bash
cd engine
go mod init github.com/ismailtsdln/forenscope/engine
go mod tidy
```

---

## Docker Build

### Build Image
```bash
docker build -t forenscope:latest .
```

### Run in Container
```bash
docker-compose up
```

---

## Performance Optimization

### Release Build (Optimized)
```bash
cd engine
go build -ldflags="-s -w" -o ../bin/engine main.go
```

Flags:
- `-s`: Strip debug symbols
- `-w`: Strip DWARF debug info

### Profile Guided Optimization (PGO)
```bash
# 1. Build with profiling
go build -o engine main.go

# 2. Run with profiling
./engine -cpuprofile=cpu.prof

# 3. Rebuild with profile
go build -pgo=cpu.prof -o engine main.go
```

---

## CI/CD Integration

GitHub Actions automatically builds and tests on:
- Python 3.10
- Go 1.21
- Ubuntu Latest

See `.github/workflows/test.yml` for details.

---

## Next Steps

After building:
1. Run the engine: `./bin/engine`
2. Test with CLI: `python cli/main.py ping`
3. Start API server: `uvicorn api.main:app`
4. Review documentation: `README.md`
