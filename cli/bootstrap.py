import sys
import os
import subprocess
import platform
import argparse
import webbrowser
import shutil

# --- Configuration ---
REQUIRED_PYTHON_MAJOR = 3
REQUIRED_PYTHON_MINOR = 13
REQUIRED_NODE_VERSION_STR = "v20.19.6" # Exact string from node -v

# --- ANSI Colors ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- Helpers ---
def print_step(msg): print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")
def print_success(msg): print(f"{Colors.GREEN}✔ {msg}{Colors.ENDC}")
def print_error(msg): print(f"{Colors.FAIL}✖ {msg}{Colors.ENDC}")
def print_warning(msg): print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def get_base_dir():
    # cli/bootstrap.py -> cli/ -> root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Checks ---

def check_python(fix=False):
    """
    Checks if the CURRENT running python is 3.13.
    If fix=True, prompts user to download (and then must exit).
    """
    current_ver = sys.version_info
    is_valid = (current_ver.major == REQUIRED_PYTHON_MAJOR and current_ver.minor == REQUIRED_PYTHON_MINOR)
    
    if is_valid:
        print_success(f"Python {current_ver.major}.{current_ver.minor} detected")
        return True
    
    print_error(f"Python {REQUIRED_PYTHON_MAJOR}.{REQUIRED_PYTHON_MINOR} is required. Detected: {current_ver.major}.{current_ver.minor}")
    
    if not fix:
        return False
        
    print(f"\n{Colors.BOLD}Options:{Colors.ENDC}")
    print("[1] Download Python 3.13")
    print("[2] Exit")
    
    choice = input(f"\n{Colors.CYAN}Select option [1-2]: {Colors.ENDC}")
    
    if choice == "1":
        print_step("Opening Python download page...")
        webbrowser.open("https://www.python.org/downloads/release/python-3130/")
        print_warning("ACTION REQUIRED: Install Python 3.13, check 'Add to PATH', and RESTART this terminal.")
        sys.exit(0) # Logic requires restart
    return False

def check_node(fix=False):
    """
    Checks if Node.js is installed and matches specific version.
    """
    try:
        # Check node
        result = subprocess.run(["node", "-v"], capture_output=True, text=True, check=True)
        detected_version = result.stdout.strip()
        
        # We can implement loose check if needed, but exact requirement was requested
        if detected_version == REQUIRED_NODE_VERSION_STR:
            print_success(f"Node.js {detected_version} detected")
            return True
        else:
            print_error(f"Node.js {REQUIRED_NODE_VERSION_STR} required. Detected: {detected_version}")

    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Node.js not found.")

    if not fix:
        return False

    print(f"\n{Colors.BOLD}Options:{Colors.ENDC}")
    print(f"[1] Download Node.js {REQUIRED_NODE_VERSION_STR}")
    print("[2] Continue anyway (Risky)")
    print("[3] Exit")
    
    choice = input(f"\n{Colors.CYAN}Select option [1-3]: {Colors.ENDC}")
    if choice == "1":
        print_step("Opening Node.js download page...")
        webbrowser.open("https://nodejs.org/dist/v20.19.6/")
        print_warning("Please install Node.js and restart the terminal.")
        sys.exit(0)
    elif choice == "2":
        return True
    
    sys.exit(1)

def check_permissions(fix=False):
    """
    Windows-only: Check PowerShell Execution Policy.
    """
    if platform.system() != "Windows":
        return True

    try:
        cmd = ["powershell", "-Command", "Get-ExecutionPolicy"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        policy = result.stdout.strip()
        
        if policy in ["Restricted", "AllSigned"]:
            print_warning(f"PowerShell Execution Policy is '{policy}'. Scripts will fail.")
            if not fix:
                return False
            
            print(f"We need to set ExecutionPolicy to 'RemoteSigned' for the CurrentUser.")
            choice = input(f"{Colors.CYAN}Authorize change? [y/N]: {Colors.ENDC}")
            if choice.lower() == 'y':
                subprocess.run(["powershell", "-Command", "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"], check=True)
                print_success("Execution Policy updated.")
                return True
            else:
                return False
        else:
            print_success(f"Execution Policy: {policy} (OK)")
            return True

    except Exception as e:
        print_warning(f"Could not check execution policy: {e}")
        return True # Soft fail

# --- Setup Phases ---

import hashlib

def get_file_hash(filepath):
    """Calculate SHA256 hash of a file."""
    if not os.path.exists(filepath): return None
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data: break
            sha256.update(data)
    return sha256.hexdigest()

def check_and_update_hash(marker_path, source_file):
    """
    Returns True if update is needed (hashes differ or marker missing).
    Updates marker if source_file exists.
    """
    if not os.path.exists(source_file): return False
    
    current_hash = get_file_hash(source_file)
    stored_hash = None
    
    if os.path.exists(marker_path):
        with open(marker_path, 'r') as f:
            stored_hash = f.read().strip()
            
    if current_hash != stored_hash:
        return True, current_hash
    return False, current_hash

def setup_backend():
    print(f"\n{Colors.HEADER}=== Backend Environment ==={Colors.ENDC}")
    root = get_base_dir()
    backend_dir = os.path.join(root, "Jarvis_code")
    venv_dir = os.path.join(backend_dir, "venv")
    
    # Check Venv
    if not os.path.exists(venv_dir):
        print_step("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print_success("Venv created.")
    
    # Requirement Check with Hash
    req_file = os.path.join(backend_dir, "requirements.txt")
    hash_file = os.path.join(venv_dir, ".requirements_hash")
    
    needs_update, new_hash = check_and_update_hash(hash_file, req_file)
    
    if needs_update:
        print_step("Updating backend dependencies (detected change)...")
        pip_path = os.path.join(venv_dir, "Scripts", "pip") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "pip")
        try:
            subprocess.run([pip_path, "install", "-r", "requirements.txt"], cwd=backend_dir, check=True)
            # Write new hash only on success
            with open(hash_file, 'w') as f: f.write(new_hash)
            print_success("Backend dependencies installed.")
        except subprocess.CalledProcessError:
            print_error("Failed to install requirements.txt.")
            sys.exit(1)
    else:
        print_success("Backend dependencies up-to-date.")

def setup_frontend():
    print(f"\n{Colors.HEADER}=== Frontend Environment ==={Colors.ENDC}")
    root = get_base_dir()
    frontend_dir = os.path.join(root, "agent-starter-react")
    node_modules = os.path.join(frontend_dir, "node_modules")
    
    # Check pnpm
    if shutil.which("pnpm"):
        pass # Silent pnpm check
    else:
        print_warning("pnpm missing.")
        # ... logic as before ...
        subprocess.run("npm install -g pnpm", shell=True, check=True)
        print_success("pnpm installed.")

    # Smart Install for Frontend
    pkg_file = os.path.join(frontend_dir, "package.json")
    hash_file = os.path.join(node_modules, ".package_hash")
    
    # Ensure node_modules exists, otherwise force update
    if not os.path.exists(node_modules):
        needs_update = True
        new_hash = get_file_hash(pkg_file)
    else:
        needs_update, new_hash = check_and_update_hash(hash_file, pkg_file)

    if needs_update:
        print_step("Installing frontend dependencies...")
        try:
            # Add concurrently safety check
            if not os.path.exists(os.path.join(node_modules, "concurrently")):
                 subprocess.run("pnpm add -D concurrently", cwd=frontend_dir, shell=True, check=True, stdout=subprocess.DEVNULL)
            
            subprocess.run("pnpm install", cwd=frontend_dir, shell=True, check=True)
            
            # Save hash
            if not os.path.exists(node_modules): os.makedirs(node_modules)
            with open(hash_file, 'w') as f: f.write(new_hash or "")
            
            print_success("Frontend ready.")
        except subprocess.CalledProcessError:
            print_error("Frontend setup failed.")
            sys.exit(1)
    else:
        print_success("Frontend dependencies up-to-date.")

def launch():
    print(f"\n{Colors.HEADER}=== Starting J.A.R.V.I.S. ==={Colors.ENDC}")
    root = get_base_dir()
    frontend_dir = os.path.join(root, "agent-starter-react")
    
    print(f"{Colors.GREEN}System Online. Press Ctrl+C to stop.{Colors.ENDC}\n")
    try:
        subprocess.run("pnpm dev", cwd=frontend_dir, shell=True)
    except KeyboardInterrupt:
        print("\nStopping...")

# --- Main Entry ---

def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. CLI")
    parser.add_argument('command', choices=['start', 'startr', 'doctor', 'help'], help="Command")
    
    if len(sys.argv) < 2:
        parser.print_help()
        return

    args = parser.parse_args()
    
    if args.command == 'doctor':
        print(f"{Colors.HEADER}Running Diagnostics...{Colors.ENDC}")
        py_ok = check_python(fix=False)
        node_ok = check_node(fix=False)
        perm_ok = check_permissions(fix=False)
        
        print("\nSummary:")
        print(f"Python: {'OK' if py_ok else 'FAIL'}")
        print(f"Node.js: {'OK' if node_ok else 'FAIL'}")
        print(f"Permissions: {'OK' if perm_ok else 'WARN'}")
        
    elif args.command in ['start', 'startr']:
        print(f"{Colors.CYAN}Initializing Bootstrap...{Colors.ENDC}")
        
        # 1. Environment Checks (Strict)
        if not check_python(fix=True): sys.exit(1)
        check_node(fix=True)
        check_permissions(fix=True)
        
        # 2. Setup
        setup_backend()
        setup_frontend()
        
        # 3. Launch
        launch()

    elif args.command == 'help':
        parser.print_help()

if __name__ == "__main__":
    main()
