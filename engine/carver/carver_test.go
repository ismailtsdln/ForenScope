package carver

import (
	"os"
	"path/filepath"
	"testing"
)

func TestNewCarver(t *testing.T) {
	c := NewCarver(4096)
	if c == nil {
		t.Error("NewCarver returned nil")
	}
	if c.BlockSize != 4096 {
		t.Errorf("Expected BlockSize 4096, got %d", c.BlockSize)
	}

	// Test default block size
	c2 := NewCarver(0)
	if c2.BlockSize != 4096 {
		t.Errorf("Expected default BlockSize 4096, got %d", c2.BlockSize)
	}
}

func TestCarveFile_EmptyImage(t *testing.T) {
	// Create temp dir
	tmpDir, err := os.MkdirTemp("", "carve_test")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(tmpDir)

	// Create empty image file
	imgPath := filepath.Join(tmpDir, "empty.img")
	err = os.WriteFile(imgPath, []byte{}, 0644)
	if err != nil {
		t.Fatal(err)
	}

	outputDir := filepath.Join(tmpDir, "output")

	c := NewCarver(4096)
	result, err := c.CarveFile(imgPath, outputDir)
	if err != nil {
		t.Fatalf("CarveFile failed: %v", err)
	}

	if !result.Success {
		t.Error("Expected success for empty image")
	}

	if result.FilesRecovered != 0 {
		t.Errorf("Expected 0 files recovered, got %d", result.FilesRecovered)
	}
}

func TestCarveFile_WithJPEG(t *testing.T) {
	// Create temp dir
	tmpDir, err := os.MkdirTemp("", "carve_test")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(tmpDir)

	// Create image with JPEG header
	imgPath := filepath.Join(tmpDir, "disk.img")

	// JPEG header: FF D8 FF E0
	jpegData := []byte{
		0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00,
		// Add some padding
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	}

	// Write image with JPEG at block start (offset 0) for block-based carver
	imageData := make([]byte, 8192)
	copy(imageData, jpegData)

	err = os.WriteFile(imgPath, imageData, 0644)
	if err != nil {
		t.Fatal(err)
	}

	outputDir := filepath.Join(tmpDir, "output")

	c := NewCarver(4096)
	result, err := c.CarveFile(imgPath, outputDir)
	if err != nil {
		t.Fatalf("CarveFile failed: %v", err)
	}

	if !result.Success {
		t.Error("Expected success")
	}

	// Should find at least one file (the JPEG)
	if result.FilesRecovered < 1 {
		t.Errorf("Expected at least 1 file recovered, got %d", result.FilesRecovered)
	}

	// Check if output directory was created
	if _, err := os.Stat(outputDir); os.IsNotExist(err) {
		t.Error("Output directory was not created")
	}
}

func TestCarveFile_NonExistentFile(t *testing.T) {
	c := NewCarver(4096)

	result, _ := c.CarveFile("/nonexistent/file.img", "/tmp/output")

	// Should handle error gracefully
	if result == nil {
		t.Error("Expected non-nil result")
	}

	if result.Success {
		t.Error("Expected failure for non-existent file")
	}
}

func TestScanFooter(t *testing.T) {
	// Create temp file with footer
	tmpDir, err := os.MkdirTemp("", "footer_test")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(tmpDir)

	testPath := filepath.Join(tmpDir, "test.dat")

	// Create data with a footer
	footer := []byte{0xFF, 0xD9} // JPEG footer
	data := make([]byte, 1024)
	copy(data[512:], footer)

	err = os.WriteFile(testPath, data, 0644)
	if err != nil {
		t.Fatal(err)
	}

	f, err := os.Open(testPath)
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()

	c := NewCarver(4096)
	size, found := c.scanFooter(f, 0, footer, 1024)

	if !found {
		t.Error("Expected to find footer")
	}

	if size != int64(512+len(footer)) {
		t.Errorf("Expected size %d, got %d", 512+len(footer), size)
	}
}
