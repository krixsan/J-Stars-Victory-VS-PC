"""
J-Stars Victory VS+ | Native PC Launcher (Tkinter Python Version)
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

def is_controller_connected():
    try:
        import ctypes
        xinput = ctypes.windll.xinput1_4
        class XINPUT_STATE(ctypes.Structure):
            _fields_ = [("dwPacketNumber", ctypes.c_uint), ("Gamepad", ctypes.c_byte * 12)]
        state = XINPUT_STATE()
        return xinput.XInputGetState(0, ctypes.byref(state)) == 0
    except Exception:
        try:
            import ctypes
            xinput = ctypes.windll.xinput9_1_0
            class XINPUT_STATE(ctypes.Structure):
                _fields_ = [("dwPacketNumber", ctypes.c_uint), ("Gamepad", ctypes.c_byte * 12)]
            state = XINPUT_STATE()
            return xinput.XInputGetState(0, ctypes.byref(state)) == 0
        except Exception:
            return False

class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("J-Stars Victory VS+ | Native PC Launcher")
        self.geometry("520x600")
        self.resizable(False, False)
        self.configure(bg="#141620")

        # Header
        header = tk.Frame(self, bg="#191b28", height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        accent_bar = tk.Frame(header, bg="#e65100", height=5)
        accent_bar.pack(fill=tk.X, side=tk.TOP)

        title = tk.Label(header, text="J-STARS VICTORY VS+", font=("Segoe UI", 18, "bold"), fg="#ffb300", bg="#191b28")
        title.pack(anchor="w", padx=25, pady=(15, 0))

        sub = tk.Label(header, text="PS4 Native PC Translation Wrapper (shadPS4 Vulkan Core)", font=("Segoe UI", 9), fg="#a0a5b9", bg="#191b28")
        sub.pack(anchor="w", padx=25)

        # Card
        card = tk.Frame(self, bg="#1e2130", bd=1, relief=tk.SOLID)
        card.pack(fill=tk.BOTH, padx=25, pady=20, expand=True)

        # Controller
        tk.Label(card, text="CONTROLLER STATUS", font=("Segoe UI", 8, "bold"), fg="#ff9800", bg="#1e2130").pack(anchor="w", padx=20, pady=(15, 2))
        self.lbl_ctrl = tk.Label(card, text="Checking controller...", font=("Segoe UI", 10, "bold"), fg="#2ecc71", bg="#1e2130")
        self.lbl_ctrl.pack(anchor="w", padx=20, pady=(0, 10))

        sep = tk.Frame(card, bg="#2d3248", height=1)
        sep.pack(fill=tk.X, padx=20, pady=5)

        # FPS
        tk.Label(card, text="Framerate & Game Speed Mode:", font=("Segoe UI", 9), fg="#f0f0f5", bg="#1e2130").pack(anchor="w", padx=20, pady=(10, 2))
        self.var_fps = tk.StringVar(value="60 FPS - High Smoothness (Normal Speed Fixed, 0.5x Delta)")
        combo_fps = ttk.Combobox(card, textvariable=self.var_fps, state="readonly", values=[
            "60 FPS - High Smoothness (Normal Speed Fixed, 0.5x Delta)",
            "30 FPS - Original Console Target (PS4 Native Rate)"
        ])
        combo_fps.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Resolution
        tk.Label(card, text="Display Resolution:", font=("Segoe UI", 9), fg="#f0f0f5", bg="#1e2130").pack(anchor="w", padx=20, pady=(5, 2))
        self.var_res = tk.StringVar(value="1920 x 1080 (1080p Full HD - Recommended)")
        combo_res = ttk.Combobox(card, textvariable=self.var_res, state="readonly", values=[
            "1920 x 1080 (1080p Full HD - Recommended)",
            "2560 x 1440 (1440p 2K QHD)",
            "3840 x 2160 (2160p 4K Ultra HD)",
            "1280 x 720 (720p HD Standard)"
        ])
        combo_res.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Toggles
        self.var_fs = tk.BooleanVar(value=False)
        chk_fs = tk.Checkbutton(card, text="Fullscreen / Borderless Mode", variable=self.var_fs, bg="#1e2130", fg="#f0f0f5", selectcolor="#141620", activebackground="#1e2130")
        chk_fs.pack(anchor="w", padx=20, pady=3)

        self.var_fsr = tk.BooleanVar(value=True)
        chk_fsr = tk.Checkbutton(card, text="Enable AMD FSR Quality Upscaling", variable=self.var_fsr, bg="#1e2130", fg="#f0f0f5", selectcolor="#141620", activebackground="#1e2130")
        chk_fsr.pack(anchor="w", padx=20, pady=3)

        # Buttons frame
        btn_frame = tk.Frame(self, bg="#141620")
        btn_frame.pack(fill=tk.X, padx=25, pady=(0, 20))

        btn_play = tk.Button(btn_frame, text="▶  PLAY J-STARS VICTORY VS+", font=("Segoe UI", 12, "bold"), bg="#f57c00", fg="white", activebackground="#ff9800", activeforeground="white", relief=tk.FLAT, height=2, cursor="hand2", command=self.launch_game)
        btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        btn_saves = tk.Button(btn_frame, text="📁 Save Folder", font=("Segoe UI", 9), bg="#282c41", fg="#f0f0f5", activebackground="#3a3f5a", activeforeground="white", relief=tk.FLAT, height=2, cursor="hand2", command=self.open_save_folder)
        btn_saves.pack(side=tk.RIGHT, padx=(0, 0))

        self.poll_controller()

    def poll_controller(self):
        if is_controller_connected():
            self.lbl_ctrl.config(text="●  Xbox Controller Connected (Slot 1 Ready)", fg="#2ecc71")
        else:
            self.lbl_ctrl.config(text="○  Keyboard Mode Active (No Xbox Controller Detected)", fg="#f1c40f")
        self.after(1500, self.poll_controller)

    def open_save_folder(self):
        save_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "extracted_game", "app0", "savedata"))
        if os.path.exists(save_path):
            os.startfile(save_path)
        else:
            messagebox.showinfo("Save Data", "Save data folder does not exist yet. Play the game to create one!")

    def launch_game(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        exe_path = os.path.join(base_dir, "out", "jstars_pc.exe")
        if not os.path.exists(exe_path):
            exe_path = os.path.join(base_dir, "jstars_pc.exe")
        if not os.path.exists(exe_path):
            messagebox.showerror("Error", f"jstars_pc.exe not found at:\n{exe_path}")
            return

        boot_bin = os.path.join(base_dir, "out", "boot-linked.bin")
        if not os.path.exists(boot_bin):
            boot_bin = os.path.join(base_dir, "boot-linked.bin")

        app0_dir = os.path.join(base_dir, "extracted_game", "app0")
        import_names = os.path.join(base_dir, "out", "import_names.txt")

        env = os.environ.copy()
        if "30 FPS" in self.var_fps.get():
            env["JSTARS_30FPS"] = "1"
            env["BB_FPS_LIMIT"] = "30"
        else:
            env["JSTARS_30FPS"] = "0"
            env["BB_FPS_LIMIT"] = "60"

        env["BB_FSR1"] = "1" if self.var_fsr.get() else "0"
        env["BB_FORCE_FULLSCREEN"] = "1" if self.var_fs.get() else "0"

        res_str = self.var_res.get()
        if "2560" in res_str:
            env["BB_RES_WIDTH"] = "2560"
            env["BB_RES_HEIGHT"] = "1440"
        elif "3840" in res_str:
            env["BB_RES_WIDTH"] = "3840"
            env["BB_RES_HEIGHT"] = "2160"
        elif "1280" in res_str:
            env["BB_RES_WIDTH"] = "1280"
            env["BB_RES_HEIGHT"] = "720"
        else:
            env["BB_RES_WIDTH"] = "1920"
            env["BB_RES_HEIGHT"] = "1080"

        cmd = [exe_path, boot_bin, "--app0", app0_dir]
        if os.path.exists(import_names):
            cmd += ["--import-names", import_names]

        self.withdraw()
        try:
            subprocess.run(cmd, cwd=os.path.dirname(exe_path), env=env)
        finally:
            self.deiconify()

if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
