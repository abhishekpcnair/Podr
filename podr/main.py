"""Main CLI module for Pod Reaper."""

import sys
from typing import Optional

import typer
from typer import Option

from .k8s_client import get_k8s_client
from .cleaner import find_and_process_pods
from .job_generator import generate_cron_job_yaml

app = typer.Typer(
    name="podr",
    help="A CLI tool for cleaning up Kubernetes pods in specific states",
    add_completion=False,
)

VALID_PHASES = ["Succeeded", "Failed", "Terminated"]

def validate_phase(phase: str) -> str:
    """Validate the pod phase argument."""
    if phase not in VALID_PHASES:
        typer.echo(f"Error: Invalid phase '{phase}'. Must be one of: {', '.join(VALID_PHASES)}")
        sys.exit(1)
    return phase

@app.command()
def clean(
    state: str = typer.Argument(
        ...,
        help="Pod phase to clean up (Succeeded, Failed, or Terminated)",
        callback=validate_phase,
    ),
    namespace: Optional[str] = Option(
        None,
        "-n",
        "--namespace",
        help="Namespace to clean pods from (defaults to current context namespace)",
    ),
    all_namespaces: bool = Option(
        False,
        "-A",
        "--all-namespaces",
        help="Clean pods across all namespaces",
    ),
    interval: Optional[int] = Option(
        None,
        "-t",
        "--interval",
        help="Generate a CronJob that runs every N seconds",
        min=1,
    ),
    output_yaml: bool = Option(
        False,
        "-o",
        "--output",
        help="Output Kubernetes Job/CronJob YAML instead of performing cleanup",
    ),
    dry_run: bool = Option(
        False,
        "--dry-run",
        help="Show what would be deleted without actually deleting",
    ),
):
    """Clean up Kubernetes pods in a specific state."""
    if all_namespaces and namespace:
        typer.echo("Error: Cannot specify both --namespace and --all-namespaces")
        sys.exit(1)

    if interval and not output_yaml:
        output_yaml = True

    try:
        k8s_client = get_k8s_client()
    except Exception as e:
        typer.echo(f"Error connecting to Kubernetes cluster: {e}")
        sys.exit(1)

    if output_yaml:
        yaml_content = generate_cron_job_yaml(
            state=state,
            namespace=namespace,
            all_namespaces=all_namespaces,
            interval=interval,
            dry_run=dry_run,
        )
        typer.echo(yaml_content)
    else:
        find_and_process_pods(
            k8s_client=k8s_client,
            state=state,
            namespace=namespace,
            all_namespaces=all_namespaces,
            dry_run=dry_run,
        )

if __name__ == "__main__":
    app()