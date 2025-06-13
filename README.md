# Pod Reaper (podr)

A CLI tool for cleaning up Kubernetes pods in specific states.

## Installation

```bash
pip install podr
```

## Usage

The main command is `podr clean`, which allows you to clean up pods in specific states:

```bash
# Clean up Succeeded pods in the current namespace
podr clean Succeeded

# Clean up Failed pods in a specific namespace
podr clean Failed -n my-namespace

# Clean up Terminated pods across all namespaces
podr clean Terminated -A

# Show what would be deleted without actually deleting
podr clean Succeeded --dry-run

# Generate a CronJob YAML that runs every 5 minutes
podr clean Failed -t 300 -o yaml
```

### Supported States

- `Succeeded`: Pods that have completed successfully
- `Failed`: Pods that have failed
- `Terminated`: Pods that have been terminated

### Options

- `-n, --namespace`: Specify the namespace to clean pods from (defaults to current context namespace)
- `-A, --all-namespaces`: Clean pods across all namespaces
- `-t, --interval`: Generate a CronJob that runs every N seconds
- `-o, --output`: Output Kubernetes Job/CronJob YAML instead of performing cleanup
- `--dry-run`: Show what would be deleted without actually deleting

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

MIT