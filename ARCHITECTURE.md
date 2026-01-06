# ForenScope Architecture

## Overview
ForenScope is a hybrid digital forensics automation platform designed for high performance and extensibility. It utilizes a Hexagonal / Clean Architecture approach.

### Core Technologies
- **Python**: Serves as the brain (Orchestrator, Logic, Parsers, API, CLI).
- **Go**: Serves as the brawn (High-performance Engines: Scanner, Carver, Hasher).
- **gRPC (Protobuf)**: Defines the strict contract between the Python brain and the Go brawn.

## System Components

### 1. Python Layer (The Orchestrator)
Located in `core/`, `orchestrator/`, `api/`, `cli/`.
- **Orchestrator**: Manages task scheduling, retries, and logging. It delegates CPU-intensive tasks to the Go Engine.
- **Forensic Logic**: Contains abstract definitions for Artifacts and Evidence.
- **API**: FastAPI based REST interface for job management and status checks.
- **CLI**: Typer based command-line interface for direct interaction.

### 2. Go Layer (The Engine)
Located in `engine/`.
- **Worker Pool**: Manages concurrent execution of tasks.
- **Scanner**: Performs raw disk scanning and signature detection.
- **Carver**: Handles file carving based on headers/footers and entropy.
- **Hasher**: High-speed parallel hashing (SHA256, MD5, Bloom Filters).

### 3. Communication Layer
Located in `contracts/`.
- **Protobuf**: Defines the service methods (e.g., `Scan`, `Carve`, `Hash`) and data structures.
- **gRPC**: The transport mechanism.

## Data Flow
1. **User** initiates a task via CLI or API.
2. **Orchestrator** receives the request and creates a Job.
3. **Orchestrator** selects the appropriate strategy.
4. If heavy lifting is required (e.g., Disk Scan), it calls the **Go Engine** via gRPC.
5. **Go Engine** processes the data (streaming or bulk) and returns results/stream.
6. **Python Layer** processes the results, parses specific artifacts (Registry, Logs), and stores them.
7. **Reporting Engine** generates the final output (HTML/PDF/JSON).

## Directory Structure
```
forenscope/
├── core/                 # Core domain logic & abstractions
├── orchestrator/         # Task management & engine delegation
├── artifacts/            # Python artifact parsers
├── timeline/             # Timeline normalization & generation
├── reporting/            # Report generation (Jinja2, WeasyPrint)
├── api/                  # FastAPI application
├── cli/                  # CLI entry point (Typer)
├── engine/               # Go module root
│   ├── scanner/          # Disk scanning logic
│   ├── carver/           # File carving logic
│   ├── hasher/           # Hashing logic
│   └── proto/            # Generated Go protobuf code
├── contracts/            # Protocol Buffer definitions
├── tests/                # Unit and integration tests
├── docs/                 # Documentation
└── docker/               # Containerization configs
```
