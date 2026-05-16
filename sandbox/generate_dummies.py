import os

def setup_sandbox():
    # Get the path to the current user's desktop dynamically
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    sandbox_dir = os.path.join(desktop, "DUMMY_TARGET")

    # Create the directory if it doesn't exist
    if not os.path.exists(sandbox_dir):
        os.makedirs(sandbox_dir)
        print(f"[+] Created Sandbox Directory at: {sandbox_dir}")
    else:
        print(f"[*] Sandbox already exists at: {sandbox_dir}")

    # A dictionary of fake files and their contents
    dummy_files = {
        "secret_passwords.txt": "Bank pin: 1234\nEmail: password123",
        "financial_report_2026.txt": "Q1 Revenue: Rs 50,000\nQ2 Projected: Rs 75,000",
        "project_ideas.txt": "1. Deepfake Detective\n2. Cryptolocker Simulator",
        "personal_diary.txt": "Dear Diary, today I started building a malware simulator.",
        "dr_sulma_notes.txt": "Remember to emphasize the network exfiltration in the presentation."
    }

    # Generate the files
    for filename, content in dummy_files.items():
        filepath = os.path.join(sandbox_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  -> Created dummy file: {filename}")

    print("\n[+] Sandbox is fully prepped and ready for attack!")

if __name__ == "__main__":
    setup_sandbox()