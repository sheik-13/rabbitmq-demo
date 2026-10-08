import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext


class RabbitMQDemoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RabbitMQ Live Demo Controller")
        self.root.geometry("800x600")

        self.folders = sorted(
            [
                f
                for f in os.listdir(".")
                if os.path.isdir(f)
                and f.startswith(("01", "02", "03", "04", "05", "06"))
            ]
        )
        self.current_folder = tk.StringVar(
            value=self.folders[0] if self.folders else ""
        )

        # Top Frame: Folder selection and Docker controls
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Select Demo Part:").pack(side=tk.LEFT, padx=5)
        self.folder_cb = ttk.Combobox(
            top_frame,
            textvariable=self.current_folder,
            values=self.folders,
            state="readonly",
            width=25,
        )
        self.folder_cb.pack(side=tk.LEFT, padx=5)
        self.folder_cb.bind("<<ComboboxSelected>>", self.on_folder_change)

        ttk.Button(
            top_frame, text="Start Broker (Compose Up)", command=self.docker_up
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            top_frame, text="Stop Broker (Compose Down)", command=self.docker_down
        ).pack(side=tk.LEFT, padx=5)

        # Middle Frame: Script selection
        mid_frame = ttk.Frame(self.root, padding=10)
        mid_frame.pack(fill=tk.X)

        ttk.Label(mid_frame, text="Select Script:").pack(side=tk.LEFT, padx=5)
        self.current_script = tk.StringVar()
        self.script_cb = ttk.Combobox(
            mid_frame, textvariable=self.current_script, state="readonly", width=30
        )
        self.script_cb.pack(side=tk.LEFT, padx=5)

        ttk.Button(mid_frame, text="Run Script", command=self.run_script).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(mid_frame, text="Clear Output", command=self.clear_output).pack(
            side=tk.LEFT, padx=5
        )

        # Output text area
        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, bg="black", fg="lightgreen", font=("Courier", 10)
        )
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.on_folder_change()

    def log(self, msg):
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.see(tk.END)

    def clear_output(self):
        self.text_area.delete("1.0", tk.END)

    def on_folder_change(self, event=None):
        folder = self.current_folder.get()
        if not folder:
            return
        scripts = sorted(
            [f for f in os.listdir(folder) if f.endswith(".py") and f != "common.py"]
        )
        self.script_cb["values"] = scripts
        if scripts:
            self.script_cb.current(0)
        else:
            self.script_cb.set("")

    def _run_cmd_thread(self, cmd, cwd, success_msg=None):
        self.log(f"$ {' '.join(cmd)}")

        def target():
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                for line in iter(proc.stdout.readline, ""):
                    if line:
                        self.root.after(0, self.log, line.rstrip("\n"))
                proc.stdout.close()
                proc.wait()
                if proc.returncode == 0 and success_msg:
                    self.root.after(0, self.log, success_msg)
                elif proc.returncode != 0:
                    self.root.after(
                        0,
                        self.log,
                        f"[Error] Process exited with code {proc.returncode}",
                    )
            except Exception as e:
                self.root.after(0, self.log, f"[Exception] {e}")
            self.root.after(0, self.log, "-" * 60)

        threading.Thread(target=target, daemon=True).start()

    def docker_up(self):
        folder = self.current_folder.get()
        if folder:
            self.log(f"\nStarting Docker in {folder}...")
            self._run_cmd_thread(
                ["docker", "compose", "up", "-d", "--wait"],
                cwd=folder,
                success_msg="RabbitMQ is ready. UI at http://localhost:15672 (guest/guest)",
            )

    def docker_down(self):
        folder = self.current_folder.get()
        if folder:
            self.log(f"\nStopping Docker in {folder}...")
            self._run_cmd_thread(
                ["docker", "compose", "down", "-v"],
                cwd=folder,
                success_msg="RabbitMQ stopped and volumes removed.",
            )

    def run_script(self):
        folder = self.current_folder.get()
        script = self.current_script.get()
        if folder and script:
            self.log(f"\nRunning {script}...")
            self._run_cmd_thread(["python", script], cwd=folder)


if __name__ == "__main__":
    root = tk.Tk()
    app = RabbitMQDemoGUI(root)
    root.mainloop()
