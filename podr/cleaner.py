"""Resource cleaner module for Pod Reaper."""

import typer
from kubernetes.client import CoreV1Api, BatchV1Api
from kubernetes.client.models import V1Pod, V1Job

from .k8s_client import list_pods, delete_pod, list_jobs, delete_job

# Valid states for different resource types
VALID_POD_PHASES = ["Succeeded", "Failed", "Terminated", "Running", "Pending", "Error"]
VALID_JOB_STATES = ["Completed", "Failed", "Active"]

def validate_state(resource_type: str, state: str) -> str:
    """Validate the state argument based on resource type."""
    valid_states = VALID_POD_PHASES if resource_type == "pods" else VALID_JOB_STATES
    if state not in valid_states:
        typer.echo(f"Error: Invalid state '{state}' for {resource_type}. Must be one of: {', '.join(valid_states)}")
        raise typer.Exit(1)
    return state

def find_and_process_resources(
    k8s_client: CoreV1Api,
    batch_client: BatchV1Api,
    resource_type: str,
    state: str,
    namespace: str = None,
    all_namespaces: bool = False,
    dry_run: bool = False,
) -> None:
    """Find and process resources in the specified state."""
    if resource_type == "pods":
        resources = list_pods(k8s_client, namespace, all_namespaces)
        matching_resources = [r for r in resources if _matches_pod_state(r, state)]
        resource_name = "pod"
        delete_func = delete_pod
    else:  # jobs
        resources = list_jobs(batch_client, namespace, all_namespaces)
        matching_resources = [r for r in resources if _matches_job_state(r, state)]
        resource_name = "job"
        delete_func = delete_job

    if not matching_resources:
        typer.echo(f"No {resource_type} found in state '{state}'")
        return

    if dry_run:
        typer.echo(f"Would delete {len(matching_resources)} {resource_type}(s) in state '{state}':")
        for resource in matching_resources:
            typer.echo(f"  {resource.metadata.name} -n {resource.metadata.namespace}")
        return

    for resource in matching_resources:
        try:
            delete_func(
                k8s_client if resource_type == "pods" else batch_client,
                resource.metadata.name,
                resource.metadata.namespace
            )
            typer.echo(f"Deleted {resource_name} {resource.metadata.name} in namespace {resource.metadata.namespace}")
        except Exception as e:
            typer.echo(f"Error deleting {resource_name} {resource.metadata.name}: {e}")

def _matches_pod_state(pod: V1Pod, state: str) -> bool:
    """Check if a pod matches the specified state."""
    pod_phase = pod.status.phase
    
    if state == "Error":
        # A pod can be in an 'Error' state for multiple reasons.
        # Common cases include:
        # 1. The pod phase is 'Failed'.
        # 2. The container has a 'Terminated' state with a non-zero exit code or 'Error' reason.
        if pod_phase == "Failed":
            return True
        if pod.status.container_statuses:
            for status in pod.status.container_statuses:
                if status.state.terminated and (status.state.terminated.exit_code != 0 or status.state.terminated.reason == 'Error'):
                    return True
        return False
        
    if state == "Terminated":
        # This is a specific case where a pod is killed for a reason like OOMKilled
        return pod_phase == "Failed" and pod.status.reason == "Terminated"

    return pod_phase == state

def _matches_job_state(job: V1Job, state: str) -> bool:
    """Check if a job matches the specified state."""
    if not job.status:
        return False

    succeeded = job.status.succeeded or 0
    active = job.status.active or 0
    failed = job.status.failed or 0

    if state == "Completed":
        return succeeded > 0 and not active
    elif state == "Failed":
        return failed > 0 and not active
    elif state == "Active":
        return active > 0
    return False

def delete_pod(k8s_client, pod, dry_run: bool):
    """Delete a single pod."""
    # ... existing code ...