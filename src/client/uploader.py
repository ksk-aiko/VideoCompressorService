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
import json

class Uploader:

    def __init__(self, host: str = "localhost", port: int = 5000):
        self.socket = TCPSocketClient()
        self.host = host
        self.port = port
    
    def send_file(self, file_path: str, options: dict = None) -> bool:
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return False
    
        if not self.socket.connect(self.host, self.port):
            return False
        
        try:
            # Prepare the header with JSON metadata, media type, and payload size
            json_data = json.dumps(options or {}).encode('utf-8')
            json_size = len(json_data)

            # Extract media type from file name
            file_name = os.path.basename(file_path)
            media_type = os.path.splitext(file_name)[1].lstrip('.').encode('utf-8')
            media_type_size = len(media_type)

            # Read the file payload
            with open(file_path, 'rb') as f:
                payload = f.read()
            payload_size = len(payload)

            # Construct the header
            header = struct.pack('!HB', json_size, media_type_size) + payload_size.to_bytes(5, 'big')

            self.socket.send(header)
            self.socket.send(json_data)
            self.socket.send(media_type)
            self.socket.send(payload)

            print(f"Sending requset: json_size={json_size}, media_type={media_type.decode('utf-8')}, payload_size={payload_size}")

            # Wait for the server's response
            status_data = self.socket.receive(16)
            status = status_data.decode('utf-8', errors='ignore').strip()

            print(f"status from server: {status}")
            return "SUCCESS" in status
        
        except Exception as e:
            print(f"An error occurred while uploading the file: {e}")
            return False
        finally:
            self.socket.close()

