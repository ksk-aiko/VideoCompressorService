"""
FileReceiver class for receiving files over network connections.
The FileReceiver handles the protocol for receiving file data from a TCP connection
and persisting it to disk using a DiskWriter instance.
The file transfer protocol is as follows:
1. 4 bytes: Unsigned integer representing the length of the filename (network byte order)
2. Variable bytes: UTF-8 encoded filename
3. 8 bytes: Unsigned long long representing the file size in bytes (network byte order)
4. Variable bytes: Raw file data
Attributes:
    disk_writer (DiskWriter): Component responsible for writing received file data to disk.

example usage:
    from .DiskWriter import DiskWriter
    from .TCPSocketServer import Connection
    from .FileReceiver import FileReceiver

    disk_writer = DiskWriter('/path/to/save/files')
    file_receiver = FileReceiver(disk_writer)
    
    conn = Connection()  # Assume this is a valid connection object
    success, filename, filesize = file_receiver.receive_file(conn)
"""

import logging
import os
from typing import Tuple, Optional
from .TCPSocketServer import Connection
from .DiskWriter import DiskWriter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FileReceiver')

class FileReceiver:

    def __init__(self, disk_writer: DiskWriter):
        self.disk_writer = disk_writer
    
    def save_payload(self, filename: str, payload: bytes) -> Optional[str]:
        # TODO: Implement logic to save the payload to disk
    
    def receive_file_with_metadata(self, conn: Connection, filename: str, file_size: int) -> Tuple[bool, str, int]:
        try:
            logger.info(f"Receiving file with provided metadata: {filename} of size {file_size} bytes")

            # Receive the file data in chunks
            remaining = file_size
            file_data = bytearray()  # Initialize as empty bytearray
            chunk_size = 4096  # 4KB chunks

            while remaining > 0:
                current_chunk_size = min(chunk_size, remaining)
                chunk = conn.receive(current_chunk_size)

                if not chunk:
                    logger.error(f"Connection closed before receiving the complete file. Missing {remaining} bytes.")
                    return False, filename, file_size
                
                file_data.extend(chunk) # Append the received chunk to file_data
                remaining -= len(chunk) # Update remaining bytes to receive

            file_path = self.disk_writer.write_to_disk(file_data, filename)

            if file_path:
                logger.info(f"Successfully received file: {filename} and saved to {file_path}")
                return True, filename, file_size
            else:
                logger.error(f"Failed to write file {filename} to disk")
                return False, filename, file_size

        except Exception as e:
            logger.error(f"Error receiving file: {e}")
            return False, "", 0