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

	"github.com/ismailtsdln/forenscope/engine/carver"
	"github.com/ismailtsdln/forenscope/engine/hasher"
	pb "github.com/ismailtsdln/forenscope/engine/proto"
	"github.com/ismailtsdln/forenscope/engine/scanner"
)

var (
	port = flag.Int("port", 50051, "The server port")
)

type server struct {
	pb.UnimplementedEngineServiceServer
	scanner *scanner.Scanner
	carver  *carver.Carver
}

func (s *server) Scan(ctx context.Context, req *pb.ScanRequest) (*pb.ScanResult, error) {
	log.Printf("Received scan request for: %v [Type: %s]", req.SourcePath, req.ScanType)
	return s.scanner.ScanDir(req.SourcePath)
}

func (s *server) Carve(ctx context.Context, req *pb.CarveRequest) (*pb.CarveResult, error) {
	log.Printf("Received carve request for: %v (Target: %v)", req.SourcePath, req.OutputDir)
	return s.carver.CarveFile(req.SourcePath, req.OutputDir)
}

func (s *server) Hash(ctx context.Context, req *pb.HashRequest) (*pb.HashResult, error) {
	log.Printf("Received hash request for: %v (Algos: %v)", req.FilePath, req.Algorithms)
	return hasher.CalculateHashes(req.FilePath, req.Algorithms)
}

func (s *server) Walk(req *pb.WalkRequest, stream pb.EngineService_WalkServer) error {
	log.Printf("Received walk request for: %v", req.RootPath)
	return s.scanner.StreamWalk(req.RootPath, stream)
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

	// Initialize components
	scanEngine := scanner.NewScanner(20)
	carveEngine := carver.NewCarver(4096)
	defer scanEngine.Close()

	s := grpc.NewServer()
	pb.RegisterEngineServiceServer(s, &server{
		scanner: scanEngine,
		carver:  carveEngine,
	})

	reflection.Register(s)

	// Graceful shutdown
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
