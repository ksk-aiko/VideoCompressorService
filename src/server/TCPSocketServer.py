import socket
"""
A TCP socket server implementation for handling client connections.
This module provides classes for creating a TCP socket server and managing client connections.
It handles socket creation, connection acceptance, and data transmission with proper error handling.
Classes:
    Connection: Manages an individual client connection, providing methods for sending and receiving data.
    TCPSocketServer: Implements a TCP server that listens for and accepts client connections.
Example:
    server = TCPSocketServer()
    if server.listen(8080):
        conn = server.accept()
        if conn:
            data = conn.receive(1024)
            conn.send(b"Response")
            conn.close()
        server.close()
"""

import logging
from typing import Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TCPSocketServer')

class Connection:

    def __init__(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        self.socket = client_socket
        self.address = client_address

    def send(self, data: bytes) -> bool:
        try:
            self.socket.sendall(data)
            return True
        except Exception as e:
            logger.error(f"Failed to send data to {self.address}: {e}")
            return False
    
    def receive(self, size: int) -> bytes:
        try:
            return self.socket.recv(size)
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            return b''
    
    def close(self):
        try:
            self.socket.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

class TCPSocketServer:
    def __init__(self):
        self.server_socket: Optional[socket.socket] = None
        self.is_listening = False

    def listen(self, port: int, host: str = '0.0.0.0') -> bool:
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set socket options to allow reuse of the address
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5) # Allow up to 5 queued connections
            self.is_listening = True
            logger.info(f"Server listening on {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            self.close()
            return False
    
    def accept(self) -> Optional[Connection]:
        if not self.is_listening or not self.server_socket:
            logger.error("Server is not listening.")
            return None
        
        try:
            client_socket, client_address = self.server_socket.accept()
            logger.info(f"Accepted connection from {client_address}")
            return Connection(client_socket, client_address)
        except Exception as e:
            logger.error(f"Error accepting connection: {e}")
            return None
    
    def close(self) -> None:
        if self.server_socket:
            try:
                self.server_socket.close()
                logger.info("Server socket closed.")
            except Exception as e:
                logger.error(f"Error closing server socket: {e}")
            finally:
                self.server_socket = None
                self.is_listening = False