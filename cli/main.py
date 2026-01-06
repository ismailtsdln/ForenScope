import typer
import sys
import os
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Ensure project root is in path
sys.path.append(os.getcwd())

from orchestrator.client import EngineClient
from reporting.generator import ReportGenerator

app = typer.Typer(
    name="forenscope",
    help="Professional Forensic Orchestration Platform",
    add_completion=False,
)

console = Console()

def print_banner():
    banner = """
    [bold cyan]ForenScope[/bold cyan] [bold white]v0.1.0[/bold white]
    [dim]Hybrid Digital Forensics Intelligence Platform[/dim]
    """
    console.print(Panel(banner, border_style="cyan"))

@app.command()
def scan(
    image: str = typer.Option(..., "--image", "-i", help="Path to disk image or source"),
    fast: bool = typer.Option(False, "--fast", help="Enable fast mode (skip deep signature scan)"),
    engine_addr: str = typer.Option("localhost:50051", "--addr", help="Address of Go Engine"),
    report: bool = typer.Option(False, "--report", "-r", help="Generate HTML & JSON reports"),
):
    """
    Start a forensic scan on a target image (Signature Analysis).
    """
    print_banner()
    console.print("[bold yellow]⚡ Starting Forensic Scan[/bold yellow]")
    console.print(f"   Target: [blue]{image}[/blue]")
    console.print(f"   Engine: [dim]{engine_addr}[/dim]")
    console.print(f"   Mode:   {'[red]FAST[/red]' if fast else '[green]DEEP[/green]'}")
    
    if report:
        console.print("   Report: [green]ENABLED[/green]")
    print()

    client = EngineClient(target=engine_addr)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="[cyan]Connecting to Engine...[/cyan]", total=None)
        
        time.sleep(0.5) 
        
        progress.update(task, description="[cyan]Scanning file system...[/cyan]")
        result = client.scan(image, scan_type="quick" if fast else "full")

    if result.success:
        console.print("[bold green]✅ Scan Complete Successfully![/bold green]")
        
        # Summary Table
        table = Table(title="Scan Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim")
        table.add_column("Value", style="bold")
        
        table.add_row("Job ID", result.job_id)
        table.add_row("Files Scanned", str(result.files_scanned))
        table.add_row("Artifacts Found", str(len(result.matches)))
        
        console.print(table)
        print()

        # Artifacts Table logic ... (omitted for brevity, keeping existing CLI look)
        if len(result.matches) > 0:
            console.print("[bold red]⚠️  Detected Suspicious / Known Artifacts:[/bold red]")
            res_table = Table(show_header=True, header_style="bold red")
            res_table.add_column("Signature", style="cyan")
            res_table.add_column("File Path", style="white")
            
            for item in result.matches:
                res_table.add_row(item.signature_name, item.file_path)
            
            console.print(res_table)
        else:
            console.print("[green]✅ No specific threat signatures matched.[/green]")

        # Report Generation
        if report:
            console.print("\n[bold yellow]📄 Generating Reports...[/bold yellow]")
            generator = ReportGenerator(output_dir="reports")
            
            # Convert protobuf result to dict
            report_data = {
                "job_id": result.job_id,
                "target_path": image,
                "files_scanned": result.files_scanned,
                "matches": [
                    {
                        "signature_name": m.signature_name,
                        "file_path": m.file_path,
                        "offset": m.offset
                    } for m in result.matches
                ]
            }
            
            json_path = generator.generate_json(report_data, result.job_id)
            html_path = generator.generate_html(report_data, result.job_id)
            
            console.print(f"   JSON: [link={json_path}]{json_path}[/link]")
            console.print(f"   HTML: [link={html_path}]{html_path}[/link]")
            
    else:
        console.print("[bold red]❌ Scan Failed![/bold red]")
        console.print(Panel(f"Error: {result.error_message}", title="Engine Error", border_style="red"))

@app.command()
def carve(
    image: str = typer.Option(..., "--image", "-i", help="Path to raw disk image"),
    output: str = typer.Option(..., "--output", "-o", help="Directory to save recovered files"),
    engine_addr: str = typer.Option("localhost:50051", "--addr", help="Address of Go Engine"),
):
    """
    Start a file carving task to recover deleted files based on headers.
    """
    print_banner()
    console.print("[bold yellow]🧬 Starting File Carving Operation[/bold yellow]")
    console.print(f"   Source: [blue]{image}[/blue]")
    console.print(f"   Output: [blue]{output}[/blue]")
    print()
    
    client = EngineClient(target=engine_addr)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[magenta]Carving sectors...[/magenta]", total=None)
        result = client.carve(image, output_dir=output)
    
    if result.success:
        console.print("[bold green]✅ Carving Complete![/bold green]")
        console.print(f"Files Recovered: [bold cyan]{result.files_recovered}[/bold cyan]")
        console.print(f"Check output directory: [underline]{output}[/underline]")
    else:
        console.print("[bold red]❌ Carving Failed![/bold red]")
        console.print(f"Error: {result.error_message}")

@app.command()
def hash(
    file: str = typer.Option(..., "--file", "-f", help="Path to file to hash"),
    engine_addr: str = typer.Option("localhost:50051", "--addr", help="Address of Go Engine"),
):
    """
    Calculate SHA256/MD5 hashes of a file.
    """
    print_banner()
    console.print("[bold yellow]🔢 Calculating File Hashes[/bold yellow]")
    console.print(f"   File: [blue]{file}[/blue]")
    print()
    
    client = EngineClient(target=engine_addr)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[cyan]Streaming file content...[/cyan]", total=None)
        # Defaulting to both algorithms
        result = client.hash_file(file, algorithms=["md5", "sha256"])
        
    if result:
        console.print("[bold green]✅ Hashing Complete![/bold green]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Hash Value", style="green")
        
        for algo, val in result.hashes.items():
            table.add_row(algo.upper(), val)
            
        console.print(table)
    else:
        console.print("[bold red]❌ Hashing Failed![/bold red]")

@app.command()
def ping(
    engine_addr: str = typer.Option("localhost:50051", "--addr", help="Address of Go Engine"),
):
    """
    Check connectivity to the Go Engine.
    """
    try:
        client = EngineClient(target=engine_addr)
        start = time.time()
        response = client.ping()
        duration = (time.time() - start) * 1000
        
        if response and response.status == "OK":
            console.print("[bold green]Connected to ForenScope Engine[/bold green]")
            console.print("Status: [green]ONLINE[/green] 🟢")
            console.print(f"Latency: [cyan]{duration:.2f}ms[/cyan]")
        else:
            console.print("[bold red]Engine Unreachable or Status Error[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Connection Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
