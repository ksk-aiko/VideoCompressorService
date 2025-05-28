"""
A class that handles writing files to disk.
This class manages file storage operations in a specified directory, 
handling directory creation and preventing filename collisions.
Attributes:
    storage_dir (str): Directory path where files will be stored. 
                      Defaults to "uploads".
Example:
    ```
    writer = DiskWriter(storage_dir="my_uploads")
    file_path = writer.write_to_disk(file_data, "example.mp4")
    if file_path:
        print(f"File saved to {file_path}")
    ```
"""

import os
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DiskWriter')

class DiskWriter:

    def __init__(self, storage_dir: str = "uploads"):
        self.storage_dir = storage_dir

        if not os.path.exists(self.storage_dir):
            try:
                os.makedirs(self.storage_dir)
                logger.info(f"Created storage directory: {self.storage_dir}")
            except Exception as e:
                logger.error(f"Failed to create storage directory: {e}")
    
    def write_to_disk(self, file_data: bytes, filename: str) -> Optional[str]:
        try:
            # Extract base name and extension
            base_name, ext = os.path.splitext(filename) 
            file_path = os.path.join(self.storage_dir, filename)
            # To handle duplicate filenames
            counter = 1 

            while os.path.exists(file_path):
                new_filename = f"{base_name}_{counter}{ext}"
                file_path = os.path.join(self.storage_dir, new_filename)
                counter += 1
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Successfully wrote file to disk: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to write file to disk: {e}")
            return None


            