import os
import sys
import subprocess
import configparser
import re
from pathlib import Path

def get_databrickscfg_path():
    return Path.home() / '.databrickscfg'

def load_config():
    config_path = get_databrickscfg_path()
    config = configparser.ConfigParser()
    if config_path.exists():
        config.read(config_path)
    return config

def save_config(config):
    config_path = get_databrickscfg_path()
    with open(config_path, 'w') as f:
        config.write(f)
    # Set permissions to 600 (read/write by owner only)
    os.chmod(config_path, 0o600)

def run_databricks_auth_login(profile, host=None):
    cmd = ["databricks", "auth", "login", "--profile", profile]
    if host:
        cmd.extend(["--host", host])
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def extract_profile_from_host(host):
    # Remove protocol
    host = host.replace("https://", "").replace("http://", "")
    # Remove trailing slash
    host = host.rstrip("/")
    # Extract first part of domain
    parts = host.split(".")
    if len(parts) > 0:
        return parts[0]
    return "DEFAULT"

def configure_profile(profile_name, host=None):
    print(f"Configuring profile: {profile_name}")
    
    # 1. Authenticate
    run_databricks_auth_login(profile_name, host)
    
    # 2. Update Configuration
    config = load_config()
    
    if profile_name not in config:
        # Should have been created by auth login, but just in case
        config[profile_name] = {}
        if host:
            config[profile_name]['host'] = host

    print("\n--- Compute Configuration ---")
    print("Choose one of the following options:")
    print("1. Serverless Compute (Recommended for ephemeral workloads)")
    print("2. Cluster ID (For specific interactive/job clusters)")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        config[profile_name]['serverless_compute_id'] = 'auto'
        # Remove cluster_id if it exists to avoid conflicts
        if 'cluster_id' in config[profile_name]:
            del config[profile_name]['cluster_id']
        print(f"Set serverless_compute_id = auto for profile '{profile_name}'")
        
    elif choice == "2":
        cluster_id = input("Enter Cluster ID: ").strip()
        config[profile_name]['cluster_id'] = cluster_id
        # Remove serverless_compute_id if it exists
        if 'serverless_compute_id' in config[profile_name]:
            del config[profile_name]['serverless_compute_id']
        print(f"Set cluster_id = {cluster_id} for profile '{profile_name}'")
    else:
        print("Invalid choice. Skipping compute configuration.")

    save_config(config)
    
    print("\n--- Configuration Updated ---")
    # Display config (redacting token)
    section = config[profile_name]
    for key in section:
        val = section[key]
        if key == 'token':
            val = '[REDACTED]'
        print(f"{key} = {val}")
    print(f"\nFull configuration saved to {get_databrickscfg_path()}")

if __name__ == "__main__":
    profile_arg = "DEFAULT"
    host_arg = None
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("http"):
            host_arg = arg
            profile_arg = extract_profile_from_host(host_arg)
        else:
            profile_arg = arg
            
    try:
        configure_profile(profile_arg, host_arg)
    except subprocess.CalledProcessError as e:
        print(f"Error during authentication: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
