import typer
from typing import Optional

app = typer.Typer(
    name="forenscope",
    help="Professional Forensic Orchestration Platform",
    add_completion=False,
)

@app.command()
def scan(
    image: str = typer.Option(..., "--image", "-i", help="Path to disk image or source"),
    fast: bool = typer.Option(False, "--fast", help="Enable fast mode (skip deep signature scan)"),
):
    """
    Start a forensic scan on a target image.
    """
    typer.echo(f"Starting scan on: {image} (Fast mode: {fast})")
    # TODO: Connect to Orchestrator -> gRPC Engine
    typer.echo("Scan initiated. Job ID: pending implementation")

@app.command()
def status(job_id: str):
    """
    Check the status of a running job.
    """
    typer.echo(f"Checking status for Job ID: {job_id}")

@app.command()
def version():
    """
    Show current version info.
    """
    typer.echo("ForenScope v0.1.0")

if __name__ == "__main__":
    app()
