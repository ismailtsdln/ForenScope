//go:build !yara

package scanner

import (
	pb "github.com/ismailtsdln/forenscope/engine/proto"
)

// YaraScanner is a stub when YARA is disabled.
type YaraScanner struct{}

func NewYaraScanner(rulePath string) (*YaraScanner, error) {
	return &YaraScanner{}, nil
}

func (y *YaraScanner) ScanFile(path string) ([]*pb.YaraMatch, error) {
	// Return empty if YARA is not enabled
	return []*pb.YaraMatch{}, nil
}

func (y *YaraScanner) Enabled() bool {
	return false
}
