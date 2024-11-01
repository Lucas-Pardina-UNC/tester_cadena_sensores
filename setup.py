import sys
import subprocess

# Required Python version
REQUIRED_PYTHON_VERSION = (3, 12, 2)

def check_python_version():
    """Checks if the current Python version meets the minimum requirement."""
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        print(f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}.{REQUIRED_PYTHON_VERSION[2]} or newer is required.")
        print("Please install the required version of Python and try again.")
        sys.exit(1)

def install_dependencies():
    """Installs required packages listed in requirements.txt."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Ensure that pip is installed and try again.")
        sys.exit(1)

def main():
    # Step 1: Check Python version
    check_python_version()

    # Step 2: Install dependencies
    print("Installing dependencies...")
    install_dependencies()
    print("All dependencies are installed successfully.")

    print("Setup complete! You can now run your application.")

if __name__ == "__main__":
    main()
