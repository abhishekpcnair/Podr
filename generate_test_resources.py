#!/usr/bin/env python3
"""Script to generate test resources for Pod Reaper."""

import time
from kubernetes import client, config
from kubernetes.client import CoreV1Api, BatchV1Api
from kubernetes.client.models import (
    V1Pod,
    V1PodSpec,
    V1Container,
    V1ObjectMeta,
    V1Job,
    V1JobSpec,
    V1PodTemplateSpec,
)

def get_k8s_clients():
    """Initialize and return Kubernetes clients."""
    try:
        config.load_kube_config()
    except config.ConfigException:
        print("Error: Failed to load Kubernetes configuration")
        return None, None
    return client.CoreV1Api(), client.BatchV1Api()

def create_test_namespace(core_v1: CoreV1Api, namespace: str):
    """Create a test namespace if it doesn't exist."""
    try:
        core_v1.create_namespace(
            client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
        )
        print(f"Created namespace: {namespace}")
    except client.exceptions.ApiException as e:
        if e.status == 409:  # Already exists
            print(f"Namespace {namespace} already exists")
        else:
            raise

def create_test_pods(core_v1: CoreV1Api, namespace: str):
    """Create test pods in different states."""
    # Pod that will succeed
    success_pod = V1Pod(
        metadata=V1ObjectMeta(name="test-success-pod"),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name="test",
                    image="busybox",
                    command=["sh", "-c", "exit 0"],
                )
            ],
            restart_policy="Never",
        ),
    )

    # Pod that will fail
    fail_pod = V1Pod(
        metadata=V1ObjectMeta(name="test-fail-pod"),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name="test",
                    image="busybox",
                    command=["sh", "-c", "exit 1"],
                )
            ],
            restart_policy="Never",
        ),
    )

    # Pod that will be pending (no resources)
    pending_pod = V1Pod(
        metadata=V1ObjectMeta(name="test-pending-pod"),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name="test",
                    image="busybox",
                    resources=client.V1ResourceRequirements(
                        requests={"cpu": "999999", "memory": "999999Gi"}
                    ),
                )
            ],
        ),
    )

    # Pod that will be running
    running_pod = V1Pod(
        metadata=V1ObjectMeta(name="test-running-pod"),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name="test",
                    image="busybox",
                    command=["sh", "-c", "sleep 3600"],
                )
            ],
        ),
    )

    # Create all pods
    pods = [success_pod, fail_pod, pending_pod, running_pod]
    for pod in pods:
        try:
            core_v1.create_namespaced_pod(namespace=namespace, body=pod)
            print(f"Created pod: {pod.metadata.name}")
        except client.exceptions.ApiException as e:
            print(f"Error creating pod {pod.metadata.name}: {e}")

def create_test_jobs(batch_v1: BatchV1Api, namespace: str):
    """Create test jobs in different states."""
    # Job that will complete successfully
    success_job = V1Job(
        metadata=V1ObjectMeta(name="test-success-job"),
        spec=V1JobSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test",
                            image="busybox",
                            command=["sh", "-c", "exit 0"],
                        )
                    ],
                    restart_policy="Never",
                )
            ),
        ),
    )

    # Job that will fail
    fail_job = V1Job(
        metadata=V1ObjectMeta(name="test-fail-job"),
        spec=V1JobSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test",
                            image="busybox",
                            command=["sh", "-c", "exit 1"],
                        )
                    ],
                    restart_policy="Never",
                )
            ),
        ),
    )

    # Job that will be active
    active_job = V1Job(
        metadata=V1ObjectMeta(name="test-active-job"),
        spec=V1JobSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="test",
                            image="busybox",
                            command=["sh", "-c", "sleep 3600"],
                        )
                    ],
                )
            ),
        ),
    )

    # Create all jobs
    jobs = [success_job, fail_job, active_job]
    for job in jobs:
        try:
            batch_v1.create_namespaced_job(namespace=namespace, body=job)
            print(f"Created job: {job.metadata.name}")
        except client.exceptions.ApiException as e:
            print(f"Error creating job {job.metadata.name}: {e}")

def main():
    """Main function to create test resources."""
    namespace = "pod-reaper-test"
    core_v1, batch_v1 = get_k8s_clients()
    if not core_v1 or not batch_v1:
        return

    try:
        # Create test namespace
        create_test_namespace(core_v1, namespace)

        # Create test pods
        print("\nCreating test pods...")
        create_test_pods(core_v1, namespace)

        # Create test jobs
        print("\nCreating test jobs...")
        create_test_jobs(batch_v1, namespace)

        print("\nWaiting for resources to reach their final states...")
        time.sleep(5)  # Give resources time to start

        # Print final states
        print("\nFinal states:")
        pods = core_v1.list_namespaced_pod(namespace=namespace)
        for pod in pods.items:
            print(f"Pod {pod.metadata.name}: {pod.status.phase}")

        jobs = batch_v1.list_namespaced_job(namespace=namespace)
        for job in jobs.items:
            status = "Active" if job.status.active else "Completed" if job.status.succeeded else "Failed"
            print(f"Job {job.metadata.name}: {status}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 