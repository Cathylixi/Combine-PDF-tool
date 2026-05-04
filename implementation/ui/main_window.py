"""Tkinter main window for selecting a folder and combining PDFs."""

import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from core.pdf_combiner import combine_pdfs
from utils.logger import get_logger
from utils.models import DEFAULT_OUTPUT_FILENAME, CombineResult

logger = get_logger(__name__)


class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Combine PDF Tool")
        self.root.geometry("820x560")
        self.root.minsize(720, 480)

        self.folder_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")

        self._message_queue: "queue.Queue[str]" = queue.Queue()
        self._worker: Optional[threading.Thread] = None

        self._build_layout()
        self.root.after(100, self._drain_queue)

    def _build_layout(self) -> None:
        padding = {"padx": 10, "pady": 6}

        input_frame = ttk.LabelFrame(self.root, text="1. Select PDF Folder")
        input_frame.pack(fill="x", **padding)

        ttk.Label(input_frame, text="PDF Folder:").grid(
            row=0, column=0, sticky="w", padx=6, pady=6
        )
        self.folder_entry = ttk.Entry(
            input_frame, textvariable=self.folder_path_var, width=80
        )
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        self.browse_btn = ttk.Button(
            input_frame, text="Browse Folder...", command=self._pick_folder
        )
        self.browse_btn.grid(row=0, column=2, padx=6, pady=6)
        input_frame.columnconfigure(1, weight=1)

        action_frame = ttk.LabelFrame(self.root, text="2. Action")
        action_frame.pack(fill="x", **padding)

        self.combine_btn = ttk.Button(
            action_frame, text="Combine PDFs", command=self._on_combine
        )
        self.combine_btn.pack(side="left", padx=6, pady=8)

        ttk.Button(action_frame, text="Clear Log", command=self._clear_log).pack(
            side="left", padx=6, pady=8
        )

        ttk.Label(
            action_frame,
            text=f"Output file: {DEFAULT_OUTPUT_FILENAME}",
        ).pack(side="left", padx=16, pady=8)

        log_frame = ttk.LabelFrame(self.root, text="3. Log / Progress")
        log_frame.pack(fill="both", expand=True, **padding)

        self.log_text = tk.Text(log_frame, wrap="none", height=18)
        self.log_text.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        log_scroll_y = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll_y.pack(side="right", fill="y", pady=6)
        self.log_text.configure(yscrollcommand=log_scroll_y.set, state="disabled")

        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill="x", side="bottom")
        ttk.Label(status_bar, textvariable=self.status_var, anchor="w").pack(
            fill="x", padx=12, pady=4
        )

    def _pick_folder(self) -> None:
        path = filedialog.askdirectory(title="Select PDF Folder")
        if path:
            self.folder_path_var.set(path)

    def _validate_inputs(self) -> bool:
        folder_path = self.folder_path_var.get().strip()

        if not folder_path:
            messagebox.showwarning("Notice", "Please select a PDF folder first.")
            return False
        if not os.path.isdir(folder_path):
            messagebox.showerror("Error", f"Folder does not exist:\n{folder_path}")
            return False
        return True

    def _on_combine(self) -> None:
        if not self._validate_inputs():
            return

        folder_path = self.folder_path_var.get().strip()
        output_path = os.path.join(folder_path, DEFAULT_OUTPUT_FILENAME)
        overwrite = False

        if os.path.exists(output_path):
            overwrite = messagebox.askyesno(
                "Confirm Overwrite",
                f"{DEFAULT_OUTPUT_FILENAME} already exists in this folder.\n\n"
                "Do you want to overwrite it?",
            )
            if not overwrite:
                return

        self._start_worker(overwrite=overwrite)

    def _start_worker(self, overwrite: bool) -> None:
        if self._worker and self._worker.is_alive():
            messagebox.showinfo(
                "Notice", "A task is already running. Please wait for it to finish."
            )
            return

        self._set_busy(True)
        self._log("=== Combine PDFs ===")
        folder_path = self.folder_path_var.get().strip()

        def worker() -> None:
            try:
                result = combine_pdfs(
                    folder_path,
                    overwrite=overwrite,
                    on_progress=self._enqueue,
                )
                self._enqueue(_summary_line(result))
            except Exception as exc:
                logger.exception("Worker failed")
                self._enqueue(f"[ERROR] {exc}")
            finally:
                self._enqueue("__DONE__")

        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()

    def _enqueue(self, message: str) -> None:
        self._message_queue.put(message)

    def _drain_queue(self) -> None:
        try:
            while True:
                msg = self._message_queue.get_nowait()
                if msg == "__DONE__":
                    self._set_busy(False)
                    continue
                self._log(msg)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._drain_queue)

    def _log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.browse_btn.configure(state=state)
        self.combine_btn.configure(state=state)
        self.status_var.set("Working..." if busy else "Ready")


def _summary_line(result: CombineResult) -> str:
    return (
        f"[Summary] combined_files={result.total_files} "
        f"total_pages={result.total_pages} output={result.output_path}"
    )


def launch() -> None:
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()
