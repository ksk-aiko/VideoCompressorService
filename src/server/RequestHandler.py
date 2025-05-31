"""
RequestHandler class for handling client connections to the video compression service.
This class manages the protocol for file upload requests, validates storage capacity,
receives file data, and communicates status responses back to clients.
The handler implements a simple protocol where:
1. Client sends a 4-byte length of the filename
2. Client sends the filename as UTF-8 encoded string
3. Client sends an 8-byte file size
4. Client sends the file data if space is available
5. Server responds with status code
Attributes:
    file_receiver (FileReceiver): Component that handles receiving and storing files
    storage_checker (StorageChecker): Component that checks if there's enough storage space
    status_responder (StatusResponder): Component that sends status responses to clients
"""

import logging
import struct
from typing import Optional
from .TCPSocketServer import Connection
from .FileReceiver import FileReceiver
from .StorageChecker import StorageChecker
from .StatusResponder import StatusResponder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('RequestHandler')

class RequestHandler:
    
    def __init__(self, file_receiver: FileReceiver, storage_checker: StorageChecker, status_responder: StatusResponder):
        self.file_receiver = file_receiver
        self.storage_checker = storage_checker
        self.status_responder = status_responder

    def handle_connection(self, conn: Connection) -> bool:
        try:
            logger.info(f"Handling connection from {conn.address}")

            name_len_data = conn.receive(4)
            if not name_len_data or len(name_len_data) != 4:
                logger.error("Failed to receive name length data")
                self.status_responder.send_status(conn, "ERROR")
                return False
            
            name_len = struct.unpack('!I', name_len_data)[0]

            filename_data = conn.receive(name_len)
            if not filename_data or len(filename_data) != name_len:
                logger.error("Failed to receive filename data")
                self.status_responder.send_status(conn, "ERROR")
                return False

            filename = filename_data.decode('utf-8')

            size_data = conn.receive(8)
            if not size_data or len(size_data) != 8:
                logger.error("Failed to receive file size data")
                self.status_responder.send_status(conn, "ERROR")
                return False

            file_size = struct.unpack('!Q', size_data)[0]

            logger.info(f"Request to upload file: {filename} of size {file_size} bytes")

            if not self.storage_checker.has_capacity(file_size):
                logger.warning(f"Not enough storage capacity for file: {filename}")
                self.status_responder.send_status(conn, "FULL")
                return False
            
            # Receive the metadata.Because the file_receiver already handles the file receiving process
            success, received_filename, _ = self.file_receiver.receive_file_with_metadata(conn, filename, file_size)

            if success:
                self.status_responder.send_status(conn, "SUCCESS")
                logger.info(f"Successfully received file: {received_filename}")
                return True
            else:
                self.status_responder.send_status(conn, "ERROR")
                logger.error(f":Failed to process file: {filename}")
                return False
        except Exception as e:
            logger.error(f"Error handling connection: {e}")
            try:
                self.status_responder.send_status(conn, "ERROR")
            except:
                logger.error("Failed to send error status")
            return False
        finally:
            conn.close()