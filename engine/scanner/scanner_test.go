package scanner

import (
	"os"
	"path/filepath"
	"testing"
)

func TestMatchSignature(t *testing.T) {
	tests := []struct {
		name     string
		data     []byte
		expected string
	}{
		{"JPEG", []byte{0xFF, 0xD8, 0xFF, 0xE0}, "JPEG"},
		{"PNG", []byte{0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A}, "PNG"},
		{"PDF", []byte{0x25, 0x50, 0x44, 0x46, 0x2D}, "PDF"},
		{"Unknown", []byte{0x00, 0x01, 0x02}, ""},
		{"Short", []byte{0xFF}, ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			sig := MatchSignature(tt.data)
			got := ""
			if sig != nil {
				got = sig.Name
			}

			if got != tt.expected {
				t.Errorf("MatchSignature() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestNewScanner(t *testing.T) {
	s := NewScanner(1, nil)
	if s == nil {
		t.Error("NewScanner returned nil")
	}
	s.Close()
}

func TestScanDir_Integration(t *testing.T) {
	// Create temp dir with dummy file
	tmpDir, err := os.MkdirTemp("", "scan_test")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(tmpDir)

	// Create a fake JPEG
	jpegPath := filepath.Join(tmpDir, "test.jpg")
	err = os.WriteFile(jpegPath, []byte{0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46}, 0644)
	if err != nil {
		t.Fatal(err)
	}

	// Scan
	s := NewScanner(2, nil)
	defer s.Close()

	result, err := s.ScanDir(tmpDir)
	if err != nil {
		t.Fatalf("ScanDir failed: %v", err)
	}

	if !result.Success {
		t.Error("ScanResult.Success is false")
	}

	if result.FilesScanned != 1 {
		t.Errorf("Expected 1 file scanned, got %d", result.FilesScanned)
	}

	if len(result.Matches) != 1 {
		t.Errorf("Expected 1 match, got %d", len(result.Matches))
	} else {
		if result.Matches[0].SignatureName != "JPEG" {
			t.Errorf("Expected JPEG match, got %s", result.Matches[0].SignatureName)
		}
	}
}
