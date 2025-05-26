import os
"""
A utility class for selecting files using a GUI dialog.

This class provides a static method to open a file selection dialog
and return the path of the selected file.

Methods:
    select_file() -> Optional[str]: Opens a file selection dialog and returns the selected file path.
        Returns None if no file is selected or if the selected path is not a valid file.

Example:
    file_path = FileSelector.select_file()
    if file_path:
        print(f"Selected file: {file_path}")
    else:
        print("No file selected")
"""
import tkinter as tk
from tkinter import filedialog
from typing import Optional

class FileSelector:
    @staticmethod
    def select_file() -> Optional[str]:
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title = "Select a file",
            filetypes = [("MP4 files", "*.mp4"), ("All files", "*.*")]
        )

        root.destroy()

        if file_path and os.path.isfile(file_path):
            return file_path
        return None