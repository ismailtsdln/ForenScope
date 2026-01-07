import os
import json
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Try import weasyprint
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logging.warning("WeasyPrint not installed. PDF generation disabled.")

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_json(self, data: dict, filename_prefix: str) -> str:
        """
        Generates a JSON report.
        """
        filename = f"{filename_prefix}.json"
        path = os.path.join(self.output_dir, filename)
        
        with open(path, "w") as f:
            json.dump(data, f, indent=4, default=str)
            
        return path

    def _render_html(self, data: dict) -> str:
        """
        Internal method to render HTML content string.
        """
        template = self.env.get_template("report.html")
        
        # Load CSS content to embed it directly (single file report)
        css_path = os.path.join(os.path.dirname(__file__), "templates", "style.css")
        with open(css_path, "r") as f:
            css_content = f.read()

        # Prepare Timeline Data from artifacts (interactive timeline)
        timeline_events = data.get("timeline_events", [])
        
        # Auto-populate timeline from artifacts if not provided
        if not timeline_events and "matches" in data:
            for idx, match in enumerate(data.get("matches", [])):
                ts = match.get("timestamp")
                if ts:
                    # Vis.js format: {id, content, start, type}
                    timeline_events.append({
                        "id": idx,
                        "content": f"{match.get('artifact_type', 'Evidence')} - {match.get('data', {}).get('value_name', 'Unknown')}",
                        "start": str(ts),
                        "type": "box"
                    })
        
        return template.render(
            css_content=css_content,
            job_id=data.get("job_id"),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            target_path=data.get("target_path"),
            files_scanned=data.get("files_scanned"),
            artifacts_count=len(data.get("matches", [])),
            matches=data.get("matches", []),
            yara_matches=data.get("yara_matches", []),
            timeline_events=timeline_events
        )

    def generate_html(self, data: dict, filename_prefix: str) -> str:
        """
        Generates an HTML report using Jinja2.
        """
        html_content = self._render_html(data)

        filename = f"{filename_prefix}.html"
        path = os.path.join(self.output_dir, filename)
        
        with open(path, "w") as f:
            f.write(html_content)
            
        return path

    def generate_pdf(self, data: dict, filename_prefix: str) -> str:
        """
        Generates a PDF report using WeasyPrint.
        """
        if not WEASYPRINT_AVAILABLE:
            logging.error("Cannot generate PDF: WeasyPrint missing.")
            return ""

        html_content = self._render_html(data)
        
        filename = f"{filename_prefix}.pdf"
        path = os.path.join(self.output_dir, filename)
        
        # WeasyPrint generation
        # Add print specific CSS if needed, or rely on style.css @media print
        HTML(string=html_content).write_pdf(path)
        
        return path
