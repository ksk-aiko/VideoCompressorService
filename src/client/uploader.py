"""
A client for uploading files to a remote server via TCP.
This class encapsulates the functionality needed to upload files to a video compression service.
It handles the connection, file transmission, and response reading from the server.
Attributes:
    socket (TCPSocketClient): The socket client used for communication.
    host (str): The hostname or IP address to connect to.
    port (int): The port number to connect to.
Example:
    >>> uploader = Uploader('compression-server.example.com', 5000)
    >>> success = uploader.send_file('/path/to/video.mp4')
    >>> if success:
    ...     print("File uploaded successfully")
    ... else:
    ...     print("Failed to upload file")
"""

import os
import struct
from typing import Tuple
from .TCPSocketClient import TCPSocketClient

class Uploader:

    def __init__(self, host: str = "localhost", port: int = 5000):
        self.socket = TCPSocketClient()
        self.host = host
        self.port = port
    
    def send_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return False
    
        if not self.socket.connect(self.host, self.port):
            return False
        
        try:
            file_size = os.path.getsize(file_path)

            file_name = os.path.basename(file_path)
            file_name_bytes = file_name.encode('utf-8')

            name_len = len(file_name_bytes)
            # Prepare the header with file name length, file name, and file size
            header = struct.pack('!I', name_len) + file_name_bytes + struct.pack('!Q', file_size)
            self.socket.send(header)

            # Debugging output for the header
            print(f"Sending header: name_len={name_len}, file_name={file_name}, size={file_size}")
            print(f"Header bytes: {len(header)}")
        
            with open(file_path, 'rb') as file:
                # Read the file in chunks and send it
                chunk_size = 4096
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    if not self.socket.send(chunk):
                        print("Failed to send file data.")
                        return False
            
            status_data = self.socket.receive(16)
            status = status_data.decode('utf-8', errors='ignore').strip()

            print(f"status from server: {status}")
            return status == "SUCCESS"
        
        except Exception as e:
            print(f"An error occurred while uploading the file: {e}")
            return False
        finally:
            self.socket.close()

