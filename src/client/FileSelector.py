

"""
FileSelector class for handling file selection operations.

This class provides static methods to select a file from the filesystem.
Currently, it uses a command line input to get the file path, but there
is a commented-out implementation using tkinter's file dialog.

Methods:
    select_file(): Prompts the user to enter a file path and validates it.
        Returns the file path if valid, None otherwise.
"""

import os
# import tkinter as tk
# from tkinter import filedialog
from typing import Optional

class FileSelector:
    @staticmethod
    def select_file() -> Optional[str]:
        file_path = input("Enter the path to the file you want to upload: ")
        if file_path and os.path.isfile(file_path):
            return file_path
        elif file_path:
            print(f"Error: The path '{file_path}' is not a valid file.")
        return None

        # root = tk.Tk()
        # root.withdraw()

        # file_path = filedialog.askopenfilename(
        #     title = "Select a file",
        #     filetypes = [("MP4 files", "*.mp4"), ("All files", "*.*")]
        # )

        # root.destroy()

        # if file_path and os.path.isfile(file_path):
        #     return file_path
        # return None