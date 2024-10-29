import os
import subprocess
import sys
from pathlib import Path

def generate_requirements():
    """
    Generate requirements.txt file from the current virtual environment.
    Returns success message or error details.
    """
    try:
        # Check if we're in a virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            return "Error: No virtual environment activated. Please activate your venv first."

        # Get the current working directory
        current_dir = Path.cwd()
        requirements_file = current_dir / "requirements.txt"

        # Use pip freeze to get all installed packages
        process = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Write the output to requirements.txt
        requirements_file.write_text(process.stdout)
        
        # Count number of packages
        package_count = len(process.stdout.splitlines())
        
        return f"Success: Created requirements.txt with {package_count} packages at {requirements_file}"

    except subprocess.CalledProcessError as e:
        return f"Error running pip freeze: {e}"
    except IOError as e:
        return f"Error writing requirements.txt: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

if __name__ == "__main__":
    print(generate_requirements())