"""
Command Line Interface for the Video Compressor Service client.
This module provides a CLI to select a video file, validate its size,
and upload it to the compression service.
Classes:
    CLI: Handles the command line interface operations.
Usage:
    python -m src.client.cli [host] [port]
    Where:
        host: Server hostname or IP (default: localhost)
        port: Server port (default: 5000)
Example:
    python -m src.client.cli compression-server.example.com 8080
"""

import sys
import os
from .FileSelector import FileSelector
from .Uploader import Uploader
from .Validator import Validator

class CLI:
    
    def __init__(self, host:str = "localhost", port: int = 5000):
        self.uploader = Uploader(host, port)

    def run(self):
        file_path = FileSelector.select_file()
        if not file_path:
            print("No file selected. Exiting.")
            return False

        print(f"Selected file: {file_path}")

        max_size_mb = 100
        if not Validator.check_file_size(file_path, max_size_mb):
            print(f"File size is too large. Maximum allowed size is {max_size_mb} MB.")
            return False
        
        print("Uploading file...")
        success = self.uploader.send_file(file_path)

        if success:
            print("File uploaded successfully.")
        else:
            print("Failed to upload file.") 
            return False
    
    def main():
        host = "localhost"
        port = 5000

        args = sys.argv[1:]
        if len(args) >= 1:
            host = args[0]
        if len(args) >= 2:
            try:
                port = int(args[1])
            except ValueError:
                print(f"Invalid port number: {args[1]}.")
                sys.exit(1)
        
        cli = CLI(host, port)
        success = cli.run()

        sys.exit(0 if success else 1)
    
    if __name__ == "__main__":
        main()