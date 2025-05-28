"""
StatusResponder module for sending status messages over TCP connections.
This module provides functionality to send fixed-length status messages
to clients connected via TCP sockets. Status messages are encoded as UTF-8
and padded or truncated to exactly 16 bytes before transmission.
Classes:
    StatusResponder: Utility class for sending status messages.
example:
    ```
    from server.StatusResponder import StatusResponder
    from server.TCPSocketServer import Connection

    conn = Connection(address=('localhost', 12345))
    status = "Server is running"
    StatusResponder.send_status(conn, status)
"""

import logging
from .TCPSocketServer import Connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('StatusResponder')

class StatusResponder:

    @staticmethod
    def send_status(conn: Connection, status: str) -> bool:
        try:
            status_bytes = status.encode('utf-8')

            if len(status_bytes) > 16:
                # truncate to 16 bytes
                status_bytes = status_bytes[:16] 
            elif len(status_bytes) < 16:
                # pad with spaces
                status_bytes = status_bytes + b' ' * (16 - len(status_bytes))
            
            result = conn.send(status_bytes)

            if result:
                logger.info(f"Status sent to {conn.address}: {status}")
            else:
                logger.error(f"Failed to send status to {conn.address}")
            
            return result
        except Exception as e:
            logger.error(f"Error sending status: {e}")
            return False