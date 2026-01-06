import typer
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from orchestrator.client import EngineClient

app = typer.Typer(
    name="forenscope",
    help="Professional Forensic Orchestration Platform",
    add_completion=False,
)

@app.command()
def scan(
    image: str = typer.Option(..., "--image", "-i", help="Path to disk image or source"),
    fast: bool = typer.Option(False, "--fast", help="Enable fast mode (skip deep signature scan)"),
    engine_addr: str = typer.Option("localhost:50051", "--addr", help="Address of Go Engine"),
):
    """
    Start a forensic scan on a target image.
    """
    typer.echo(f"Starting scan on: {image} via {engine_addr}")
    
    client = EngineClient(target=engine_addr)
    try:
        typer.echo("Contacting engine...")
        result = client.scan(image, scan_type="quick" if fast else "full")
        if result.success:
            typer.echo(f"✅ Scan Complete. Files found: {result.files_found}")
            typer.echo(f"Job ID: {result.job_id}")
        else:
            typer.echo(f"❌ Scan Failed: {result.error_message}")
    except Exception as e:
        typer.echo(f"Error communicating with engine: {e}")

@app.command()
def ping(
    engine_addr: str = typer.Option("localhost:50051", "--addr", help="Address of Go Engine"),
):
    """
    Ping the engine.
    """
    client = EngineClient(target=engine_addr)
    response = client.ping()
    if response:
        typer.echo(f"Pong! Status: {response.status}")
    else:
        typer.echo("No response.")

if __name__ == "__main__":
    app()
