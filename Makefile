.PHONY: all proto build run-engine

all: proto build

proto:
	@echo "Generating Protobufs..."
	# Generate Python
	python -m grpc_tools.protoc -Icontracts --python_out=core/rpc --grpc_python_out=core/rpc contracts/engine.proto
	# Generate Go (assumes protoc-gen-go is in PATH given setup, or add explicitly)
	protoc --proto_path=contracts --go_out=engine/proto --go_opt=paths=source_relative --go-grpc_out=engine/proto --go-grpc_opt=paths=source_relative engine.proto

build:
	@echo "Building Go Engine..."
	cd engine && go mod tidy && go build -o ../bin/engine main.go

run-engine:
	@echo "Starting Go Engine..."
	./bin/engine

clean:
	@echo "Cleaning up..."
	rm -rf bin/*
	rm -rf reports/*
	rm -rf test_reports/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -f .coverage
	rm -rf htmlcov
	rm -f .DS_Store
	find . -name "*.pyc" -delete
	@echo "Done."
