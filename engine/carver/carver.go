package carver

import (
	"bytes"
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

// CarveFile attempts to recover files from a raw image based on headers and footers.
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

		// Check buffer for signatures (Headers)
		sig := scanner.MatchSignature(buffer[:32]) // Simple check at block start
		if sig != nil {
			log.Printf("Found Header %s at offset %d", sig.Name, offset)

			// Determine recovery strategy
			var sizeToRecover int64 = 0

			if len(sig.Footer) > 0 {
				// HEADER + FOOTER STRATEGY
				// Scan forward for footer until MaxFileSize
				foundSize, foundFooter := c.scanFooter(f, offset, sig.Footer, sig.MaxFileSize)
				if foundFooter {
					sizeToRecover = foundSize
				} else {
					// Footer not found within limit, truncate to max size or just fail?
					// Implementation choice: Recover up to defined 'reasonable' max size anyway (e.g. 1MB default or MaxFileSize)
					// Let's cap at 5MB if footer lost, to avoid junk.
					sizeToRecover = 5 * 1024 * 1024
					if sizeToRecover > sig.MaxFileSize {
						sizeToRecover = sig.MaxFileSize
					}
				}
			} else {
				// HEADER ONLY STRATEGY
				// Fallback to fixed size (e.g. 1MB or signatures default max)
				sizeToRecover = 1 * 1024 * 1024
			}

			recoverName := fmt.Sprintf("%d_%s.recovered", offset, strings.ReplaceAll(sig.Name, "/", "_"))
			recoverPath := filepath.Join(outputDir, recoverName)

			c.saveChunk(f, offset, recoverPath, sizeToRecover)
			recoveredCount++

			// Should we jump ahead?
			// Yes, jump by sizeToRecover to avoid carving inside the file we just recovered (usually)
			// But careful about alignment.
			// Simpler approach: Just continue scanning block by block.
			// If we jump, we might miss embedded files (though rarely desired in simple carving).
			// Let's jump to avoid duplicates.

			// We need to re-seek because saveChunk restored the position to 'offset' + maybe read?
			// saveChunk restores to original handle position (start of next block usually).
			// If we want to skip the carved file:
			// newPos := offset + sizeToRecover
			// f.Seek(newPos, 0)
			// offset = newPos
			// continue

			// For safety (files might be fragmented), standard simple carving often continues linearly.
			// But for header-footer, skipping is better.
			// Let's skip.

			newPos := offset + sizeToRecover
			// Align to block size?
			remainder := newPos % c.BlockSize
			if remainder != 0 {
				newPos += (c.BlockSize - remainder)
			}

			_, err = f.Seek(newPos, 0)
			if err != nil {
				break
			}
			offset = newPos
			continue
		}

		offset += int64(n)
	}

	return &pb.CarveResult{
		Success:        true,
		FilesRecovered: recoveredCount,
	}, nil
}

// scanFooter searches for a footer starting from offset up to maxBytes.
// Returns size (including footer) and true if found.
func (c *Carver) scanFooter(reader *os.File, startOffset int64, footer []byte, maxBytes int64) (int64, bool) {
	// Save pos
	current, _ := reader.Seek(0, 1)
	defer reader.Seek(current, 0)

	reader.Seek(startOffset, 0)

	bufSize := 4096
	buf := make([]byte, bufSize)
	var scanned int64 = 0

	// Create a window for footer matching across blocks
	// Not fully implemented for cross-block split footer for simplicity here,
	// but standard block scanning catches most.

	for scanned < maxBytes {
		n, err := reader.Read(buf)
		if n == 0 || err != nil {
			break
		}

		// Search in buffer
		idx := bytes.Index(buf[:n], footer)
		if idx != -1 {
			// Found it!
			foundSize := scanned + int64(idx) + int64(len(footer))
			return foundSize, true
		}

		scanned += int64(n)
	}

	return 0, false
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

	io.CopyN(outFile, reader, maxSize)

	// Restore
	reader.Seek(current, 0)
}
