"""Job generator module for Pod Reaper."""

import yaml
from typing import Optional

def generate_cron_job_yaml(
    state: str,
    namespace: Optional[str] = None,
    all_namespaces: bool = False,
    interval: Optional[int] = None,
    dry_run: bool = False,
) -> str:
    """Generate Kubernetes CronJob YAML for pod cleanup."""
    # Build the podr command
    cmd = ["podr", "clean", state]
    if namespace:
        cmd.extend(["-n", namespace])
    if all_namespaces:
        cmd.append("-A")
    if dry_run:
        cmd.append("--dry-run")

    # Calculate schedule
    if interval:
        if interval >= 60 and interval % 60 == 0:
            minutes = interval // 60
            schedule = f"*/{minutes} * * * *"
        else:
            schedule = f"*/{interval} * * * * *"
    else:
        schedule = "0 * * * *"  # Default to hourly

    # Generate the CronJob YAML
    cronjob = {
        "apiVersion": "batch/v1",
        "kind": "CronJob",
        "metadata": {
            "name": f"pod-reaper-{state.lower()}-cronjob",
            "namespace": namespace or "default",
        },
        "spec": {
            "schedule": schedule,
            "jobTemplate": {
                "spec": {
                    "template": {
                        "spec": {
                            "serviceAccountName": "pod-reaper",
                            "containers": [
                                {
                                    "name": "pod-reaper",
                                    "image": "python:3.9-slim",
                                    "command": [
                                        "pip",
                                        "install",
                                        "podr",
                                        "&&",
                                        *cmd,
                                    ],
                                }
                            ],
                            "restartPolicy": "OnFailure",
                        }
                    }
                }
            }
        }
    }

    # Add RBAC resources
    rbac = {
        "apiVersion": "v1",
        "kind": "ServiceAccount",
        "metadata": {
            "name": "pod-reaper",
            "namespace": namespace or "default",
        }
    }

    role = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "Role",
        "metadata": {
            "name": "pod-reaper",
            "namespace": namespace or "default",
        },
        "rules": [
            {
                "apiGroups": [""],
                "resources": ["pods"],
                "verbs": ["list", "delete"],
            }
        ]
    }

    role_binding = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "RoleBinding",
        "metadata": {
            "name": "pod-reaper",
            "namespace": namespace or "default",
        },
        "subjects": [
            {
                "kind": "ServiceAccount",
                "name": "pod-reaper",
                "namespace": namespace or "default",
            }
        ],
        "roleRef": {
            "kind": "Role",
            "name": "pod-reaper",
            "apiGroup": "rbac.authorization.k8s.io",
        }
    }

    # Combine all resources
    resources = [rbac, role, role_binding, cronjob]
    return yaml.dump_all(resources, default_flow_style=False)