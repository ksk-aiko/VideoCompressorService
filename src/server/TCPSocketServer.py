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

import socket
import threading
import logging
from typing import Optional, Tuple, Callable
from .Connection import Connection
from .ConnectionManager import ConnectionManager
from .RequestHandler import RequestHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TCPSocketServer')


class TCPSocketServer:
    def __init__(self, host: str, port: int, handler_factory: Callable, connection_manager: ConnectionManager):
        self.server_socket: Optional[socket.socket] = None
        self.host = host
        self.port = port
        self.handler_factory = handler_factory
        self.connection_manager = connection_manager

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(self.host, self.port)
            self.server_socket.listen(5)
            logger.info(f"Server started and listening on {self.host}:{self.port}")

            while True:
                client_socket, client_address = self.server_socket.accept()
                ip_address = client_address[0]

                if self.connection_manager.add_connection(ip_address):
                    logger.info(f"Accepted connection from {client_address}")
                    connection = Connection(client_socket, client_address)
                    handler_thread = threading.Thread(
                        target=self._client_handler_wrapper,
                        args=(connection, ip_address)
                    )
                    handler_thread.daemon = True
                    handler_thread.start()
                else:
                    logger.warning(f"Rejected connection from {client_address} (IP already processing.)")
                    try:
                        client_socket.sendall(b"SERVER_BUSY: Your IP is already proccessing a request.")
                    finally:
                        client_socket.close()
        except KeyboardInterrupt:
            logger.info("Server shutting down due to KeyboardInterrupt.")
        except Exception as e:
            logger.critical(f"Server failed to start or crashed: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
                logger.info("Server socket closed.")
    
    def _client_handler_wrapper(self, connection: Connection, ip_address: str):
        try:
            handler = self.handler_factory(connection)
            handler.handle_connection()
        except Exception as e:
            logger.error(f"Unhandled exception in handler for {connection.address}: {e}")
        finally:
            self.connection_manager.remove_connection(ip_address)
            connection.close()
            logger.info(f"Handler finished and connection closed for {ip_address}")