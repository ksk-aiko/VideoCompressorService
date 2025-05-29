"""
StorageChecker class for managing and monitoring storage capacity.
This module provides functionality to check available storage space, 
track usage against a configured maximum, and determine if there's
enough capacity for new files.
Attributes:
    max_storage_bytes (int): Maximum storage capacity in bytes.
    storage_path (str): Path to the storage directory.
Example:
    >>> checker = StorageChecker(max_storage_tb=2.0, storage_path='/data')
    >>> if checker.has_capacity(file_size):
    >>>     # proceed with file operation
"""
import os
import logging
import shutil
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('StorageChecker')

class StorageChecker:
    def __init__(self, max_storage_tb: float = 4.0, storage_path: str = None):
        self.max_storage_bytes = max_storage_tb * 1024 * 1024 * 1024 * 1024
        self.storage_path = storage_path or os.getcwd()

        if not os.path.exists(self.storage_path):
            try:
                os.makedirs(self.storage_path)
                logger.info(f"Created storage directory at {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to create storage directory {self.storage_path}: {e}")
    
    def get_used_space(self) -> int:
        try:
            total_size = 0
            # Walk through the directory and sum up the sizes of all files
            for dirpath, _, filenames in os.walk(self.storage_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
        except Exception as e:
            logger.error(f"Error calculating used space in {self.storage_path}: {e}")
            return 0
    
    def get_free_space(self) -> int:
        return self.max_storage_bytes - self.get_used_space()
    
    def has_capacity(self, file_size: int) -> bool:
        free_space = self.get_free_space()
        has_space = free_space >= file_size
        if not has_space:
            logger.warning(f"Not enough storage space. Required: {file_size} bytes, Available: {free_space} bytes")
        
        return has_space
    
    def get_system_free_space(self) -> Optional[int]:
        try:
            disk_usage = shutil.disk_usage(self.storage_path)
            return disk_usage.free
        except Exception as e:
            logger.error(f"Error getting system free space for {self.storage_path}: {e}")
            return None