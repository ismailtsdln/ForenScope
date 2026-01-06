package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	pb "github.com/ismailtsdln/forenscope/engine/proto"
	"github.com/ismailtsdln/forenscope/engine/scanner"
)

var (
	port = flag.Int("port", 50051, "The server port")
)

type server struct {
	pb.UnimplementedEngineServiceServer
	scanner *scanner.Scanner
}

func (s *server) Scan(ctx context.Context, req *pb.ScanRequest) (*pb.ScanResult, error) {
	log.Printf("Received scan request for: %v [Type: %s]", req.SourcePath, req.ScanType)
	return s.scanner.ScanDir(req.SourcePath)
}

func (s *server) Hash(ctx context.Context, req *pb.HashRequest) (*pb.HashResult, error) {
	// TODO: Implement actual hashing logic
	log.Printf("Received hash request for: %v", req.FilePath)
	return &pb.HashResult{
		FilePath: req.FilePath,
		Hashes:   map[string]string{"sha256": "mock_hash_1234"},
	}, nil
}

func (s *server) Ping(ctx context.Context, req *pb.Empty) (*pb.Pong, error) {
	return &pb.Pong{
		Status:    "OK",
		Timestamp: time.Now().Unix(),
	}, nil
}

func main() {
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	// Initialize the scanner with a worker pool of 20
	// We pass a background context or a global app context if needed in the future
	scanEngine := scanner.NewScanner(20)
	defer scanEngine.Close()

	s := grpc.NewServer()
	pb.RegisterEngineServiceServer(s, &server{
		scanner: scanEngine,
	})

	// Register reflection service on gRPC server for debugging with grpcurl
	reflection.Register(s)

	// Graceful shutdown channel
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)

	go func() {
		log.Printf("Engine server listening at %v", lis.Addr())
		if err := s.Serve(lis); err != nil {
			log.Fatalf("failed to serve: %v", err)
		}
	}()

	<-stop
	log.Println("Shutting down Engine server...")
	s.GracefulStop()
	log.Println("Engine server stopped.")
}
