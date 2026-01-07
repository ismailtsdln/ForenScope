package hasher

import (
	"os"
	"path/filepath"
	"testing"
)

func TestHashFile_SHA256(t *testing.T) {
	// Create temp file
	tmpDir, err := os.MkdirTemp("", "hash_test")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(tmpDir)

	testPath := filepath.Join(tmpDir, "test.txt")
	testData := []byte("Hello, ForenScope!")

	err = os.WriteFile(testPath, testData, 0644)
	if err != nil {
		t.Fatal(err)
	}

	// Hash the file
	result, err := CalculateHashes(testPath, []string{"sha256"})
	if err != nil {
		t.Fatalf("CalculateHashes failed: %v", err)
	}

	if result.FilePath != testPath {
		t.Errorf("Expected path %s, got %s", testPath, result.FilePath)
	}

	if len(result.Hashes) != 1 {
		t.Fatalf("Expected 1 hash, got %d", len(result.Hashes))
	}

	// Get SHA256 hash from map
	hashValue, ok := result.Hashes["sha256"]
	if !ok {
		t.Error("SHA256 hash not found")
	}

	// SHA256 hash is 64 characters in hex
	if len(hashValue) != 64 {
		t.Errorf("Expected hash length 64, got %d", len(hashValue))
	}

	// Check it's not empty
	if hashValue == "" {
		t.Error("Hash value is empty")
	}
}

func TestHashFile_MultipleAlgorithms(t *testing.T) {
	// Create temp file
	tmpDir, err := os.MkdirTemp("", "hash_test")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(tmpDir)

	testPath := filepath.Join(tmpDir, "test.txt")
	testData := []byte("Test data for multiple algorithms")

	err = os.WriteFile(testPath, testData, 0644)
	if err != nil {
		t.Fatal(err)
	}

	// Hash with multiple algorithms (only sha256, md5 supported currently)
	result, err := CalculateHashes(testPath, []string{"sha256", "md5"})
	if err != nil {
		t.Fatalf("CalculateHashes failed: %v", err)
	}

	if len(result.Hashes) != 2 {
		t.Fatalf("Expected 2 hashes, got %d", len(result.Hashes))
	}

	// Verify all algorithms are present
	_, hasSha256 := result.Hashes["sha256"]
	_, hasMd5 := result.Hashes["md5"]

	if !hasSha256 || !hasMd5 {
		t.Error("Not all algorithms were computed")
	}

	// Verify hash lengths
	sha256Hash := result.Hashes["sha256"]
	md5Hash := result.Hashes["md5"]

	if len(sha256Hash) != 64 {
		t.Errorf("SHA256 hash length should be 64, got %d", len(sha256Hash))
	}

	if len(md5Hash) != 32 {
		t.Errorf("MD5 hash length should be 32, got %d", len(md5Hash))
	}
}

func TestHashFile_NonExistentFile(t *testing.T) {
	_, err := CalculateHashes("/nonexistent/file.txt", []string{"sha256"})
	if err == nil {
		t.Error("Expected error for non-existent file")
	}
}

func TestHashFile_EmptyFile(t *testing.T) {
	// Create temp empty file
	tmpDir, err := os.MkdirTemp("", "hash_test")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(tmpDir)

	testPath := filepath.Join(tmpDir, "empty.txt")
	err = os.WriteFile(testPath, []byte{}, 0644)
	if err != nil {
		t.Fatal(err)
	}

	result, err := CalculateHashes(testPath, []string{"sha256"})
	if err != nil {
		t.Fatalf("CalculateHashes failed: %v", err)
	}

	if len(result.Hashes) != 1 {
		t.Fatalf("Expected 1 hash, got %d", len(result.Hashes))
	}

	// SHA256 of empty string is: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
	expectedEmptyHash := "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
	sha256Hash := result.Hashes["sha256"]
	if sha256Hash != expectedEmptyHash {
		t.Errorf("Expected hash %s, got %s", expectedEmptyHash, sha256Hash)
	}
}

func TestHashFile_InvalidAlgorithm(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "hash_test")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(tmpDir)

	testPath := filepath.Join(tmpDir, "test.txt")
	err = os.WriteFile(testPath, []byte("test"), 0644)
	if err != nil {
		t.Fatal(err)
	}

	// Request invalid algorithm
	result, err := CalculateHashes(testPath, []string{"invalid_algo"})

	// Should either error or skip the invalid algorithm
	// Depending on implementation, adjust this test
	if err != nil {
		// If implementation returns error for invalid algorithm
		return
	}

	// If implementation skips invalid algorithms
	if len(result.Hashes) != 0 {
		t.Error("Should not compute hashes for invalid algorithm")
	}
}
