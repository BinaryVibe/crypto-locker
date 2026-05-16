import customtkinter as ctk
from tkinter import messagebox
import os
from cryptography.fernet import Fernet

# --- UI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green") # Green for recovery/safety

# --- Configuration ---
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
TARGET_DIRECTORY = os.path.join(DESKTOP_PATH, "DUMMY_TARGET")

class DecryptorTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Project Cryptolocker: Incident Response Decryptor")
        self.geometry("550x350")
        self.resizable(False, False)

        # Title
        self.title_label = ctk.CTkLabel(self, text="Cryptolocker Recovery Tool", font=("Helvetica", 24, "bold"), text_color="#2ECC71")
        self.title_label.pack(pady=(20, 10))

        # Instructions
        self.inst_label = ctk.CTkLabel(self, text="Enter the AES-128 Decryption Key recovered from the C2 Server:")
        self.inst_label.pack(anchor="center")

        # Key Input Box
        self.key_entry = ctk.CTkEntry(self, width=450, placeholder_text="Paste your decryption key here...")
        self.key_entry.pack(pady=(10, 20))

        # Decrypt Button
        self.decrypt_btn = ctk.CTkButton(self, text="UNLOCK FILES", fg_color="#27AE60", hover_color="#1E8449", 
                                        font=("Helvetica", 14, "bold"), height=40, command=self.execute_decryption)
        self.decrypt_btn.pack(pady=10)

        # Status Output
        self.status_box = ctk.CTkTextbox(self, width=450, height=100, state="disabled")
        self.status_box.pack(pady=10)

    def log_status(self, message):
        """Updates the log window in the UI."""
        self.status_box.configure(state="normal")
        self.status_box.insert("end", message + "\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")
        self.update()

    def execute_decryption(self):
        key_input = self.key_entry.get().strip()

        if not key_input:
            messagebox.showwarning("Warning", "Please enter a decryption key.")
            return

        if not os.path.exists(TARGET_DIRECTORY):
            self.log_status("[-] Error: Sandbox directory not found.")
            return

        self.log_status("[*] Validating key and initializing decryption routine...")
        
        try:
            fernet = Fernet(key_input.encode('utf-8'))
            
            # Walk the directory looking for .locked files
            files_restored = 0
            for root, dirs, files in os.walk(TARGET_DIRECTORY):
                for file in files:
                    if not file.endswith(".locked"):
                        continue # Skip files that aren't locked
                        
                    file_path = os.path.join(root, file)
                    original_file_path = file_path[:-7] # Remove the '.locked' extension
                    
                    try:
                        # 1. Read the scrambled bytes
                        with open(file_path, "rb") as f:
                            encrypted_data = f.read()
                        
                        # 2. Reverse the AES math using the key
                        decrypted_data = fernet.decrypt(encrypted_data)
                        
                        # 3. Write the clean bytes to the original filename
                        with open(original_file_path, "wb") as f:
                            f.write(decrypted_data)
                            
                        # 4. Delete the locked garbage file
                        os.remove(file_path)
                        
                        self.log_status(f"  -> Restored: {file}")
                        files_restored += 1
                        
                    except Exception as e:
                        self.log_status(f"  -> Failed to unlock {file}: {e}")

            if files_restored > 0:
                self.log_status(f"\n[+] SUCCESS: {files_restored} files successfully unlocked.")
                messagebox.showinfo("System Restored", "All files have been successfully decrypted and restored.")
            else:
                self.log_status("\n[*] No .locked files found in the target directory.")

        except ValueError:
             self.log_status("[-] FATAL ERROR: Invalid Key Format. Decryption aborted.")
             messagebox.showerror("Error", "The key provided is invalid. Please ensure you copied the entire key string from the C2 server.")
        except Exception as e:
             self.log_status("[-] FATAL ERROR: Incorrect Key. Decryption failed.")
             messagebox.showerror("Error", "Decryption failed. The key is incorrect or the files are corrupted.")

if __name__ == "__main__":
    app = DecryptorTool()
    app.mainloop()