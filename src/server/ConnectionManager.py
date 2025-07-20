import threading
import logging

logger = logging.getLogger('ConnectionManager')

class ConnectionManager:
    def __init__(self):
        self._active_ips = set()
        self._lock = threading.Lock()
    
    def add_connection(self, ip_address: str) -> bool:
        with self._lock:
            if ip_address in self._active_ips:
                logger.warning(f"Connection attempt from an already active IP: {ip_address}")
                return False
            self._active_ips.add(ip_address)
            logger.info(f"Added new connection for IP: {ip_address}.Active connections: {len(self._active_ips)}")
            return True
    
    def remove_connection(self, ip_address: str):
        with self._lock:
            self._active_ips.discard(ip_address)
            logger.info(f"Removed connection for IP: {ip_address}. Active connections: {len(self._active_ips)}")