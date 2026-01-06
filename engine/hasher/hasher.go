package hasher

import (
	"crypto/md5"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"

	pb "github.com/ismailtsdln/forenscope/engine/proto"
)

// CalculateHashes computes the requested hashes for a given file.
// It uses a MultiWriter to calculate multiple hashes in a single pass.
func CalculateHashes(filePath string, algos []string) (*pb.HashResult, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	// Prepare hashers
	writers := []io.Writer{}
	resultMap := make(map[string]interface{}) // temporary map to hold hash interfaces

	// By default, if algos is empty, do SHA256
	if len(algos) == 0 {
		algos = []string{"sha256"}
	}

	for _, algo := range algos {
		switch algo {
		case "md5":
			h := md5.New()
			writers = append(writers, h)
			resultMap["md5"] = h
		case "sha256":
			h := sha256.New()
			writers = append(writers, h)
			resultMap["sha256"] = h
		default:
			// Ignore unknown or handle error
			continue
		}
	}

	if len(writers) == 0 {
		return &pb.HashResult{
			FilePath: filePath,
			Hashes:   make(map[string]string),
		}, nil
	}

	// Create a MultiWriter to write to all hashers at once
	multiWriter := io.MultiWriter(writers...)

	// Stream the file
	if _, err := io.Copy(multiWriter, f); err != nil {
		return nil, fmt.Errorf("failed to read file: %v", err)
	}

	// Collect results
	finalHashes := make(map[string]string)
	for algo, h := range resultMap {
		var sum []byte
		if hasher, ok := h.(interface{ Sum([]byte) []byte }); ok {
			sum = hasher.Sum(nil)
			finalHashes[algo] = hex.EncodeToString(sum)
		}
	}

	return &pb.HashResult{
		FilePath: filePath,
		Hashes:   finalHashes,
	}, nil
}
