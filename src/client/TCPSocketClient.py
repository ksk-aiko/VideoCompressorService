import socket
from typing import Optional

class TCPSocketClient:
    """
    TCP Socket Client for network communication.
    This class provides a simple interface for TCP/IP socket operations including
    connecting to a server, sending and receiving data, and closing the connection.
    Attributes:
        socket (Optional[socket.socket]): The underlying socket object used for network communication.
    Examples:
        ```python
        client = TCPSocketClient()
        if client.connect('localhost', 8080):
            client.send(b'Hello, server!')
            response = client.receive(1024)
            print(f"Received: {response}")
            client.close()
        ```
    """

    def __init__(self):
        self.socket: Optional[socket.socket] = None

    def connect(self, host:str, port:int) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def send(self, data:bytes) -> bool:

        if not self.socket:
            print("Socket is not connected.")
            return False

        try:
            self.socket.sendall(data)
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
    
    def receive(self, size: int) -> bytes:

        if not self.socket:
            print("Socket is not connected.")
            return b''
        
        try:
            return self.socket.recv(size)
        except Exception as e:
            print(f"Receive failed: {e}")
            return b''
    
    def close(self) -> None:
        if self.socket:
            self.socket.close()
            self.socket = None