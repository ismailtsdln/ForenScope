import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

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

    def generate_html(self, data: dict, filename_prefix: str) -> str:
        """
        Generates an HTML report using Jinja2.
        """
        template = self.env.get_template("report.html")
        
        # Load CSS content to embed it directly (single file report)
        css_path = os.path.join(os.path.dirname(__file__), "templates", "style.css")
        with open(css_path, "r") as f:
            css_content = f.read()

        html_content = template.render(
            css_content=css_content,
            job_id=data.get("job_id"),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            target_path=data.get("target_path"),
            files_scanned=data.get("files_scanned"),
            artifacts_count=len(data.get("matches", [])),
            matches=data.get("matches", [])
        )

        filename = f"{filename_prefix}.html"
        path = os.path.join(self.output_dir, filename)
        
        with open(path, "w") as f:
            f.write(html_content)
            
        return path
