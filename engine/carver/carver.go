package carver

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"

	pb "github.com/ismailtsdln/forenscope/engine/proto"
	"github.com/ismailtsdln/forenscope/engine/scanner" // Reuse signatures
)

type Carver struct {
	BlockSize int64
}

func NewCarver(blockSize int64) *Carver {
	if blockSize <= 0 {
		blockSize = 4096
	}
	return &Carver{BlockSize: blockSize}
}

// CarveFile attempts to recover files from a raw image based on headers.
// Note: This is a simplified "header-only" carver. A robust carver needs footers/length fields.
func (c *Carver) CarveFile(sourcePath string, outputDir string) (*pb.CarveResult, error) {
	f, err := os.Open(sourcePath)
	if err != nil {
		return &pb.CarveResult{Success: false, ErrorMessage: err.Error()}, nil
	}
	defer f.Close()

	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return &pb.CarveResult{Success: false, ErrorMessage: err.Error()}, nil
	}

	buffer := make([]byte, c.BlockSize)
	var offset int64 = 0
	var recoveredCount int64 = 0

	for {
		n, err := f.Read(buffer)
		if err != nil {
			break // EOF or error
		}
		if n == 0 {
			break
		}

		// Check buffer for signatures
		// Optimization: Only check the start of the block or scan entire block?
		// Real carvers scan byte-by-byte or at sector boundaries.
		// We will assume 512-byte alignment for common filesystems.
		// For simplicity/demo: Check ONLY the start of the block.

		sigName := scanner.MatchSignature(buffer[:32]) // Check first 32 bytes of block
		if sigName != "" {
			// Found a potential file start!
			log.Printf("Found %s at offset %d", sigName, offset)

			// Recover simple chunk (e.g. 1MB or until next header - minimal implementation)
			// In production, we'd look for a footer or parse the header for size.
			recoverName := fmt.Sprintf("%d_%s.recovered", offset, strings.ReplaceAll(sigName, "/", "_"))
			recoverPath := filepath.Join(outputDir, recoverName)

			// Save 1MB or remaining
			c.saveChunk(f, offset, recoverPath, 1024*1024)

			recoveredCount++

			// Reset cursor to next block (saveChunk moves it, we need to handle that)
			f.Seek(offset+c.BlockSize, 0)
		}

		offset += int64(n)
	}

	return &pb.CarveResult{
		Success:        true,
		FilesRecovered: recoveredCount,
	}, nil
}

// saveChunk saves a specific amount of data from the current file handle position.
func (c *Carver) saveChunk(reader *os.File, startOffset int64, outPath string, maxSize int64) {
	// Remember original pos
	current, _ := reader.Seek(0, 1)

	// Go to start
	reader.Seek(startOffset, 0)

	outFile, err := os.Create(outPath)
	if err != nil {
		log.Printf("Failed to create recovered file: %v", err)
		reader.Seek(current, 0) // Restore
		return
	}
	defer outFile.Close()

	// Copy
	// LimitReader to avoid reading whole disk
	// In real life, we read until EOF or next header
	io.CopyN(outFile, reader, maxSize)

	// Restore
	reader.Seek(current, 0)
}
