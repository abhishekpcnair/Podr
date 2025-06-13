"""Test script for Pod Reaper CLI."""

import sys
from podr.main import app

if __name__ == "__main__":
    # Pass all command line arguments to the app
    sys.argv[0] = "podr"  # Set the program name to match the CLI
    app()