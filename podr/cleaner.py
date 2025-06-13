"""Pod cleaner module for Pod Reaper."""

import typer
from kubernetes.client import CoreV1Api
from kubernetes.client.models import V1Pod

from .k8s_client import list_pods, delete_pod

def find_and_process_pods(
    k8s_client: CoreV1Api,
    state: str,
    namespace: str = None,
    all_namespaces: bool = False,
    dry_run: bool = False,
) -> None:
    """Find and process pods in the specified state."""
    pods = list_pods(k8s_client, namespace, all_namespaces)
    matching_pods = []

    for pod in pods:
        if _matches_state(pod, state):
            matching_pods.append(pod)

    if not matching_pods:
        typer.echo(f"No pods found in state '{state}'")
        return

    if dry_run:
        typer.echo(f"Would delete {len(matching_pods)} pod(s) in state '{state}':")
        for pod in matching_pods:
            typer.echo(f"  {pod.metadata.name} -n {pod.metadata.namespace}")
        return

    for pod in matching_pods:
        try:
            delete_pod(k8s_client, pod.metadata.name, pod.metadata.namespace)
            typer.echo(f"Deleted pod {pod.metadata.name} in namespace {pod.metadata.namespace}")
        except Exception as e:
            typer.echo(f"Error deleting pod {pod.metadata.name}: {e}")

def _matches_state(pod: V1Pod, state: str) -> bool:
    """Check if a pod matches the specified state."""
    if state == "Terminated":
        return pod.status.phase == "Failed" and pod.status.reason == "Terminated"
    return pod.status.phase == state