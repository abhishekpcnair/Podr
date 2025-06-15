# Pod Reaper (`podr`) 💀

[![Pytest](https://github.com/user/podr/actions/workflows/pytest.yml/badge.svg)](https://github.com/user/podr/actions/workflows/pytest.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/user/podr.svg?style=social&label=Star)](https://github.com/user/podr)

**Tired of lingering Kubernetes pods and jobs cluttering your namespaces? Meet Pod Reaper, the ultimate cleanup tool for your cluster.**

`podr` is a simple but powerful CLI tool that finds Kubernetes pods and jobs in a specific state (like `Succeeded`, `Failed`, or `Error`) and deletes them. Stop manually running `kubectl delete` and automate your cluster hygiene!

---

### The Problem: A Messy Cluster

In a dynamic Kubernetes environment, completed pods (`Succeeded`) and failed jobs (`Failed`) can accumulate quickly. This digital debris clutters your cluster, making it difficult to monitor and manage. While a few leftover resources might seem harmless, they can eventually:

-   **Obscure real issues:** A long list of failed pods makes it hard to spot new, critical failures.
-   **Consume resources:** In some cases, completed resources can still hold on to claims or other resources.
-   **Create noise:** A messy `kubectl get pods` output is a daily annoyance for any developer or SRE.

### Why Pod Reaper?

-   **🎯 Simple & Specific:** Target exactly what you want to delete. Clean up `Succeeded` pods, `Failed` jobs, or pods in an `Error` state with a single, readable command.
-   **🤖 Automation-Ready:** Generate Kubernetes `CronJob` YAML directly from the CLI. Set up a GitOps workflow to keep your cluster clean automatically.
-   **🛡️ Safe & Predictable:** Use the `--dry-run` flag to see what `podr` *would* delete before making any changes. No surprises.
-   **🌐 Namespace Flexible:** Clean the current namespace, a specific namespace, or all namespaces at once (`-A`).

---

## 🚀 Installation

Install directly from PyPI:

```bash
pip install podr
```

## Usage

The command structure is simple: `podr <resource> <state> [options]`

| Resource | Supported States                                    |
| :------- | :-------------------------------------------------- |
| `pods`   | `Succeeded`, `Failed`, `Error`, `Running`, `Pending`  |
| `jobs`   | `Completed`, `Failed`, `Active`                     |

**Examples:**

```bash
# See which 'Succeeded' pods would be deleted in the 'default' namespace
podr pods Succeeded -n default --dry-run

# Delete all pods in an 'Error' state across the entire cluster
podr pods Error -A

# Delete all 'Completed' jobs in the current namespace
podr jobs Completed

# Generate a CronJob YAML to clean failed jobs every 15 minutes
podr jobs Failed --interval 900 --output
```

---

## 🧪 Development & Testing

We believe in robust testing. `podr` comes with a full `pytest` suite and a script to generate test resources in your cluster.

### Generating Test Resources

To test `podr` in a real environment (like `minikube`), you can generate a sample set of pods and jobs.

1.  **Target your cluster:** Make sure your `kubectl` context is pointing to the desired test cluster.
2.  **Run the script:**

    ```bash
    python3 generate_test_resources.py
    ```

This will create a new namespace `pod-reaper-test` and populate it with resources in various states, ready for reaping.

### Running the Test Suite

Run the full `pytest` suite locally:

```bash
make test
```

---

## 🙌 How to Contribute

We welcome contributions! Whether it's a bug fix, a new feature, or a documentation improvement, we'd love your help.

1.  **Fork the repository.**
2.  **Create a new branch:** `git checkout -b my-feature-branch`
3.  **Set up your development environment:**
    ```bash
    make install-dev
    ```
4.  **Make your changes.**
5.  **Run the tests:** `make test`
6.  **Submit a pull request!**

We'll review your PR as soon as possible.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.