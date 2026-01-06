package scanner

import (
	"bytes"
)

// Signature represents a file signature (magic bytes).
type Signature struct {
	Name   string
	Bytes  []byte
	Offset int64 // Usually 0
}

// Common Signatures
var DefaultSignatures = []Signature{
	{Name: "JPEG", Bytes: []byte{0xFF, 0xD8, 0xFF}, Offset: 0},
	{Name: "PNG", Bytes: []byte{0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A}, Offset: 0},
	{Name: "PDF", Bytes: []byte{0x25, 0x50, 0x44, 0x46}, Offset: 0},
	{Name: "ZIP/Jar/Docx", Bytes: []byte{0x50, 0x4B, 0x03, 0x04}, Offset: 0},
	{Name: "ELF", Bytes: []byte{0x7F, 0x45, 0x4C, 0x46}, Offset: 0},
	{Name: "Mach-O (64-bit)", Bytes: []byte{0xCF, 0xFA, 0xED, 0xFE}, Offset: 0},
}

// MatchSignature checks if data matches any known signature.
// Returns the name of the signature if found, or empty string.
func MatchSignature(data []byte) string {
	for _, sig := range DefaultSignatures {
		if int64(len(data)) > sig.Offset+int64(len(sig.Bytes)) {
			if bytes.Equal(data[sig.Offset:sig.Offset+int64(len(sig.Bytes))], sig.Bytes) {
				return sig.Name
			}
		}
	}
	return ""
}
