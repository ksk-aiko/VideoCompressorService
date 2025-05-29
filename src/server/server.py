"""
Server class that manages a TCP socket server for receiving files.
This server handles incoming client connections, processes file transfer requests,
monitors storage capacity, and responds with status information. It supports
graceful shutdown via signal handling.
The server uses the following components:
- TCPSocketServer: Manages socket connections
- RequestHandler: Routes and processes incoming requests
- FileReceiver: Handles file transfer protocol
- StorageChecker: Monitors available disk space
- StatusResponder: Generates status responses
- DiskWriter: Handles file system operations
Attributes:
    port (int): Port number to bind the server to (default: 5000)
    server (TCPSocketServer): Socket server instance
    storage_dir (str): Directory to store uploaded files
    disk_writer (DiskWriter): Handles file system operations
    storage_checker (StorageChecker): Monitors disk space usage
    file_receiver (FileReceiver): Handles file reception
    status_responder (StatusResponder): Generates status responses
    request_handler (RequestHandler): Routes and processes client requests
Methods:
    start(): Starts the server and enters the main listening loop
    main(): Static entry point that parses command-line arguments and starts the server
Usage:
    Run directly as a script with optional port and storage directory arguments:
    python -m server.Server [port] [storage_directory]
"""

import os
import sys
import logging
import signal
import time
import socket
from typing import Optional

from .TCPSocketServer import TCPSocketServer, Connection
from .RequestHandler import RequestHandler
from .FileReceiver import FileReceiver
from .StorageChecker import StorageChecker
from .StatusResponder import StatusResponder
from .DiskWriter import DiskWriter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log")
    ]
)
logger = logging.getLogger('Server')

running = True

def signal_handler(sig, frame):
    global running
    logger.info("Shutdown signal received. Stopping server...")
    running = False

class Server:

    def __init__(self, port: int = 5000, storage_dir: str = "uploads", max_storage_tb: float = 4.0):
        self.port = port
        self.server = TCPSocketServer()
        self.storage_dir = storage_dir

        self.disk_writer = DiskWriter(storage_dir)
        self.storage_checker = StorageChecker(max_storage_tb, storage_dir)
        self.file_receiver = FileReceiver(self.disk_writer)
        self.status_responder = StatusResponder()

        self.request_handler = RequestHandler(
            self.file_receiver,
            self.storage_checker,
            self.status_responder
        )
    
    def start(self):

        if not self.server.listen(self.port):
            logger.error(f"Failed to start server on port {self.port}.")
            return False

        logger.info(f"Server started on port {self.port}.")
        logger.info(f"Storage directory: {self.storage_dir}")        
        logger.info(f"Waiting for connections...")

        global running
        running = True

        signal.signal(signal.SIGINT, signal_handler) # Handle Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler) # Handle termination signal

        while running:
            self.server.server_socket.settimeout(1.0)
            try:
                conn = self.server.accept()
                if conn:
                    self.request_handler.handle_connection(conn)
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Error in server loop: {e}")
                time.sleep(1)  # Avoid tight loop on error
        
        logger.info("Server shutting down....")
        self.server.close()
        return True
    
def main():
    port = 5000
    storage_dir = os.path.abspath("uploads")

    args = sys.argv[1:]
    if len(args) >= 1:
        try:
            port = int(args[0])
        except ValueError:
            logger.error(f"Invalid port number: {args[0]}")
            sys.exit(1)
    
    if len(args) >= 2:
        storage_dir = os.path.abspath(args[1])
    
    server = Server(port=port, storage_dir=storage_dir)
    success = server.start()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


