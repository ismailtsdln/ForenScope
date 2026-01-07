package scanner

import (
	"context"
	"io"
	"io/fs"
	"log"
	"os"
	"path/filepath"
	"sync"
	"time"

	pb "github.com/ismailtsdln/forenscope/engine/proto"
	"github.com/ismailtsdln/forenscope/engine/worker"
)

// Scanner handles file system scanning logic.
type Scanner struct {
	pool        *worker.Pool
	yaraScanner *YaraScanner
}

// NewScanner creates a new Scanner with a worker pool and optional YARA scanner.
func NewScanner(workerCount int, y *YaraScanner) *Scanner {
	pool := worker.NewPool(workerCount)
	pool.Start()
	return &Scanner{pool: pool, yaraScanner: y}
}

// Close stops the scanner and its workers.
func (s *Scanner) Close() {
	s.pool.Stop()
}

// StreamWalk walks the directory and streams metadata to the server.
func (s *Scanner) StreamWalk(root string, stream pb.EngineService_WalkServer) error {
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			log.Printf("Error accessing path %q: %v\n", path, err)
			return nil // Don't abort walk on individual access error
		}

		info, err := d.Info()
		if err != nil {
			return nil
		}

		entry := &pb.WalkEntry{
			Path:         path,
			Size:         info.Size(),
			Mode:         int64(info.Mode()),
			ModifiedTime: info.ModTime().Unix(),
			IsDir:        d.IsDir(),
		}

		if err := stream.Send(entry); err != nil {
			return err
		}

		return nil
	})
	return err
}

// ScanDir walks the directory and submits file processing tasks to the worker pool.
func (s *Scanner) ScanDir(root string) (*pb.ScanResult, error) {
	// startTime := time.Now()
	var fileCount int64 = 0
	var mu sync.Mutex
	var foundItems []*pb.FoundItem
	var yaraMatches []*pb.YaraMatch

	// We use a WaitGroup to wait for all submitted tasks to finish
	var wg sync.WaitGroup

	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			log.Printf("Error accessing path %q: %v\n", path, err)
			return err
		}

		if !d.IsDir() {
			fileCount++
			wg.Add(1)

			// Submit task to pool
			s.pool.Submit(func(ctx context.Context) error {
				defer wg.Done()

				// 1. Signature Scan (Magic Bytes)
				f, err := os.Open(path)
				if err != nil {
					log.Printf("Warning: Failed to open %s for signature scan: %v", path, err)
					return nil // Continue scanning other files
				}
				defer f.Close()

				// Read first 32 bytes for magic number check
				buf := make([]byte, 32)
				_, err = io.ReadFull(f, buf)
				if err != nil && err != io.EOF && err != io.ErrUnexpectedEOF {
					log.Printf("Warning: Failed to read from %s: %v", path, err)
					return nil
				}

				sig := MatchSignature(buf)
				if sig != nil {
					mu.Lock()
					foundItems = append(foundItems, &pb.FoundItem{
						FilePath:      path,
						SignatureName: sig.Name, // Using Name from returned struct
						Offset:        0,
					})
					mu.Unlock()
				}

				// 2. YARA Scan (If Enabled)
				if s.yaraScanner != nil && s.yaraScanner.Enabled() {
					// Note: YARA scan might be heavy, running inside worker is good.
					// However, go-yara might require thread safety or lock?
					// Usually ScanFile is thread-safe if Rules are used (not Compiler).
					matches, err := s.yaraScanner.ScanFile(path)
					if err == nil && len(matches) > 0 {
						mu.Lock()
						yaraMatches = append(yaraMatches, matches...)
						mu.Unlock()
					}
				}

				return nil
			})
		}
		return nil
	})

	if err != nil {
		return &pb.ScanResult{
			Success:      false,
			ErrorMessage: err.Error(),
		}, nil
	}

	// Wait for all workers to finish
	wg.Wait()

	return &pb.ScanResult{
		JobId:        "job_" + time.Now().Format("20060102150405"),
		Success:      true,
		FilesScanned: fileCount,
		Matches:      foundItems,
		YaraMatches:  yaraMatches,
	}, nil
}
