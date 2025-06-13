"""Kubernetes client module for Pod Reaper."""

from kubernetes import client, config
from kubernetes.client import CoreV1Api
from kubernetes.config import ConfigException

def get_k8s_client() -> CoreV1Api:
    """Initialize and return a Kubernetes client."""
    try:
        # Try to load in-cluster config first
        config.load_incluster_config()
    except ConfigException:
        try:
            # Fall back to kubeconfig
            config.load_kube_config()
        except ConfigException as e:
            raise Exception("Failed to load Kubernetes configuration") from e

    return client.CoreV1Api()

def list_pods(
    k8s_client: CoreV1Api,
    namespace: str = None,
    all_namespaces: bool = False,
) -> list:
    """List pods in the specified namespace(s)."""
    if all_namespaces:
        namespace = None

    try:
        if namespace:
            return k8s_client.list_namespaced_pod(namespace=namespace).items
        return k8s_client.list_pod_for_all_namespaces().items
    except Exception as e:
        raise Exception(f"Failed to list pods: {e}")

def delete_pod(
    k8s_client: CoreV1Api,
    pod_name: str,
    namespace: str,
) -> None:
    """Delete a pod by name and namespace."""
    try:
        k8s_client.delete_namespaced_pod(
            name=pod_name,
            namespace=namespace,
        )
    except Exception as e:
        raise Exception(f"Failed to delete pod {pod_name} in namespace {namespace}: {e}")