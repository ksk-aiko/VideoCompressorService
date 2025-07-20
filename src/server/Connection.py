
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