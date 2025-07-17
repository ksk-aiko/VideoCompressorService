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
from typing import Tuple, Optional
from .TCPSocketClient import TCPSocketClient
import json

class Uploader:

    def __init__(self, host: str = "localhost", port: int = 5000, output_dir: str = "downloads"):
        self.socket = TCPSocketClient()
        self.host = host
        self.port = port
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def send_file(self, file_path: str, options: dict = None) -> Optional[str]:
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
            print(f"Request senf.Waiting for reponse...")

            response_header = self._receive_all(8)
            if not response_header:
                print("Failed to receive response header from server.")
                return None
            
            json_size, media_type_size = struct.unpack('!HB', response_header[:3])
            payload_size = int.from_bytes(response_header[3:], 'big')

            response_json_data = self._receive_all(json_size)
            response_media_type = self._receive_all(media_type_size)
            response_payload = self._receive_all(payload_size)

            if payload_size > 0 and response_payload:
                response_media_type = response_media_type.decode('utf-8')
                original_basename = os.path.splitext(os.path.basename(file_path))[0]
                output_filename = f"{original_basename}_processed.{response_media_type}"
                output_path = os.path.join(self.output_dir, output_filename)

                with open(output_path, 'wb') as f:
                    f.write(response_payload)
                
                print(f"Success! Processed file saved to {output_path}")
                return output_path
            else: 
                if response_json_data:
                    error_info = json.loads(response_json_data.decode('utf-8'))
                    print(f"Received an error from server: {error_info.get('error', 'Unknown error')}")
                else:
                    print("Received an empty or invalid response from server.")
                return None
                
        except Exception as e:
            print(f"An error occurred while uploading the file: {e}")
            return False
        finally:
            self.socket.close()
    
    def _receive_all(self, n: int) -> Optional[bytes]:
        data = bytearray()
        while len(data) < n:
            packet = self.socket.receive(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)