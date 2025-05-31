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
import struct
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
    
    def receive_file(self, conn: Connection) -> Tuple[bool, str, int]:
        try:
            # Read the file name length
            # Receive 4 bytes for the length of the file name
            name_len_data = conn.receive(4)
            if not name_len_data or len(name_len_data) != 4:
                logger.error("Failed to receive file name length")
                return False, "", 0

            name_len = struct.unpack('!I', name_len_data)[0]

            filename_data = conn.receive(name_len)
            if not filename_data or len(filename_data) != name_len:
                logger.error("Failed to receive file name")
                return False, "", 0
            
            filename = filename_data.decode('utf-8')

            # Next 8 bytes are the file size
            size_data = conn.receive(8)
            if not size_data or len(size_data) != 8:
                logger.error("Failed to receive file size")
                return False, "", 0
            
            file_size = struct.unpack('!Q', size_data)[0]

            logger.info(f"Receiving file: {filename} of size {file_size} bytes")

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