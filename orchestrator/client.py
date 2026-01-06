import sys
import os
import logging
import grpc

# Add core/rpc to path so generated files can import each other
RPC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "rpc")
if RPC_DIR not in sys.path:
    sys.path.append(RPC_DIR)

import engine_pb2
import engine_pb2_grpc

class EngineClient:
    def __init__(self, target="localhost:50051"):
        self.channel = grpc.insecure_channel(target)
        self.stub = engine_pb2_grpc.EngineServiceStub(self.channel)

    def scan(self, path: str, scan_type: str = "full") -> engine_pb2.ScanResult:
        """
        Trigger a scan on the Go engine.
        """
        request = engine_pb2.ScanRequest(
            source_path=path,
            scan_type=scan_type
        )
        try:
            logging.info(f"Sending Scan request for {path}")
            return self.stub.Scan(request)
        except grpc.RpcError as e:
            logging.error(f"RPC failed: {e}")
            res = engine_pb2.ScanResult()
            res.success = False
            res.error_message = str(e)
            return res

    def carve(self, path: str, output_dir: str) -> engine_pb2.CarveResult:
        """
        Trigger a file carving task on the Go engine.
        """
        request = engine_pb2.CarveRequest(
            source_path=path,
            output_dir=output_dir,
            block_size=4096
        )
        try:
            logging.info(f"Sending Carve request for {path} -> {output_dir}")
            return self.stub.Carve(request)
        except grpc.RpcError as e:
            logging.error(f"RPC failed: {e}")
            res = engine_pb2.CarveResult()
            res.success = False
            res.error_message = str(e)
            return res

    def hash_file(self, path: str, algorithms: list[str] = None) -> engine_pb2.HashResult:
        """
        Trigger a file hash calculation on the Go engine.
        """
        if algorithms is None:
            algorithms = ["sha256"]
            
        request = engine_pb2.HashRequest(
            file_path=path,
            algorithms=algorithms
        )
        try:
            logging.info(f"Sending Hash request for {path}")
            return self.stub.Hash(request)
        except grpc.RpcError as e:
            logging.error(f"RPC failed: {e}")
            return None

    def walk(self, path: str):
        """
        Stream file metadata from the Go engine (Generator).
        """
        request = engine_pb2.WalkRequest(root_path=path)
        try:
            return self.stub.Walk(request)
        except grpc.RpcError as e:
            logging.error(f"Walk failed: {e}")
            return None

    def ping(self):
        try:
            return self.stub.Ping(engine_pb2.Empty())
        except grpc.RpcError as e:
            logging.error(f"Ping failed: {e}")
            return None
