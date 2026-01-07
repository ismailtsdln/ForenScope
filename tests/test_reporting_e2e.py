import os
import os
from reporting.generator import ReportGenerator
from datetime import datetime

def test_generate_reports_e2e():
    generator = ReportGenerator(output_dir="test_reports")
    
    # Sample data mimicking a real scan result
    data = {
        "job_id": "test-job-123",
        "target_path": "/Users/test/evidence.ad1",
        "files_scanned": 1500,
        "matches": [
            {
                "artifact_type": "Registry Run Key",
                "signature_name": "MALICIOUS_RUN_KEY",
                "file_path": "C:\\Windows\\System32\\config\\SOFTWARE",
                "offset": 512,
                "timestamp": datetime(2026, 1, 7, 10, 0, 0),
                "data": {"value_name": "Updater", "value_data": "evil.exe"}
            },
            {
                "artifact_type": "Browser History",
                "signature_name": "SUSPICIOUS_DOMAIN",
                "file_path": "C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History",
                "offset": 1024,
                "timestamp": datetime(2026, 1, 7, 10, 30, 0),
                "data": {"value_name": "Download", "value_data": "http://evil.com/payload"}
            }
        ],
        "yara_matches": [
            {
                "rule_name": "CobaltStrike_Beacon",
                "tags": ["malware", "c2"],
                "file_path": "/tmp/recovered_carved_1.exe"
            }
        ]
    }
    
    # 1. Test JSON Generation
    json_path = generator.generate_json(data, "test_report")
    assert os.path.exists(json_path)
    
    # 2. Test HTML Generation (Timeline check)
    html_path = generator.generate_html(data, "test_report")
    assert os.path.exists(html_path)
    with open(html_path, "r") as f:
        content = f.read()
        assert "MALICIOUS_RUN_KEY" in content
        assert "vis.Timeline" in content
        assert "Updater" in content
        
    # 3. Test PDF Generation (Optional, might skip if weasyprint fails)
    pdf_path = generator.generate_pdf(data, "test_report")
    if pdf_path:
        assert os.path.exists(pdf_path)
        print(f"PDF successfully generated at: {pdf_path}")
    else:
        print("PDF generation skipped (WeasyPrint not available)")

if __name__ == "__main__":
    test_generate_reports_e2e()
