//go:build yara

package scanner

import (
	"log"
	"os"

	"github.com/hillu/go-yara/v4"
	pb "github.com/ismailtsdln/forenscope/engine/proto"
)

// YaraScanner uses libyara to scan files.
type YaraScanner struct {
	rules   *yara.Rules
	enabled bool
}

func NewYaraScanner(rulePath string) (*YaraScanner, error) {
	if rulePath == "" {
		return &YaraScanner{enabled: false}, nil
	}

	cmp, err := yara.NewCompiler()
	if err != nil {
		return nil, err
	}

	f, err := os.Open(rulePath)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	if err := cmp.AddFile(f, "default"); err != nil {
		return nil, err
	}

	rules, err := cmp.GetRules()
	if err != nil {
		return nil, err
	}

	return &YaraScanner{rules: rules, enabled: true}, nil
}

func (y *YaraScanner) ScanFile(path string) ([]*pb.YaraMatch, error) {
	if !y.enabled {
		return []*pb.YaraMatch{}, nil
	}

	var matches []yara.MatchRule
	err := y.rules.ScanFile(path, 0, 0, &matches)
	if err != nil {
		log.Printf("YARA scan error for %s: %v", path, err)
		return nil, err
	}

	var pbMatches []*pb.YaraMatch
	for _, m := range matches {
		var tags []string
		for _, t := range m.Tags {
			tags = append(tags, t)
		}

		pbMatches = append(pbMatches, &pb.YaraMatch{
			FilePath: path,
			RuleName: m.Rule,
			Tags:     tags,
		})
	}

	return pbMatches, nil
}

func (y *YaraScanner) Enabled() bool {
	return y.enabled
}
