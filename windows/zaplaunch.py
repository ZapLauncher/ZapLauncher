import customtkinter as ctk
from tkinter import filedialog
import subprocess
import os
import platform
import zipfile
import requests

CONFIG_FILE = "zap_config.zlc"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ZapLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Zap Launcher - Minecraft without Java!")
        self.geometry("560x400")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")


        self.executable_path = None
        self.game_process = None
        config_status = self.load_saved_path()

        self.title_label = ctk.CTkLabel(self, text="Zap Launcher", font=("Arial", 28))
        self.title_label.pack(pady=20)

        self.subtitle = ctk.CTkLabel(self, text="Install and Run Eaglercraft (No Java Needed)", font=("Arial", 16))
        self.subtitle.pack(pady=5)

        self.install_button = ctk.CTkButton(self, text="Install Minecraft/Eaglercraft", command=self.install_minecraft)
        self.install_button.pack(pady=10)

        self.launch_button = ctk.CTkButton(self, text="Launch Game", command=self.launch_game,
                                           state="normal" if self.executable_path and os.path.isfile(self.executable_path) else "disabled")
        self.launch_button.pack(pady=10)

        self.browse_button = ctk.CTkButton(self, text="Browse Manually", command=self.browse_executable)
        self.browse_button.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 14), wraplength=500, justify="center")
        self.status_label.pack(pady=10)

        # Status after config check
        if config_status == "valid":
            self.status_label.configure(text=f"Found saved executable:\n{self.executable_path}")
        elif config_status == "invalid":
            self.status_label.configure(text="⚠️ The Zap Launcher configuration is incorrect.\nPlease reinstall or browse manually.")
        else:
            self.status_label.configure(text="No game installed or path found. Please install or browse manually.")

        self.check_gpu_support()

        # Spacer
        ctk.CTkLabel(self, text="").pack(pady=(20, 0))

        # Copyright and License
        ctk.CTkLabel(self, text="Copyright (c) 2025 Zohan Haque", font=("Arial", 10), text_color="#888").pack()
        ctk.CTkLabel(self, text="Licensed under the MIT License", font=("Arial", 10), text_color="#888").pack()

    def check_gpu_support(self):
        unsupported_keywords = [
            "microsoft basic display",
            "vmware",
            "virtualbox",
            "intel gma",
            "llvmpipe",
            "software renderer",
            "vboxsvga"
        ]

        gpu_info = self.get_gpu_info().lower()
        if any(keyword in gpu_info for keyword in unsupported_keywords):
            warning = "⚠️ Your graphics card is not supported, your game might crash or be laggy"
            self.status_label.configure(text=f"{self.status_label.cget('text')}\n\n{warning}")

    def get_gpu_info(self):
        try:
            result = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"], capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return str(e)

    def load_saved_path(self):
        if os.path.isfile(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    path = f.read().strip()
                    if os.path.isfile(path):
                        self.executable_path = path
                        return "valid"
                    else:
                        return "invalid"
            except Exception:
                return "invalid"
        return "none"

    def save_path(self, path):
        with open(CONFIG_FILE, "w") as f:
            f.write(path)

    def install_minecraft(self):
        self.status_label.configure(text="📦 Downloading Eaglercraft for Windows...")

        try:
            url = "https://github.com/ZohanHaqu/eaglercraftwindows/releases/download/1.0/eaglercraft.zip"
            zip_path = "eaglercraft.zip"
            extract_path = "eaglercraft"

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            self.status_label.configure(text="📂 Extracting files...")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            exe_path = os.path.join(extract_path, "eaglercraft", "eaglercraft.exe")
            if os.path.isfile(exe_path):
                self.executable_path = exe_path
                self.save_path(exe_path)
                self.status_label.configure(text=f"✅ Eaglercraft installed successfully!\nExecutable: {exe_path}")
                self.launch_button.configure(state="normal")
            else:
                self.status_label.configure(text="❌ Could not find eaglercraft.exe.\nTry using 'Browse Manually'.")

        except Exception as e:
            self.status_label.configure(text=f"❌ Install Error:\n{str(e)}")

    def browse_executable(self):
        file_path = filedialog.askopenfilename(title="Select eaglercraft.exe", filetypes=[("Executable Files", "*.exe")])
        if file_path and os.path.isfile(file_path):
            self.executable_path = file_path
            self.save_path(file_path)
            self.status_label.configure(text=f"📁 Executable set to:\n{file_path}")
            self.launch_button.configure(state="normal")
        else:
            self.status_label.configure(text="❌ No valid file selected.")

    def launch_game(self):
        if self.executable_path and os.path.isfile(self.executable_path):
            self.status_label.configure(text="🚀 Launching Eaglercraft...")
            try:
                subprocess.run([self.executable_path], check=True)
                self.status_label.configure(text="🎮 Game Launched!")
            except subprocess.CalledProcessError:
                self.status_label.configure(text="❌ Game Crashed. Check the terminal output for errors.")
            except Exception as e:
                self.status_label.configure(text=f"❌ Error launching game:\n{str(e)}")
        else:
            self.status_label.configure(text="❌ Game executable not found. Use 'Browse Manually'.")

if __name__ == "__main__":
    app = ZapLauncher()
    app.mainloop()
