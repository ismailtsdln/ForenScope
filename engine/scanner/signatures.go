package scanner

import (
	"bytes"
)

// Signature represents a file signature (magic bytes).
type Signature struct {
	Name        string
	Bytes       []byte
	Uncommon    bool
	Footer      []byte // Optional footer for scraping
	MaxFileSize int64  // Max reasonable size to scan for footer
}

// Common Signatures
var DefaultSignatures = []Signature{
	{
		Name:        "JPEG",
		Bytes:       []byte{0xFF, 0xD8, 0xFF},
		Footer:      []byte{0xFF, 0xD9},
		MaxFileSize: 20 * 1024 * 1024, // 20MB
	},
	{
		Name:        "PNG",
		Bytes:       []byte{0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A},
		Footer:      []byte{0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82},
		MaxFileSize: 50 * 1024 * 1024,
	},
	{
		Name:  "PDF",
		Bytes: []byte{0x25, 0x50, 0x44, 0x46},
		// PDF footer is not always strict EOF, usually %%EOF, but often followed by junk.
		// We'll simplistic "%%EOF" match but it might be flaky in raw streams.
		Footer:      []byte{0x25, 0x25, 0x45, 0x4F, 0x46},
		MaxFileSize: 100 * 1024 * 1024,
	},
	{
		Name:        "ZIP/Jar/Docx",
		Bytes:       []byte{0x50, 0x4B, 0x03, 0x04},
		Footer:      []byte{0x50, 0x4B, 0x05, 0x06}, // End of central directory record
		MaxFileSize: 500 * 1024 * 1024,
	},
	{Name: "ELF", Bytes: []byte{0x7F, 0x45, 0x4C, 0x46}},
	{Name: "Mach-O (64-bit)", Bytes: []byte{0xCF, 0xFA, 0xED, 0xFE}},
}

// MatchSignature checks if data matches any known signature.
// Returns the signature object if found, or nil.
func MatchSignature(data []byte) *Signature {
	for _, sig := range DefaultSignatures {
		if int64(len(data)) >= int64(len(sig.Bytes)) {
			if bytes.Equal(data[:len(sig.Bytes)], sig.Bytes) {
				return &sig
			}
		}
	}
	return nil
}
