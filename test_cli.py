"""Test script for Pod Reaper CLI."""

import sys
import os

if __name__ == "__main__":
    # Construct the command string from the script arguments
    command_args = " ".join(sys.argv[1:])
    
    # Get the correct python executable
    python_executable = sys.executable
    
    # Build the full command to execute podr as a module
    full_command = f"{python_executable} -m podr.main {command_args}"
    
    print(f"Executing command: {full_command}")
    
    # Run the command using the system's shell
    os.system(full_command)