import sys
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

# Add the project root to the path to allow importing the 'podr' package
sys.path.insert(0, ".")
# Can't import from podr.main directly anymore because of the typer.run()
# We need to import the function itself to test it.
from podr.main import app
from podr.cleaner import VALID_POD_PHASES, VALID_JOB_STATES

runner = CliRunner()

def create_mock_pod(name, namespace, phase):
    """Helper to create a mock V1Pod object."""
    pod = MagicMock()
    pod.metadata.name = name
    pod.metadata.namespace = namespace
    pod.status.phase = phase
    pod.status.reason = None
    pod.status.container_statuses = []
    return pod

def create_mock_error_pod(name, namespace):
    pod = create_mock_pod(name, namespace, "Failed")
    # Simulate container error status
    container_status = MagicMock()
    container_status.state.terminated.exit_code = 1
    pod.status.container_statuses = [container_status]
    return pod

def create_mock_job(name, namespace, succeeded=0, active=0, failed=0):
    """Helper to create a mock V1Job object."""
    job = MagicMock()
    job.metadata.name = name
    job.metadata.namespace = namespace
    job.status.succeeded = succeeded
    job.status.active = active
    job.status.failed = failed
    return job

@pytest.fixture
def mock_k8s_clients():
    """A fixture to provide mock Kubernetes clients."""
    with patch('podr.main.get_k8s_client') as mock_get:
        mock_core_v1 = MagicMock()
        mock_batch_v1 = MagicMock()
        mock_get.return_value = (mock_core_v1, mock_batch_v1)
        yield mock_core_v1, mock_batch_v1

# --- Test Cases ---

def test_clean_pods_succeeded_dry_run(mock_k8s_clients):
    """Test dry run for cleaning 'Succeeded' pods."""
    mock_core_v1, _ = mock_k8s_clients
    mock_core_v1.list_pod_for_all_namespaces.return_value.items = [
        create_mock_pod("pod-1", "ns-a", "Succeeded")
    ]
    # To test a function with typer.run(), we pass the function to the runner
    # and the arguments as a list.
    result = runner.invoke(app, ["pods", "Succeeded", "--dry-run", "-A"])
    assert result.exit_code == 0
    assert "Would delete 1 pods(s)" in result.stdout
    assert "pod-1" in result.stdout

def test_clean_pods_error(mock_k8s_clients):
    mock_core_v1, _ = mock_k8s_clients
    mock_core_v1.list_pod_for_all_namespaces.return_value.items = [
        create_mock_error_pod("error-pod-1", "ns-b")
    ]
    result = runner.invoke(app, ["pods", "Error", "-A", "--dry-run"])
    assert result.exit_code == 0
    assert "Would delete 1 pods(s)" in result.stdout
    assert "error-pod-1" in result.stdout

def test_clean_jobs_completed_namespaced(mock_k8s_clients):
    """Test cleaning 'Completed' jobs in a specific namespace."""
    _, mock_batch_v1 = mock_k8s_clients
    mock_batch_v1.list_namespaced_job.return_value.items = [
        create_mock_job("job-1", "myns", succeeded=1)
    ]
    result = runner.invoke(app, ["jobs", "Completed", "--namespace", "myns", "--dry-run"])
    assert result.exit_code == 0
    assert "Would delete 1 jobs(s)" in result.stdout
    assert "job-1" in result.stdout

def test_yaml_generation_for_jobs(mock_k8s_clients):
    """Test that YAML generation for a CronJob works correctly."""
    result = runner.invoke(app, ["jobs", "Failed", "-t", "900", "--output"])
    assert result.exit_code == 0
    assert "kind: CronJob" in result.stdout
    assert "pod-reaper-jobs-failed-cronjob" in result.stdout
    assert "*/15 * * * *" in result.stdout  # 900 seconds = 15 minutes

def test_no_resources_found(mock_k8s_clients):
    """Test that a message is displayed when no resources are found."""
    mock_core_v1, _ = mock_k8s_clients
    mock_core_v1.list_pod_for_all_namespaces.return_value.items = []
    result = runner.invoke(app, ["pods", "Running", "-A"])
    assert result.exit_code == 0
    assert "No pods found in state 'Running'" in result.stdout

def test_invalid_resource_type():
    result = runner.invoke(app, ["goats", "Running"])
    assert result.exit_code == 1
    assert "Invalid resource type" in result.stdout

def test_invalid_state_for_pods():
    result = runner.invoke(app, ["pods", "Completed"])
    assert result.exit_code == 1
    assert f"Invalid state 'Completed' for pods. Must be one of: {', '.join(VALID_POD_PHASES)}" in result.stdout
    
def test_invalid_state_for_jobs():
    """Test that an invalid state for a resource exits with an error."""
    result = runner.invoke(app, ["jobs", "Succeeded"])
    assert result.exit_code == 1
    assert f"Invalid state 'Succeeded' for jobs. Must be one of: {', '.join(VALID_JOB_STATES)}" in result.stdout 