"""Main CLI module for Pod Reaper."""

import sys
from typing import Optional
import typer
from typer import Option

# NOTE: All previous attempts to structure this as a multi-command app have failed.
# This is a fallback to the simplest possible structure to ensure it runs.

from .k8s_client import get_k8s_client
from .cleaner import find_and_process_resources, validate_state
from .job_generator import generate_cron_job_yaml


def clean(
    resource: str = typer.Argument(
        ...,
        help="Resource type to clean up (e.g., 'pods', 'jobs').",
    ),
    state: str = typer.Argument(
        ...,
        help="State to clean up (e.g., 'Succeeded', 'Failed', 'Completed').",
    ),
    namespace: Optional[str] = Option(
        None,
        "-n",
        "--namespace",
        help="Namespace to clean resources from (defaults to current context).",
    ),
    all_namespaces: bool = Option(
        False,
        "-A",
        "--all-namespaces",
        help="Clean resources across all namespaces.",
    ),
    interval: Optional[int] = Option(
        None,
        "-t",
        "--interval",
        help="Generate a CronJob that runs every N seconds.",
        min=1,
    ),
    output_yaml: bool = Option(
        False,
        "-o",
        "--output",
        help="Output Kubernetes Job/CronJob YAML instead of performing cleanup.",
    ),
    dry_run: bool = Option(
        False,
        "--dry-run",
        help="Show what would be deleted without actually deleting.",
    ),
):
    """
    Clean up Kubernetes resources (pods or jobs) in a specific state.
    """
    if resource not in ["pods", "jobs"]:
        typer.echo(f"Error: Invalid resource type '{resource}'. Must be 'pods' or 'jobs'.")
        raise typer.Exit(code=1)

    try:
        state = validate_state(resource, state)
    except typer.Exit:
        raise

    if all_namespaces and namespace:
        typer.echo("Error: Cannot specify both --namespace and --all-namespaces.")
        raise typer.Exit(code=1)

    if interval and not output_yaml:
        output_yaml = True

    try:
        k8s_client, batch_client = get_k8s_client()
    except Exception as e:
        typer.echo(f"Error connecting to Kubernetes cluster: {e}")
        raise typer.Exit(code=1)

    if output_yaml:
        yaml_content = generate_cron_job_yaml(
            resource_type=resource,
            state=state,
            namespace=namespace,
            all_namespaces=all_namespaces,
            interval=interval,
            dry_run=dry_run,
        )
        typer.echo(yaml_content)
    else:
        find_and_process_resources(
            k8s_client=k8s_client,
            batch_client=batch_client,
            resource_type=resource,
            state=state,
            namespace=namespace,
            all_namespaces=all_namespaces,
            dry_run=dry_run,
        )

# This is needed for the test runner
app = typer.Typer()
app.command()(clean)

if __name__ == "__main__":
    app()