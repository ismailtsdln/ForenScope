import sys
import os
import logging
import grpc

# Add core/rpc to path so generated files can import each other
# This is a runtime hack to handle protobuf's generated imports which are not relative by default
RPC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "rpc")
if RPC_DIR not in sys.path:
    sys.path.append(RPC_DIR)

# Now we can safely import the generated PB modules
# We import them within the class or just here, but we reference them carefully.
# Note: The generated code uses 'import engine_pb2', so adding RPC_DIR to sys.path makes that work.

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
            # Create a failure result
            res = engine_pb2.ScanResult()
            res.success = False
            res.error_message = str(e)
            return res

    def ping(self):
        try:
            return self.stub.Ping(engine_pb2.Empty())
        except grpc.RpcError as e:
            logging.error(f"Ping failed: {e}")
            return None
